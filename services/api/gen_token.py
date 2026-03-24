from jose import jwt
from datetime import datetime, timedelta
import uuid

secret = "super_secret_for_development_change_in_production"
algo = "HS256"

def create_token():
    payload = {
        "sub": "admin-user",
        "tenant_id": "f47ac10b-58cc-4372-a567-0e02b2c3d479",
        "modules": ["CORE", "A1", "F1", "O1", "P1"],
        "exp": datetime.utcnow() + timedelta(days=30)
    }
    token = jwt.encode(payload, secret, algorithm=algo)
    print(token)

if __name__ == "__main__":
    create_token()
