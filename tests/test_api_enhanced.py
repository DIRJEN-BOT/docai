"""Enhanced API tests — password parameter, /verify-income, API key auth."""

from __future__ import annotations

from pathlib import Path
from unittest.mock import MagicMock, patch

from fastapi.testclient import TestClient

from docai.api import app, API_KEYS

FIXTURES_DIR = Path(__file__).parent / "fixtures"
NATIVE_PATH = FIXTURES_DIR / "bca_native.pdf"
HAPPY_PATH = FIXTURES_DIR / "bca_happy_path.pdf"

API_KEY = list(API_KEYS.keys())[0]
client = TestClient(app)


# ---------------------------------------------------------------------------
# API key authentication
# ---------------------------------------------------------------------------

class TestAPIKeyAuth:
    def test_health_exempt_from_auth(self):
        """GET /health works without an API key."""
        resp = client.get("/health")
        assert resp.status_code == 200
        assert resp.json()["status"] == "ok"

    def test_landing_exempt_from_auth(self):
        """GET / works without an API key."""
        resp = client.get("/")
        assert resp.status_code == 200

    def test_parse_requires_api_key(self):
        """POST /parse without X-API-Key returns 401."""
        with open(NATIVE_PATH, "rb") as f:
            resp = client.post(
                "/parse",
                files={"file": ("bca_native.pdf", f, "application/pdf")},
            )
        assert resp.status_code == 401
        body = resp.json()
        assert body["error"] == "unauthorized"

    def test_parse_rejects_invalid_api_key(self):
        """POST /parse with wrong key returns 401."""
        with open(NATIVE_PATH, "rb") as f:
            resp = client.post(
                "/parse",
                files={"file": ("bca_native.pdf", f, "application/pdf")},
                headers={"X-API-Key": "invalid-key-00000"},
            )
        assert resp.status_code == 401

    def test_parse_accepts_valid_api_key(self):
        """POST /parse with valid key succeeds."""
        with open(NATIVE_PATH, "rb") as f:
            resp = client.post(
                "/parse",
                files={"file": ("bca_native.pdf", f, "application/pdf")},
                headers={"X-API-Key": API_KEY},
            )
        assert resp.status_code == 200
        assert resp.json()["bank"] == "bca"

    def test_verify_income_requires_api_key(self):
        """POST /verify-income without X-API-Key returns 401."""
        with open(NATIVE_PATH, "rb") as f:
            resp = client.post(
                "/verify-income",
                files={"file": ("bca_native.pdf", f, "application/pdf")},
            )
        assert resp.status_code == 401

    def test_verify_income_accepts_valid_api_key(self):
        """POST /verify-income with valid key succeeds."""
        with open(NATIVE_PATH, "rb") as f:
            resp = client.post(
                "/verify-income",
                files={"file": ("bca_native.pdf", f, "application/pdf")},
                headers={"X-API-Key": API_KEY},
            )
        assert resp.status_code == 200


# ---------------------------------------------------------------------------
# Password parameter on /parse
# ---------------------------------------------------------------------------

