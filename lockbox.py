import tkinter as tk
from tkinter import filedialog
from tkinter import messagebox
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

BG = "#0d1117"
PANEL = "#161b22"
ACCENT = "#00e676"
DANGER = "#ff5252"
WARN = "#ffb300"
TEXT = "#c9d1d9"
FONT_TITLE = ("Consolas", 22, "bold")
FONT_NORMAL = ("Consolas", 11)
FONT_MONO = ("Consolas", 10)

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
        self.root.geometry("520x560")
        self.root.configure(bg=BG)
        self.key = None
        self.failed_attempts = 0
        self.show_login()

    def clear(self):
        for widget in self.root.winfo_children():
            widget.destroy()

    def show_login(self):
        self.clear()
        first_time = not os.path.exists(PASSWORD_FILE)

        tk.Label(self.root, text="🔒 LOCKBOX", font=FONT_TITLE, bg=BG, fg=ACCENT).pack(pady=(40, 5))
        tk.Label(self.root, text="Encrypted File Vault", font=FONT_NORMAL, bg=BG, fg=TEXT).pack(pady=(0, 30))

        label_text = "Create your master password" if first_time else "Enter master password"
        tk.Label(self.root, text=label_text, font=FONT_NORMAL, bg=BG, fg=TEXT).pack(pady=5)

        self.pw_entry = tk.Entry(self.root, show="●", font=FONT_NORMAL, width=25,
                                  bg=PANEL, fg=ACCENT, insertbackground=ACCENT,
                                  relief="flat", justify="center")
        self.pw_entry.pack(pady=10, ipady=8)
        self.pw_entry.focus()
        self.pw_entry.bind("<Return>", lambda e: self.submit_login(first_time))

        self.status_label = tk.Label(self.root, text="", font=FONT_MONO, bg=BG, fg=DANGER)
        self.status_label.pack(pady=5)

        submit = tk.Button(self.root, text="UNLOCK" if not first_time else "CREATE VAULT",
                            font=FONT_NORMAL, bg=ACCENT, fg=BG, relief="flat",
                            activebackground=ACCENT, width=20, cursor="hand2",
                            command=lambda: self.submit_login(first_time))
        submit.pack(pady=15, ipady=6)

    def submit_login(self, first_time):
        password = self.pw_entry.get()
        if first_time:
            if len(password) < 4:
                self.status_label.config(text="Password too short (min 4 chars)")
                return
            setup_password(password)
            self.key = get_key(password)
            log("Master password created")
            self.show_main()
        else:
            if check_password(password):
                self.key = get_key(password)
                self.failed_attempts= 0
                log("Login successful")
                self.show_main()
            else:
                self.failed_attempts +=1
                log("Login FAILED - wrong password(attempt"+str(self.failed_attempts)+")")
                if self.failed_attempts>=3:
                    messagebox.showerror("locked out","too many failed attempts.access denied.")
                    self.root.destory()
                else:
                    self.status_label.config(text="✗ Wrong password("+str(self.failed_attempts)+"/3)")

    def show_main(self):
        self.clear()

        header = tk.Frame(self.root, bg=PANEL)
        header.pack(fill="x")
        tk.Label(header, text="🔓 VAULT UNLOCKED", font=("Consolas", 14, "bold"),
                 bg=PANEL, fg=ACCENT).pack(side="left", padx=15, pady=12)
        tk.Label(header, text=datetime.now().strftime("%d %b %Y"), font=FONT_MONO,
                 bg=PANEL, fg=TEXT).pack(side="right", padx=15)

        btn_frame = tk.Frame(self.root, bg=BG)
        btn_frame.pack(pady=20)

        def make_btn(text, color, command):
            return tk.Button(btn_frame, text=text, font=FONT_NORMAL, bg=color, fg=BG,
                              relief="flat", width=22, cursor="hand2",
                              activebackground=color, command=command)

        make_btn("🔐  Encrypt a File", ACCENT, self.encrypt_file).pack(pady=6, ipady=8)
        make_btn("🔑  Decrypt a File", "#40c4ff", self.decrypt_file).pack(pady=6, ipady=8)
        make_btn("📜  View Access Log", "#b388ff", self.view_log).pack(pady=6, ipady=8)

        self.status_bar = tk.Label(self.root, text="Ready.", font=FONT_MONO,
                                    bg=BG, fg=TEXT, wraplength=460, justify="left")
        self.status_bar.pack(pady=15, padx=20, fill="x")

    def set_status(self, text, color=TEXT):
        self.status_bar.config(text=text, fg=color)

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
        self.set_status("✓ Encrypted: " + os.path.basename(path) + ".locked", ACCENT)

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
            log("Decrypt FAILED (wrong key/corrupted) on: " + path)
            self.set_status("✗ DECRYPT FAILED — wrong key or file corrupted/tampered.", DANGER)
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
            self.set_status("⚠ TAMPER DETECTED — file changed after encryption!", WARN)
        else:
            log("Decrypted successfully: " + path)
            self.set_status("✓ Verified & decrypted: " + os.path.basename(out_path), ACCENT)

    def view_log(self):
        win = tk.Toplevel(self.root)
        win.title("Access Log")
        win.configure(bg=BG)
        win.geometry("480x360")
        tk.Label(win, text="ACCESS LOG", font=("Consolas", 12, "bold"),
                 bg=BG, fg=ACCENT).pack(pady=10)
        text = tk.Text(win, width=58, height=18, bg=PANEL, fg=TEXT,
                        font=FONT_MONO, relief="flat", insertbackground=TEXT)
        text.pack(padx=10, pady=5)
        if os.path.exists(LOG_FILE):
            with open(LOG_FILE) as f:
                text.insert("1.0", f.read())
        else:
            text.insert("1.0", "No activity yet.")
        text.config(state="disabled")

root = tk.Tk()
app = LockBoxApp(root)
root.mainloop()