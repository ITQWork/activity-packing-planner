from cryptography.fernet import Fernet
import os

def decrypt_spec():
    key_path = 'specifications/activity_packing_planner/challenge/crypto_key.txt'
    spec_path = 'specifications/activity_packing_planner/challenge/encrypted_spec.txt'

    with open(key_path, 'rb') as f:
        key = f.read().strip()

    with open(spec_path, 'rb') as f:
        encrypted_data = f.read().strip()

    f = Fernet(key)
    decrypted_message = f.decrypt(encrypted_data).decode()

    print(decrypted_message)

if __name__ == "__main__":
    decrypt_spec()
