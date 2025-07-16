from typing import Any
from unittest.mock import patch


class StripeCustomer:
    def __init__(self, id: str = "cus_123") -> None:
        self.id = id


class StripeMock:
    def __init__(self) -> None:
        self.create_calls: list = []
        self.modify_calls: list = []

    def customer_create(self, **kwargs: Any) -> StripeCustomer:
        self.create_calls.append(kwargs)
        return StripeCustomer()

    def customer_modify(self, id: str, **kwargs: Any) -> None:
        self.modify_calls.append((id, kwargs))
        return None


def enable_stripe_mock(self: Any) -> None:
    self.stripe_mock = StripeMock()
    patcher_create = patch(
        "customer.models.stripe.Customer.create", self.stripe_mock.customer_create
    )
    patcher_modify = patch(
        "customer.models.stripe.Customer.modify", self.stripe_mock.customer_modify
    )
    self.addCleanup(patcher_create.stop)
    self.addCleanup(patcher_modify.stop)
    patcher_create.start()
    patcher_modify.start()
