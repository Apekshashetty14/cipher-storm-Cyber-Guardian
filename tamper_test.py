with open("secret.txt.locked", "rb") as f:
    data = f.read()

data = data[:20] + b"XXXX" + data[24:]

with open("secret.txt.locked", "wb") as f:
    f.write(data)

print("File tampered")