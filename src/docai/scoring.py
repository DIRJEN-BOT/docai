"""Income verification scoring engine.

Analyses a ParseResult to produce a structured IncomeReport covering:
- Salary / recurring income detection
- Monthly income consistency
- Fraud / anomaly signals
- Composite verification score (0-100)
"""

from __future__ import annotations

import re
import statistics
from collections import defaultdict
from dataclasses import dataclass, field
from datetime import datetime
from decimal import Decimal, ROUND_HALF_UP
from typing import List, Optional, Tuple

from docai.models import ParseResult, Transaction
from docai.utils import clean_text


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

_SALARY_KEYWORDS = re.compile(
    r"\b(gaji|salary|payroll|upah|wages|thp|take\s*home)\b", re.IGNORECASE
)

_ROUND_MULTIPLE = Decimal("100000")  # IDR 100k round-number threshold


def _parse_date(date_str: str) -> Optional[datetime]:
    """Best-effort parse of DD/MM/YYYY or DD/MM/YY date strings."""
    date_str = date_str.strip()
    for fmt in ("%d/%m/%Y", "%d/%m/%y"):
        try:
            return datetime.strptime(date_str, fmt)
        except ValueError:
            continue
    return None


def _month_key(dt: datetime) -> str:
    """Return 'YYYY-MM' string."""
    return dt.strftime("%Y-%m")


def _is_salary_description(desc: str) -> bool:
    """Check if a transaction description contains salary keywords."""
    return bool(_SALARY_KEYWORDS.search(clean_text(desc)))


def _is_round_number(amount: Decimal) -> bool:
    """True if amount is a clean multiple of IDR 100,000."""
    if amount <= 0:
        return False
    return (amount % _ROUND_MULTIPLE) == 0


# ---------------------------------------------------------------------------
# Data models
# ---------------------------------------------------------------------------

@dataclass
class IncomeReport:
    """Structured income verification report."""

    # Overall
    verification_score: int  # 0-100 composite score
    confidence: str  # "high" | "medium" | "low"

    # Income detection
    detected_monthly_income: Decimal  # best estimate of monthly income
    income_source: str  # "salary" | "mixed" | "freelance" | "business" | "undetected"
    salary_months_detected: int  # how many months of salary found
    monthly_incomes: List[dict] = field(default_factory=list)
    # [{month: "2025-01", amount: Decimal, source: str}]

    # Consistency
    consistency_score: int = 0  # 0-100, how stable is the income
    income_cv: float = 0.0  # coefficient of variation
    has_gaps: bool = False
    gap_months: List[str] = field(default_factory=list)

    # Fraud signals
    fraud_flags: List[str] = field(default_factory=list)
    balance_valid: bool = True
    has_suspicious_patterns: bool = False

    # Metadata
    statement_period: str = ""
    total_months_covered: int = 0
    total_transactions: int = 0
    total_credit: Decimal = Decimal("0")
    total_debit: Decimal = Decimal("0")


# ---------------------------------------------------------------------------
# Salary detection
# ---------------------------------------------------------------------------

