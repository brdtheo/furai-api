import os

import stripe
from django.shortcuts import get_object_or_404
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.status import HTTP_200_OK
from rest_framework.views import APIView
from stripe import PaymentIntent

from booking.enums import BookingStatus
from booking.models import Booking

stripe.api_key = os.getenv("STRIPE_API_KEY")

endpoint_secret = os.getenv("STRIPE_ENDPOINT_SECRET")


class WebhookView(APIView):
    """
    Receive events from Stripe API
    """

    def post(self, request: Request) -> Response:
        event = None
        payload = request.body.decode("utf-8")
        sig_header = request.headers["STRIPE_SIGNATURE"]

        try:
            event = stripe.Webhook.construct_event(payload, sig_header, endpoint_secret)
        except ValueError as error:
            # Invalid payload
            raise error
        except stripe.SignatureVerificationError as error:
            # Invalid signature
            raise error

        if event["type"] == "payment_intent.succeeded":
            payment_intent: PaymentIntent = event["data"]["object"]
            if payment_intent.metadata.get("booking_id"):
                booking = get_object_or_404(
                    Booking, pk=payment_intent.metadata["booking_id"]
                )
                booking.status = BookingStatus.ACTIVE
                booking.save()
                booking.send_confirmation_email()
        if event["type"] == "payment_intent.canceled":
            booking_id: str = event["data"]["object"].metadata["booking_id"]
            booking = get_object_or_404(Booking, pk=booking_id)
            booking.delete()
        else:
            print("Unhandled event type {}".format(event["type"]))

        return Response(status=HTTP_200_OK)