class TestParsePassword:
    def test_parse_without_password_unchanged(self):
        """Normal parse without password works as before."""
        with open(NATIVE_PATH, "rb") as f:
            resp = client.post(
                "/parse",
                files={"file": ("bca_native.pdf", f, "application/pdf")},
                headers={"X-API-Key": API_KEY},
            )
        assert resp.status_code == 200
        assert resp.json()["bank"] == "bca"

    def test_parse_with_password_none_unchanged(self):
        """Passing password=None behaves like no password."""
        with open(NATIVE_PATH, "rb") as f:
            resp = client.post(
                "/parse",
                files={"file": ("bca_native.pdf", f, "application/pdf")},
                data={"password": ""},
                headers={"X-API-Key": API_KEY},
            )
        assert resp.status_code == 200

    def test_parse_with_wrong_password_on_unencrypted_returns_200(self):
        """Sending a password for a non-encrypted PDF is harmless (no-op)."""
        with open(NATIVE_PATH, "rb") as f:
            resp = client.post(
                "/parse",
                files={"file": ("bca_native.pdf", f, "application/pdf")},
                data={"password": "12345678"},
                headers={"X-API-Key": API_KEY},
            )
        # The file is NOT encrypted, so password is ignored and parse succeeds.
        assert resp.status_code == 200
        assert resp.json()["bank"] == "bca"

    @patch("docai.api._decrypt_pdf")
    def test_parse_with_password_retries_on_protected(self, mock_decrypt):
        """When PasswordProtectedError is raised and password is provided, decrypt is attempted."""
        import shutil
        import tempfile

        from docai.base import PasswordProtectedError

        call_count = 0

        def side_effect(pdf_path):
            """First call raises, second call (after decrypt) succeeds."""
            nonlocal call_count
            call_count += 1
            if call_count == 1:
                raise PasswordProtectedError("PDF is password-protected")
            # After decrypt, parse the decrypted file normally
            from docai.parsers.registry import get_parser
            parser = get_parser("bca")
            return parser.parse(pdf_path)

        # Create a temp copy so unlinking doesn't fail on Windows
        tmp_copy = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf")
        shutil.copy2(NATIVE_PATH, tmp_copy.name)
        tmp_copy.close()
        mock_decrypt.return_value = tmp_copy.name

        try:
            with patch("docai.api.get_parser") as mock_get_parser:
                mock_parser = MagicMock()
                mock_parser.parse.side_effect = side_effect
                mock_get_parser.return_value = mock_parser

                with open(NATIVE_PATH, "rb") as f:
                    resp = client.post(
                        "/parse",
                        files={"file": ("bca_native.pdf", f, "application/pdf")},
                        data={"password": "12345678"},
                        headers={"X-API-Key": API_KEY},
                    )

                # Decrypt should have been called once
                mock_decrypt.assert_called_once()
                # Parse should have been called twice (first fail, then retry)
                assert mock_parser.parse.call_count == 2
        finally:
            try:
                Path(tmp_copy.name).unlink(missing_ok=True)
            except OSError:
                pass


# ---------------------------------------------------------------------------
# /verify-income endpoint
# ---------------------------------------------------------------------------

class TestVerifyIncome:
    def test_verify_income_returns_structured_report(self):
        """POST /verify-income returns expected report structure."""
        with open(NATIVE_PATH, "rb") as f:
            resp = client.post(
                "/verify-income",
                files={"file": ("bca_native.pdf", f, "application/pdf")},
                headers={"X-API-Key": API_KEY},
            )
        assert resp.status_code == 200, resp.text
        body = resp.json()

        # Required top-level keys
        assert "verification_score" in body
        assert "confidence" in body
        assert "detected_monthly_income" in body
        assert "income_source" in body
        assert "salary_months_detected" in body
        assert "monthly_incomes" in body
        assert "consistency_score" in body
        assert "income_cv" in body
        assert "has_gaps" in body
        assert "gap_months" in body
        assert "fraud_flags" in body
        assert "balance_valid" in body
        assert "has_suspicious_patterns" in body
        assert "statement_period" in body
        assert "total_months_covered" in body
        assert "total_transactions" in body
        assert "total_credit" in body
        assert "total_debit" in body
        assert "bank" in body
        assert "account_number" in body

    def test_verify_income_sets_balance_valid_from_validation(self):
        """balance_valid reflects whether the statement passed balance check."""
        with open(NATIVE_PATH, "rb") as f:
            resp = client.post(
                "/verify-income",
                files={"file": ("bca_native.pdf", f, "application/pdf")},
                headers={"X-API-Key": API_KEY},
            )
        body = resp.json()
        # The native fixture should pass balance validation
        assert body["balance_valid"] is True

    def test_verify_income_rejects_missing_file(self):
        resp = client.post(
            "/verify-income",
            headers={"X-API-Key": API_KEY},
        )
        assert resp.status_code == 422

    def test_verify_income_bank_field(self):
        with open(NATIVE_PATH, "rb") as f:
            resp = client.post(
                "/verify-income",
                files={"file": ("bca_native.pdf", f, "application/pdf")},
                headers={"X-API-Key": API_KEY},
            )
        assert resp.json()["bank"] == "bca"
