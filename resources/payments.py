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
        paying_phone = data.get("paying_phone")
        amount = data.get("amount")
        description = data.get("description")
        mpesa_code = data.get("mpesa_code")
        booking_id = data.get("booking_id")

        # 3. Simple validation
        if not paying_phone or not amount or not description:
            return {
                "message": "Missing one or more required fields: paying_phone, amount, description"
            }, 400

        # 4. Format paying_phone number if needed (ensure starts with '254' and is numeric)
        if paying_phone.startswith("0"):
            paying_phone = "254" + paying_phone[1:]

        # 5. Create Mpesa instance and initiate STK Push
        mpesa_instance = Mpesa()

        mpesa_response = mpesa_instance.make_stk_push(
            {
                "paying_phone": paying_phone,
                "amount": amount,
                "description": description,
                "mpesa_code": mpesa_code,
            }
        )

        # 6. Save checkout ID if request was successful
        checkout_id = mpesa_response.get("CheckoutRequestID")

        if checkout_id:
            try:
                payment_data = Payment(
                    booking_id=booking_id,
                    amount=amount,
                    paying_phone=paying_phone,
                    mpesa_code=mpesa_code,
                    checkout_id=checkout_id,
                    payment_mode="mpesa",
                    payment_status="pending",
                )
                db.session.add(payment_data)
                db.session.commit()
            except Exception as e:
                db.session.rollback()
                return {"message": "Error saving payment", "error": str(e)}, 500

        return {"message": "STK Push initiated", "data": mpesa_response}, 200
