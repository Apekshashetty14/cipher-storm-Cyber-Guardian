import tkinter as tk
from tkinter import filedialog, messagebox
import bcrypt
import hashlib
import os
from datetime import datetime
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import base64

PASSWORD_FILE = "master.hash"
LOG_FILE = "access_log.txt"
SALT = b"lockbox_salt_fixed_demo"

def log(message):
    with open(LOG_FILE, "a") as f:
        f.write(datetime.now().strftime("%Y-%m-%d %H:%M:%S") + " - " + message + "\n")

def get_key(password):
    kdf = PBKDF2HMAC(algorithm=hashes.SHA256(), length=32, salt=SALT, iterations=100000)
    return base64.urlsafe_b64encode(kdf.derive(password.encode()))

def setup_password(password):
    hashed = bcrypt.hashpw(password.encode(), bcrypt.gensalt())
    with open(PASSWORD_FILE, "wb") as f:
        f.write(hashed)

def check_password(password):
    with open(PASSWORD_FILE, "rb") as f:
        hashed = f.read()
    return bcrypt.checkpw(password.encode(), hashed)

def file_hash(data):
    return hashlib.sha256(data).hexdigest()

class LockBoxApp:
    def __init__(self, root):
        self.root = root
        self.root.title("LockBox")
        self.root.geometry("400x300")
        self.key = None
        self.show_login()

    def show_login(self):
        for widget in self.root.winfo_children():
            widget.destroy()

        first_time = not os.path.exists(PASSWORD_FILE)
        label_text = "Create a master password:" if first_time else "Enter master password:"

        tk.Label(self.root, text="LockBox", font=("Arial", 20)).pack(pady=10)
        tk.Label(self.root, text=label_text).pack(pady=5)
        self.pw_entry = tk.Entry(self.root, show="*")
        self.pw_entry.pack(pady=5)

        def submit():
            password = self.pw_entry.get()
            if first_time:
                if len(password) < 4:
                    messagebox.showerror("Error", "Password too short")
                    return
                setup_password(password)
                self.key = get_key(password)
                log("Master password created")
                self.show_main()
            else:
                if check_password(password):
                    self.key = get_key(password)
                    log("Login successful")
                    self.show_main()
                else:
                    log("Login FAILED - wrong password")
                    messagebox.showerror("Error", "Wrong password")

        tk.Button(self.root, text="Submit", command=submit).pack(pady=10)

    def show_main(self):
        for widget in self.root.winfo_children():
            widget.destroy()

        tk.Label(self.root, text="LockBox - Unlocked", font=("Arial", 16)).pack(pady=10)
        tk.Button(self.root, text="Encrypt a File", command=self.encrypt_file).pack(pady=5)
        tk.Button(self.root, text="Decrypt a File", command=self.decrypt_file).pack(pady=5)
        tk.Button(self.root, text="View Access Log", command=self.view_log).pack(pady=5)

    def encrypt_file(self):
        path = filedialog.askopenfilename()
        if not path:
            return
        with open(path, "rb") as f:
            data = f.read()
        h = file_hash(data)
        fernet = Fernet(self.key)
        encrypted = fernet.encrypt(data)
        with open(path + ".locked", "wb") as f:
            f.write(encrypted)
        with open(path + ".hash", "w") as f:
            f.write(h)
        log("Encrypted file: " + path)
        messagebox.showinfo("Done", "File encrypted:\n" + path + ".locked")

    def decrypt_file(self):
        path = filedialog.askopenfilename(filetypes=[("Locked files", "*.locked")])
        if not path:
            return
        try:
            with open(path, "rb") as f:
                encrypted = f.read()
            fernet = Fernet(self.key)
            data = fernet.decrypt(encrypted)
        except Exception:
            log("Decrypt FAILED (wrong key) on: " + path)
            messagebox.showerror("Error", "Cannot decrypt. Wrong password/key or corrupted file.")
            return

        hash_path = path.replace(".locked", ".hash")
        current_hash = file_hash(data)
        tampered = False
        if os.path.exists(hash_path):
            with open(hash_path) as f:
                original_hash = f.read().strip()
            if current_hash != original_hash:
                tampered = True

        out_path = path.replace(".locked", ".restored")
        with open(out_path, "wb") as f:
            f.write(data)

        if tampered:
            log("TAMPER DETECTED on: " + path)
            messagebox.showwarning("Warning", "File decrypted but INTEGRITY CHECK FAILED.\nThis file may have been tampered with!")
        else:
            log("Decrypted successfully: " + path)
            messagebox.showinfo("Done", "File decrypted and verified:\n" + out_path)

    def view_log(self):
        if not os.path.exists(LOG_FILE):
            messagebox.showinfo("Log", "No activity yet.")
            return
        with open(LOG_FILE) as f:
            content = f.read()
        win = tk.Toplevel(self.root)
        win.title("Access Log")
        text = tk.Text(win, width=60, height=20)
        text.insert("1.0", content)
        text.pack()

root = tk.Tk()
app = LockBoxApp(root)
root.mainloop()