def _detect_salary_transactions(
    result: ParseResult,
) -> Tuple[List[Transaction], bool]:
    """Return (salary_transactions, keyword_matched).

    A transaction is classified as salary if:
    1. Its description contains a salary keyword, OR
    2. A similar credit amount (±10%) appears in 3+ distinct calendar months.
    """
    credits_by_month: dict[str, list[tuple[Transaction, bool]]] = defaultdict(list)

    for t in result.transactions:
        if t.credit <= 0:
            continue
        dt = _parse_date(t.date)
        if dt is None:
            continue
        mk = _month_key(dt)
        keyword_hit = _is_salary_description(t.description)
        credits_by_month[mk].append((t, keyword_hit))

    keyword_matched = any(
        any(hit for _, hit in txns) for txns in credits_by_month.values()
    )

    # --- Pass 1: keyword-flagged transactions ---
    keyword_txns: list[Transaction] = []
    for txns in credits_by_month.values():
        for t, hit in txns:
            if hit:
                keyword_txns.append(t)

    # --- Pass 2: recurring amount detection (±10%) ---
    # Collect the largest credit per month for cross-month comparison.
    month_top: dict[str, Transaction] = {}
    for mk, txns in credits_by_month.items():
        if not txns:
            continue
        # Pick the largest credit that isn't tiny (<1% of the largest overall).
        best = max(txns, key=lambda x: x[0].credit)[0]
        month_top[mk] = best

    recurring_txns: list[Transaction] = []
    if len(month_top) >= 3:
        amounts = sorted(
            {t.credit for t in month_top.values()}, key=lambda a: a, reverse=True
        )
        for candidate_amount in amounts:
            matching_months: list[Transaction] = []
            for t in month_top.values():
                if candidate_amount == 0:
                    continue
                ratio = abs(t.credit - candidate_amount) / candidate_amount
                if ratio <= Decimal("0.10"):
                    matching_months.append(t)
            if len(matching_months) >= 3:
                recurring_txns = matching_months
                break

    # Merge keyword + recurring without duplicates.
    seen_ids = set(id(t) for t in keyword_txns)
    for t in recurring_txns:
        if id(t) not in seen_ids:
            keyword_txns.append(t)
            seen_ids.add(id(t))

    return keyword_txns, keyword_matched


def _group_credits_by_month(result: ParseResult) -> dict[str, Decimal]:
    """Return {YYYY-MM: total_credits} for all months in the statement."""
    by_month: dict[str, Decimal] = defaultdict(Decimal)
    for t in result.transactions:
        if t.credit <= 0:
            continue
        dt = _parse_date(t.date)
        if dt is None:
            continue
        by_month[_month_key(dt)] += t.credit
    return dict(by_month)


# ---------------------------------------------------------------------------
# Consistency scoring
# ---------------------------------------------------------------------------

def _score_consistency(
    monthly_incomes_map: dict[str, Decimal],
    all_months: list[str],
) -> Tuple[int, float, bool, list[str]]:
    """Score consistency from the full monthly-income map."""
    values = list(monthly_incomes_map.values())
    if not values:
        return 0, 0.0, True, all_months

    mean_val = sum(values, Decimal("0")) / Decimal(str(len(values)))
    if mean_val == 0:
        return 0, 0.0, True, all_months

    # CV using Decimal for precision, convert at end.
    if len(values) < 2:
        cv = 0.0
        score = 80
        gap_months = [m for m in all_months if monthly_incomes_map.get(m, Decimal("0")) == 0]
        has_gaps = len(gap_months) > 0
        return score, cv, has_gaps, gap_months

    variance = sum((v - mean_val) ** 2 for v in values) / Decimal(str(len(values)))
    stdev = variance.sqrt()
    cv = float(stdev / mean_val)

    if cv < 0.1:
        score = 100 - max(1, int(cv * 100))
        score = max(score, 90)
    elif cv < 0.2:
        score = 89 - int((cv - 0.1) * 190)
        score = max(score, 70)
    elif cv < 0.4:
        score = 69 - int((cv - 0.2) * 145)
        score = max(score, 40)
    else:
        score = max(0, 39 - int((cv - 0.4) * 50))

    gap_months = [m for m in all_months if monthly_incomes_map.get(m, Decimal("0")) == 0]
    has_gaps = len(gap_months) > 0

    return score, cv, has_gaps, gap_months


# ---------------------------------------------------------------------------
# Fraud signals
# ---------------------------------------------------------------------------

