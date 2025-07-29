from flask_restful import Resource
from flask import request

from resources.mpesa import Mpesa
from models import Payment, db


class PaymentResource(Resource):
    def post(self):
        data = request.get_json()

        if not data:
            return {"message": "Missing JSON payload"}, 400

        # 2. Extract fields safely
        phone = data.get("phone")
        amount = data.get("amount")
        description = data.get("description")

        # 3. Simple validation
        if not phone or not amount or not description:
            return {
                "message": "Missing one or more required fields: phone, amount, description"
            }, 400

        # 4. Format phone number if needed (ensure starts with '254' and is numeric)
        if phone.startswith("0"):
            phone = "254" + phone[1:]

        # 5. Create Mpesa instance and initiate STK Push
        mpesa_instance = Mpesa()

        mpesa_response = mpesa_instance.make_stk_push(
            {"phone": phone, "amount": amount, "description": description}
        )

        # 6. Save checkout ID if request was successful
        checkout_id = mpesa_response.get("CheckoutRequestID")

        if checkout_id:
            payment_data = Payment(checkout_id=checkout_id)
            db.session.add(payment_data)
            db.session.commit()

        return {"message": "Ok", "data": mpesa_response}
