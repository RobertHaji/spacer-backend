# from flask_restful import Resource
# from flask import request
# import uuid

# from resources.mpesa import Mpesa
# from models import Payment, db


# class PaymentResource(Resource):
#     def post(self):
#         data = request.get_json()

#         if not data:
#             return {"message": "Missing JSON payload"}, 400

#         # 2. Extract fields safely
#         paying_phone = data.get("paying_phone")
#         amount = data.get("amount")
#         description = data.get("description")
#         temp_code = f"TEMP-{uuid.uuid4().hex[:8].upper()}"[:10]

#         # 3. Simple validation
#         if not paying_phone or not amount or not description:
#             return {
#                 "message": "Missing one or more required fields: paying_phone, amount, description"
#             }, 400

#         # 4. Format paying_phone number if needed (ensure starts with '254' and is numeric)
#         if paying_phone.startswith("0"):
#             paying_phone = "254" + paying_phone[1:]

#         # 5. Create Mpesa instance and initiate STK Push
#         mpesa_instance = Mpesa()

#         mpesa_response = mpesa_instance.make_stk_push(
#             {
#                 "paying_phone": paying_phone,
#                 "amount": amount,
#                 "description": description,
#                 "mpesa_code": temp_code,
#             }
#         )

#         # 6. Save checkout ID if request was successful
#         checkout_id = mpesa_response.get("CheckoutRequestID")

#         if checkout_id:
#             try:
#                 payment_data = Payment(
#                     amount=amount,
#                     paying_phone=paying_phone,
#                     mpesa_code=temp_code,
#                     checkout_id=checkout_id,
#                     payment_mode="mpesa",
#                     payment_status="pending",
#                 )
#                 db.session.add(payment_data)
#                 db.session.commit()
#             except Exception as e:
#                 db.session.rollback()
#                 return {"message": "Error saving payment", "error": str(e)}, 500

#         return {"message": "STK Push initiated", "data": mpesa_response}, 200


# class PaymentCallbackResource(Resource):
#     def get(self):
#         return {"message": "Callback endpoint is registered successfully."}, 200

#     def post(self):
#         try:
#             # Step 1: Receive JSON data from M-Pesa
#             data = request.get_json()
#             print("Callback received:", data)

#             # Step 2: Extract relevant parts of the response
#             stk_callback = data.get("Body", {}).get("stkCallback", {})
#             checkout_id = stk_callback.get("CheckoutRequestID")
#             result_code = stk_callback.get("ResultCode")

#             # Step 3: Proceed only if payment was successful
#             if result_code == 0:
#                 # Step 4: Extract payment metadata from callback
#                 metadata = stk_callback.get("CallbackMetadata", {}).get("Item", [])
#                 mpesa_code = next(
#                     (
#                         item["Value"]
#                         for item in metadata
#                         if item["Name"] == "MpesaReceiptNumber"
#                     ),
#                     None,
#                 )
#                 amount = next(
#                     (item["Value"] for item in metadata if item["Name"] == "Amount"),
#                     None,
#                 )
#                 phone = next(
#                     (
#                         item["Value"]
#                         for item in metadata
#                         if item["Name"] == "PhoneNumber"
#                     ),
#                     None,
#                 )

#                 # Step 5: Find the payment using the checkout ID
#                 payment = Payment.query.filter_by(checkout_id=checkout_id).one_or_none()

#                 if not payment:
#                     return {"message": "Payment record not found"}, 404

#                 # Step 6: Update the payment record
#                 payment.payment_status = "paid"
#                 payment.mpesa_code = mpesa_code
#                 payment.amount = amount
#                 payment.paying_phone = str(phone)
#                 db.session.commit()

#                 return {"message": "Payment updated successfully"}, 200

#             else:
#                 # Payment failed or was canceled
#                 return {
#                     "message": "Payment not successful",
#                     "status_code": result_code,
#                 }, 400

#         except Exception as e:
#             return {"message": "Callback processing error", "error": str(e)}, 500

# class PaymentStatusResource(Resource):
#     def get(self, checkout_id):
#         # Find payment with this checkout_id
#         payment = Payment.query.filter_by(checkout_id=checkout_id).first()

#         if not payment:
#             return {"error": "Payment not found"}, 404

