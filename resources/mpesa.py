import os
import base64
import requests

from requests.auth import HTTPBasicAuth
from dotenv import load_dotenv
from datetime import datetime


load_dotenv()


class Mpesa:
    consumer_key = None
    consumer_secret = None
    business_short_code = "174379"
    timestamp = None

    def __init__(self):
        self.consumer_key = os.environ.get("CONSUMER_KEY")
        self.consumer_secret = os.environ.get("CONSUMER_SECRET")
        self.timestamp = datetime.now().strftime("%Y%m%d%H%M%S")

    def get_access_token(self):
        res = requests.get(
            "https://sandbox.safaricom.co.ke/oauth/v1/generate?grant_type=client_credentials",
            auth=HTTPBasicAuth(self.consumer_key, self.consumer_secret),
        )

        data = res.json()

        return data["access_token"]

    def generate_password(self):
        password_str = (
            self.business_short_code + os.environ.get("SAF_PASSKEY") + self.timestamp
        )

        return base64.b64encode(password_str.encode()).decode("utf-8")

    def make_stk_push(self, data):
        amount = data["amount"]
        paying_phone = data["paying_phone"]
        description = data["description"]

        body = {
            "BusinessShortCode": self.business_short_code,
            "Password": self.generate_password(),
            "Timestamp": self.timestamp,
            "TransactionType": "CustomerPayBillOnline",
            "Amount": amount,
            "PartyA": paying_phone,
            "PartyB": self.business_short_code,
            "PhoneNumber": paying_phone,
            "CallBackURL": "https://mydomain.com/pat",
            "AccountReference": "Spacer",
            "TransactionDesc": description,
        }

        token = self.get_access_token()

        response = requests.post(
            "https://sandbox.safaricom.co.ke/mpesa/stkpush/v1/processrequest",
            json=body,
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {token}",
            },
        )

        response_data = response.json()

        return response_data
