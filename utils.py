from cryptography.hazmat.primitives import serialization,hashes
from cryptography.hazmat.primitives.asymmetric import rsa,padding
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.asymmetric import rsa
import base64
import os
import binascii
import hashlib

import base64
from stegano import lsb

def embed_signature(base64_signature, file_path,output_path):
    # Decode the base64 signature to bytes
    signature_bytes = base64.b64decode(base64_signature)

    # Convert the signature bytes to a bit string
    signature_bit_string = "".join(format(byte, "08b") for byte in signature_bytes)

    stego_image = lsb.hide(file_path, signature_bit_string)

    # Save the stego image
    stego_image.save(output_path)

    print(f"Signature embedded successfully and saved as {output_path}")

def embed_string(str, file_path,output_path):
   
    stego_image = lsb.hide(file_path, str)

    # Save the stego image
    stego_image.save(output_path)

    print(f"String embedded successfully and saved as {str}")


def generate_keys():
    private_key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=2048
    )
    public_key = private_key.public_key()

    return (
        public_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        ).decode('utf-8'),
        private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.NoEncryption()
        ).decode('utf-8')
    )

from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import serialization

def generate_signature(private_key_pem_str, file_path):
    # Convert the private key string to bytes
    private_key_pem_bytes = private_key_pem_str.encode("utf-8")

    # Load the private key from the PKCS#8 PEM encoded string
    private_key = serialization.load_pem_private_key(
        private_key_pem_bytes,
        password=None
    )

    data=""
    with open(file_path, "rb") as file:
        data = file.read()


    # Generate the signature
    signature = private_key.sign(
        data,
        padding.PSS(
            mgf=padding.MGF1(hashes.SHA256()),
            salt_length=padding.PSS.MAX_LENGTH
        ),
        hashes.SHA256()
    )

    signature_str = base64.b64encode(signature).decode("utf-8")

    return signature_str
