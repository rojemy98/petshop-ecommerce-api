from pathlib import Path

from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa


BASE_DIR = Path(__file__).resolve().parent.parent
KEYS_DIR = BASE_DIR / "keys"

KEYS_DIR.mkdir(exist_ok=True)


private_key = rsa.generate_private_key(
    public_exponent=65537,
    key_size=2048
)


private_pem = private_key.private_bytes(
    encoding=serialization.Encoding.PEM,
    format=serialization.PrivateFormat.PKCS8,
    encryption_algorithm=serialization.NoEncryption()
)


public_key = private_key.public_key()

public_pem = public_key.public_bytes(
    encoding=serialization.Encoding.PEM,
    format=serialization.PublicFormat.SubjectPublicKeyInfo
)


(KEYS_DIR / "private.pem").write_bytes(private_pem)
(KEYS_DIR / "public.pem").write_bytes(public_pem)


print("RSA keys generated successfully.")
print(f"Private key: {KEYS_DIR / 'private.pem'}")
print(f"Public key: {KEYS_DIR / 'public.pem'}")