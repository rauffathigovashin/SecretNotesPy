import tkinter as tk
from tkinter import messagebox
from PIL import ImageTk, Image
import os

# --- GÜVENLİ ŞİFRELEME İÇİN GEREKLİ KÜTÜPHANELER ---
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.backends import default_backend
import base64

path = r"D:\Downloads\pngtree-top-secret-envelope-note-dossier-label-vector-picture-image_9448898.png"

# --- ŞİFRELEME FONKSİYONLARI ---

SALT = b'gizli_notlar_icin_salt_degeri'

def derive_key(password: str, salt: bytes) -> bytes:
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=100000,
        backend=default_backend()
    )
    return base64.urlsafe_b64encode(kdf.derive(password.encode()))


# --- ARAYÜZ FONKSİYONLARI ---

def encrypt_and_save():
    title = title_entry.get()
    password = password_entry.get()
    secret_text = text_box.get("1.0", "end-1c")
    if not title or not password or not secret_text:
        messagebox.showwarning("Missing Information", "Please fill in the title, key, and note fields.")
        return

    try:
        key = derive_key(password, SALT)
        f = Fernet(key)
        encrypted_data = f.encrypt(secret_text.encode('utf-8'))

        filename = f"{title}.enc"
        with open(filename, 'wb') as file:
            file.write(encrypted_data)

        messagebox.showinfo("Success", f"Your note has been encrypted and saved as '{filename}'.")

        title_entry.delete(0, tk.END)
        password_entry.delete(0, tk.END)
        text_box.delete("1.0", tk.END)

    except Exception as e:
        messagebox.showerror("Error", f"An error occurred during encryption: {e}")


def decrypt_and_load():
    title = title_entry.get()
    password = password_entry.get()

    if not title or not password:
        messagebox.showwarning("Missing Information", "Please enter the title of the note and your key to decrypt it.")
        return

    filename = f"{title}.enc"
    if not os.path.exists(filename):
        # --- DEĞİŞTİRİLDİ ---
        messagebox.showerror("Error", f"File named '{filename}' could not be found.")
        return

    try:
        with open(filename, 'rb') as file:
            encrypted_data = file.read()

        key = derive_key(password, SALT)
        f = Fernet(key)

        decrypted_data = f.decrypt(encrypted_data).decode('utf-8')

        text_box.delete("1.0", tk.END)
        text_box.insert("1.0", decrypted_data)
        messagebox.showinfo("Success", "Your note has been successfully decrypted and loaded.")

    except Exception as e:
        messagebox.showerror("Error", "Decryption failed! Please check your key or the file may be corrupt.")


# --- TKINTER ARAYÜZ KURULUMU ---
window = tk.Tk()
window.title("Secret Notes")
window.geometry("400x700")

# --- Resim Bölümü ---
try:
    original_image = Image.open(path)
    resized_image = original_image.resize((110, int(110 * original_image.height / original_image.width)))
    img = ImageTk.PhotoImage(resized_image)
    image_label = tk.Label(window, image=img)
    image_label.pack(pady=10)
except FileNotFoundError:
    image_label = tk.Label(window, text="Image file not found!", fg="red")
    image_label.pack(pady=10)

# --- Başlık Bölümü ---
label_title = tk.Label(window, text="Enter your title", font=("Arial", 12))
label_title.pack()
title_entry = tk.Entry(window, width=25)
title_entry.pack(pady=5)

# --- Şifre Bölümü ---
label_password = tk.Label(window, text="Enter your key", font=("Arial", 12))
label_password.pack()
password_entry = tk.Entry(window, width=25, show="*")  # show="*" şifreyi gizler
password_entry.pack(pady=5)

# --- Metin Kutusu Bölümü ---
label_textbox = tk.Label(window, text="Enter your note", font=("Arial", 12))
label_textbox.pack(pady=(10, 0))
text_box = tk.Text(window, height=15, width=40)
text_box.pack(pady=10, padx=20)

# --- Buton Bölümü ---
button_frame = tk.Frame(window)
button_frame.pack(pady=10)

encrypt_button = tk.Button(button_frame, text="Save & Encrypt", command=encrypt_and_save, bg="#4CAF50", fg="white",
                           font=("Arial", 10, "bold"))
encrypt_button.grid(row=0, column=0, padx=10, ipadx=10, ipady=5)

decrypt_button = tk.Button(button_frame, text="Decrypt & Load", command=decrypt_and_load, bg="#f44336", fg="white",
                           font=("Arial", 10, "bold"))
decrypt_button.grid(row=0, column=1, padx=10, ipadx=10, ipady=5)

window.mainloop()