#         return {
#             "payment_status": payment.payment_status,
#             "mpesa_code": payment.mpesa_code,
#             "amount": float(payment.amount),
#             "paying_phone": payment.paying_phone,
#         }, 200
from flask_restful import Resource, reqparse
from flask import request, jsonify
from models import db, Payment, Booking  
import uuid
import logging


# Payment resource to initiate STK push
class PaymentResource(Resource):
    def post(self, booking_id):
        parser = reqparse.RequestParser()
        parser.add_argument(
            "amount", type=float, required=True, help="Amount is required"
        )
        parser.add_argument(
            "phone_number", type=str, required=True, help="Phone number is required"
        )
        parser.add_argument(
            "user_id", type=int, required=True, help="User ID is required"
        )
        parser.add_argument(
            "space_id", type=int, required=True, help="Space ID is required"
        )
        parser.add_argument("number_of_guests", type=int)
        parser.add_argument("date_of_booking", type=str)
        parser.add_argument("number_of_hours", type=int)
        data = parser.parse_args()

        phone_number = data["phone_number"]
        amount = data["amount"]

        try:
            #  Initiate STK push
            response = Mpesa.stk_push(phone_number, amount)

            if response.get("ResponseCode") == "0":
                checkout_request_id = response["CheckoutRequestID"]

                mpesa_code = f"TEMP-{uuid.uuid4().hex[:8]}"

                payment = Payment(
                    booking_id=booking_id,
                    user_id=data["user_id"],
                    space_id=data["space_id"],
                    amount=amount,
                    mpesa_code=mpesa_code,
                    status="pending",
                    checkout_id=checkout_request_id,
                    metadata={
                        "number_of_guests": data.get("number_of_guests"),
                        "date_of_booking": data.get("date_of_booking"),
                        "number_of_hours": data.get("number_of_hours"),
                    },
                )

                db.session.add(payment)
                db.session.commit()

                return jsonify(
                    {
                        "message": "STK push initiated",
                        "checkout_request_id": checkout_request_id,
                        "payment_id": payment.id,
                    }
                )
            else:
                return jsonify(
                    {"error": "Failed to initiate STK push", "details": response}
                )

        except Exception as e:
            logging.error(f"Payment initiation error: {str(e)}")
            return jsonify({"error": "Internal server error", "details": str(e)}), 500

class PaymentCallbackResource(Resource):
    def post(self):
        try:
            data = request.get_json()
            logging.info(f"Callback data received: {data}")

            body = data.get("Body", {})
            stk_callback = body.get("stkCallback", {})
            result_code = stk_callback.get("ResultCode")
            checkout_request_id = stk_callback.get("CheckoutRequestID")

            payment = Payment.query.filter_by(checkout_id=checkout_request_id).first()

            if not payment:
                return jsonify({"error": "Payment not found"}), 404

            if result_code == 0:
                callback_metadata = stk_callback.get("CallbackMetadata", {}).get(
                    "Item", []
                )
                mpesa_code = None
                for item in callback_metadata:
                    if item.get("Name") == "MpesaReceiptNumber":
                        mpesa_code = item.get("Value")

                payment.status = "paid"
                payment.mpesa_code = mpesa_code or payment.mpesa_code

                booking = Booking(
                    user_id=payment.user_id,
                    space_id=payment.space_id,
                    number_of_guests=payment.metadata.get("number_of_guests"),
                    date_of_booking=payment.metadata.get("date_of_booking"),
                    number_of_hours=payment.metadata.get("number_of_hours"),
                    total_amount=payment.amount,
                    status="confirmed",
                )

                db.session.add(booking)

            else:
                payment.status = "failed"

            db.session.commit()
            return jsonify({"message": "Callback processed successfully"})

        except Exception as e:
            logging.error(f"Callback processing error: {str(e)}")
            return jsonify({"error": "Internal server error", "details": str(e)}), 500

class PaymentStatusResource(Resource):
    def get(self, payment_id):
        payment = Payment.query.get(payment_id)
        if not payment:
            return jsonify({"error": "Payment not found"}), 404

        return jsonify(
            {
                "id": payment.id,
                "amount": payment.amount,
                "status": payment.status,
                "mpesa_code": payment.mpesa_code,
            }
        )
