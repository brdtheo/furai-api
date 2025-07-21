# conftest.py
"""
pytest configuration file
"""

from unittest.mock import patch

import pytest
import resend

from furai.tests.mocks import StripeMock


@pytest.fixture(autouse=True)
def stub_resend_send(monkeypatch):
    """Prevent sending emails"""

    def send(params):
        pass

    # Remove Resend API key from env
    monkeypatch.setenv("RESEND_API_KEY", "")
    # Mock Resend SDK send method
    monkeypatch.setattr(resend.Emails, "send", send)
    yield


@pytest.fixture
def stripe_mocks():
    """Mock stripe customer methods"""

    stripe_mock = StripeMock()
    with (
        patch("customer.services.stripe.Customer.create", stripe_mock.customer_create),
        patch("customer.services.stripe.Customer.modify", stripe_mock.customer_modify),
    ):
        yield stripe_mock