def _detect_fraud_signals(result: ParseResult, balance_valid: bool) -> list[str]:
    """Return a list of human-readable fraud/anomaly flags."""
    flags: list[str] = []

    # --- Balance validation ---
    if not balance_valid:
        flags.append("Balance mismatch: computed closing ≠ declared closing")

    # --- Round number detection ---
    non_zero = [t for t in result.transactions if t.debit > 0 or t.credit > 0]
    if non_zero:
        round_count = sum(
            1 for t in non_zero
            if _is_round_number(t.debit) or _is_round_number(t.credit)
        )
        ratio = round_count / len(non_zero)
        if ratio > 0.30:
            flags.append(
                f"Round-number concentration: {round_count}/{len(non_zero)} "
                f"transactions ({ratio:.0%}) are round multiples of IDR 100,000"
            )

    # --- Impossible velocity: >5 transactions in the same minute ---
    minute_buckets: dict[str, int] = defaultdict(int)
    for t in result.transactions:
        dt = _parse_date(t.date)
        if dt is None:
            continue
        # Use date as-is; we only have day-level precision, so we skip
        # minute-level velocity unless the description contains a timestamp.
        # For now, flag truly duplicated amounts+descriptions (see below).
    # Since statement dates are day-level only, impossible-velocity at the
    # minute granularity cannot be detected without time-of-day data.

    # --- Duplicate detection: same amount + same description ---
    seen: dict[tuple[str, str, str], int] = defaultdict(int)
    for t in result.transactions:
        key = (t.date, t.description.strip().upper(), str(t.debit or t.credit))
        seen[key] += 1
    for (date, desc, amt), count in seen.items():
        if count >= 2:
            flags.append(
                f"Duplicate transaction detected: {desc} "
                f"for IDR {amt} on {date} appears {count}×"
            )

    # --- Balance jumps without matching transactions ---
    # (Already covered by validation; we just note if balance_valid is False.)

    # --- High balance relative to income ---
    if result.closing_balance > 0 and result.total_credit > 0:
        avg_monthly_income = _estimate_avg_monthly_income(result)
        if avg_monthly_income > 0:
            months_of_balance = float(result.closing_balance / avg_monthly_income)
            if months_of_balance > 24:
                flags.append(
                    f"High balance relative to income: closing balance "
                    f"represents ~{months_of_balance:.0f} months of detected income"
                )

    return flags


def _estimate_avg_monthly_income(result: ParseResult) -> Decimal:
    """Quick average monthly income estimate for fraud heuristics."""
    by_month = _group_credits_by_month(result)
    if not by_month:
        return Decimal("0")
    total = sum(by_month.values(), Decimal("0"))
    return total / Decimal(str(len(by_month)))


# ---------------------------------------------------------------------------
# Date range helpers
# ---------------------------------------------------------------------------

def _statement_date_range(
    result: ParseResult,
) -> Tuple[Optional[datetime], Optional[datetime]]:
    """Return (earliest, latest) transaction dates."""
    dates = [_parse_date(t.date) for t in result.transactions]
    valid = [d for d in dates if d is not None]
    if not valid:
        return None, None
    return min(valid), max(valid)


def _all_month_keys(result: ParseResult) -> list[str]:
    """Return sorted list of all YYYY-MM keys spanned by the statement."""
    earliest, latest = _statement_date_range(result)
    if earliest is None or latest is None:
        return []

    months: list[str] = []
    cur = datetime(earliest.year, earliest.month, 1)
    end = datetime(latest.year, latest.month, 1)
    while cur <= end:
        months.append(_month_key(cur))
        # advance month
        if cur.month == 12:
            cur = datetime(cur.year + 1, 1, 1)
        else:
            cur = datetime(cur.year, cur.month + 1, 1)
    return months


def _format_period(earliest: Optional[datetime], latest: Optional[datetime]) -> str:
    """Human-readable period string like 'Jan 2025 - Jun 2025'."""
    if earliest is None or latest is None:
        return "N/A"
    months = [
        "Jan", "Feb", "Mar", "Apr", "May", "Jun",
        "Jul", "Aug", "Sep", "Oct", "Nov", "Dec",
    ]
    return f"{months[earliest.month - 1]} {earliest.year} - {months[latest.month - 1]} {latest.year}"


# ---------------------------------------------------------------------------
# Composite score
# ---------------------------------------------------------------------------

