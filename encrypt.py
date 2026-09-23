from cryptography.fernet import Fernet
key = Fernet.generate_key()
print(key)
with open("secret.key", "wb") as f:
    f.write(key)
    fernet = Fernet(key)
    with open("secret.txt", "rb") as f:
     original = f.read()
     encrypted = fernet.encrypt(original)
     print(encrypted)
     with open("secret.txt.encrypted", "wb") as f:
      f.write(encrypted)