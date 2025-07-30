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


class PaymentCallbackResource(Resource):
    def get(self):
        return {"message": "Callback endpoint is registered successfully."}, 200

    def post(self):
        try:
            # Step 1: Receive JSON data from M-Pesa
            data = request.get_json()
            print("Callback received:", data)

            # Step 2: Extract relevant parts of the response
            stk_callback = data.get("Body", {}).get("stkCallback", {})
            checkout_id = stk_callback.get("CheckoutRequestID")
            result_code = stk_callback.get("ResultCode")

            # Step 3: Proceed only if payment was successful
            if result_code == 0:
                # Step 4: Extract payment metadata from callback
                metadata = stk_callback.get("CallbackMetadata", {}).get("Item", [])
                mpesa_code = next(
                    (
                        item["Value"]
                        for item in metadata
                        if item["Name"] == "MpesaReceiptNumber"
                    ),
                    None,
                )
                amount = next(
                    (item["Value"] for item in metadata if item["Name"] == "Amount"),
                    None,
                )
                phone = next(
                    (
                        item["Value"]
                        for item in metadata
                        if item["Name"] == "PhoneNumber"
                    ),
                    None,
                )

                # Step 5: Find the payment using the checkout ID
                payment = Payment.query.filter_by(checkout_id=checkout_id).one_or_none()

                if not payment:
                    return {"message": "Payment record not found"}, 404

                # Step 6: Update the payment record
                payment.payment_status = "paid"
                payment.mpesa_code = mpesa_code
                payment.amount = amount
                payment.paying_phone = str(phone)
                db.session.commit()

                return {"message": "Payment updated successfully"}, 200

            else:
                # Payment failed or was canceled
                return {
                    "message": "Payment not successful",
                    "status_code": result_code,
                }, 400

        except Exception as e:
            return {"message": "Callback processing error", "error": str(e)}, 500

class PaymentStatusResource(Resource):
    def get(self, checkout_id):
        # Find payment with this checkout_id
        payment = Payment.query.filter_by(checkout_id=checkout_id).first()

        if not payment:
            return {"error": "Payment not found"}, 404

        return {
            "payment_status": payment.payment_status,
            "mpesa_code": payment.mpesa_code,
            "amount": float(payment.amount),
            "paying_phone": payment.paying_phone,
        }, 200