def _compute_composite(
    balance_valid: bool,
    income_source: str,
    consistency_score: int,
    fraud_flag_count: int,
) -> Tuple[int, str]:
    """Return (composite_score 0-100, confidence)."""
    # Balance: 25 pts
    pts_balance = 25 if balance_valid else 0

    # Income detected: 25 pts
    pts_income_map = {"salary": 25, "mixed": 15, "freelance": 10, "business": 15}
    pts_income = pts_income_map.get(income_source, 5)

    # Consistency: 30 pts (scaled)
    pts_consistency = int(consistency_score * 30 / 100)

    # No-fraud: 20 pts (lose 5 per flag, min 0)
    pts_fraud = max(0, 20 - fraud_flag_count * 5)

    total = pts_balance + pts_income + pts_consistency + pts_fraud
    total = max(0, min(100, total))

    if total >= 80:
        confidence = "high"
    elif total >= 50:
        confidence = "medium"
    else:
        confidence = "low"

    return total, confidence


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def analyze_income(result: ParseResult) -> IncomeReport:
    """Analyse a ParseResult and return a structured IncomeReport.

    This is the single public entry point for the scoring engine.
    """
    # --- Metadata ---
    earliest, latest = _statement_date_range(result)
    statement_period = _format_period(earliest, latest)
    all_months = _all_month_keys(result)

    # --- Balance validation ---
    balance_ok = True
    try:
        computed = result.computed_closing()
        if computed != result.closing_balance:
            balance_ok = False
    except Exception:
        balance_ok = False

    # --- Salary / income detection ---
    salary_txns, keyword_matched = _detect_salary_transactions(result)
    credits_by_month = _group_credits_by_month(result)

    # Determine salary amount: use the median of detected salary credits.
    salary_amounts = [t.credit for t in salary_txns]
    salary_months_set = {_parse_date(t.date) for t in salary_txns}
    salary_months_set.discard(None)
    salary_months_count = len(salary_months_set)  # type: ignore[arg-type]

    if salary_amounts:
        detected_income = Decimal(
            str(statistics.median(salary_amounts))
        ).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
    else:
        # Fallback: median of the largest credit per month.
        top_per_month = []
        for txns in credits_by_month.values():
            pass  # we rebuilt below
        monthly_totals = list(credits_by_month.values())
        if monthly_totals:
            detected_income = Decimal(
                str(statistics.median(monthly_totals))
            ).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
        else:
            detected_income = Decimal("0")

    # --- Income source classification ---
    if salary_months_count >= 3 and keyword_matched:
        income_source = "salary"
    elif salary_months_count >= 3:
        income_source = "mixed"
    elif salary_months_count >= 1:
        income_source = "mixed"
    elif credits_by_month:
        income_source = "freelance"
    else:
        income_source = "undetected"

    # --- Monthly incomes list ---
    monthly_incomes: list[dict] = []
    salary_month_keys = set()
    for t in salary_txns:
        dt = _parse_date(t.date)
        if dt:
            salary_month_keys.add(_month_key(dt))

    for mk in all_months:
        total = credits_by_month.get(mk, Decimal("0"))
        source = "salary" if mk in salary_month_keys else "other"
        monthly_incomes.append({"month": mk, "amount": total, "source": source})

    # --- Consistency ---
    income_values = {mk: credits_by_month.get(mk, Decimal("0")) for mk in all_months}
    cons_score, cv, has_gaps, gap_months = _score_consistency(income_values, all_months)

    # --- Fraud signals ---
    fraud_flags = _detect_fraud_signals(result, balance_ok)

    # --- Composite score ---
    composite, confidence = _compute_composite(
        balance_valid=balance_ok,
        income_source=income_source,
        consistency_score=cons_score,
        fraud_flag_count=len(fraud_flags),
    )

    return IncomeReport(
        verification_score=composite,
        confidence=confidence,
        detected_monthly_income=detected_income,
        income_source=income_source,
        salary_months_detected=salary_months_count,
        monthly_incomes=monthly_incomes,
        consistency_score=cons_score,
        income_cv=cv,
        has_gaps=has_gaps,
        gap_months=gap_months,
        fraud_flags=fraud_flags,
        balance_valid=balance_ok,
        has_suspicious_patterns=len(fraud_flags) > 0,
        statement_period=statement_period,
        total_months_covered=len(all_months),
        total_transactions=len(result.transactions),
        total_credit=result.total_credit,
        total_debit=result.total_debit,
    )
