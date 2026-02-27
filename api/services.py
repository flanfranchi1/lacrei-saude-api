import uuid


class AsaasService:
    @staticmethod
    def generate_mock_billing(appointment_id, value=150.00):
        fake_payment_id = f"pay_{uuid.uuid4().hex[:12]}"
        fake_url = f"https://sandbox.asaas.com/c/{fake_payment_id}"

        return {"payment_id": fake_payment_id, "payment_url": fake_url, "value": value, "status": "PENDING"}
