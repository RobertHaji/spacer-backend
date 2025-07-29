from flask_restful import Resource

from resources.mpesa import Mpesa
from models import Payment, db


class PaymentResource(Resource):
    def post(self):
        mpesa_instance = Mpesa()

        data = {"phone": "254757397083", "amount": "1", "description": "Space payment"}

        mpesa_response = mpesa_instance.make_stk_push(data)

        # payment_data = Payment(checkout_id=mpesa_response["CheckoutRequestID"])

        # db.session.add(payment_data)
        # db.session.commit ()

        return {"message": "Ok", "data": mpesa_response}
