# conftest.py
import pytest
import resend


@pytest.fixture(autouse=True)
def stub_resend_send(monkeypatch):
    """Prevent sending emails in tests"""

    def fake_send(params):
        pass
    # Remove Resend API key from env
    monkeypatch.setenv("RESEND_API_KEY", "")
    # Mock Resend SDK send method
    monkeypatch.setattr(resend.Emails, "send", fake_send)
    yield
