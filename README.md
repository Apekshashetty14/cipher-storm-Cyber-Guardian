# 🔒 LockBox

A desktop vault that encrypts your files behind a master password — with tamper detection and a login lockout, built entirely in Python.

## Features

- **Master password setup** — created once on first launch (minimum 4 characters), stored as a secure hash, never in plain text.
- **File encryption** — lock any file into an encrypted `.locked` copy using your master password as the key.
- **File decryption** — restore a `.locked` file back to its original contents, only with the correct password.
- **Tamper detection** — each file's fingerprint is saved at encryption time; if it's changed later, LockBox flags it on unlock.
- **Login lockout** — three wrong passwords in a row triggers an alert and closes the app.
- **Access log** — every login, failure, and file action is timestamped and viewable from inside the app.

## How it works

1. **Open the app** — LockBox checks whether a master password already exists. First time, it asks you to create one; after that, it asks you to enter it.
2. **Unlock the vault** — your password is checked and turned into an encryption key. Get it right, and the main screen opens.
3. **Encrypt or decrypt files** — choose a file to lock, or a `.locked` file to restore. Every action is logged automatically.
4. **Review activity anytime** — open the access log from the main screen to see the full history of logins and file actions.

> After 3 failed password attempts, LockBox shows an alert — "Too many failed attempts. Access denied." — and closes itself. The attempt counter resets after any successful login.

## Project files

| File | Purpose |
|---|---|
| `lockbox.py` | Main app — login, vault UI, encryption, lockout |
| `master.hash` | Stored hash of the master password |
| `access_log.txt` | Timestamped log of logins and file actions |
| `*.locked` | Encrypted copy of a protected file |
| `*.hash` | Fingerprint used to detect tampering |
| `*.restored` | Decrypted output of a `.locked` file |

## Built with

- Python 3
- Tkinter — UI
- bcrypt — password hashing
- cryptography (Fernet) — file encryption
- PBKDF2-HMAC — key derivation
- SHA-256 — tamper fingerprint

## Running it

```bash
python lockbox.py
```

On first run, you'll be asked to create a master password. On later runs, enter it to unlock the vault.# cipher-storm-Cyber-Guardian
