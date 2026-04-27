"""
gui.py – Secret Notes – Ana arayüz
Desteklenen şifreleme metodları: AES-256 (Fernet) | RSA-2048 | ECC (P-256)
"""

import os, tkinter as tk
from tkinter import messagebox, simpledialog, ttk, scrolledtext
from path import ICON_PNG, DATA_DIR
import encrypt

BG         = "#1a1a2e"
PANEL      = "#16213e"
ACCENT     = "#0f3460"
HIGHLIGHT  = "#e94560"
TEXT_FG    = "#eaeaea"
ENTRY_BG   = "#0d1b2a"
BTN_ENC    = "#00b4d8"
BTN_DEC    = "#e94560"
BTN_KEYGEN = "#7b2d8b"
BTN_IMPORT = "#2d6a4f"
FONT_MAIN  = ("Segoe UI", 11)
FONT_BOLD  = ("Segoe UI", 11, "bold")
FONT_TITLE = ("Segoe UI", 16, "bold")
FONT_SMALL = ("Segoe UI", 9)


state = {
    "rsa_private": None,  
    "rsa_public":  None,  
    "ecc_private": None,  
    "ecc_public":  None,  
}


def styled_button(parent, text, command, bg=HIGHLIGHT, **kw):
    btn = tk.Button(
        parent, text=text, command=command,
        bg=bg, fg="white", font=FONT_BOLD,
        relief="flat", cursor="hand2",
        activebackground=bg, activeforeground="white",
        padx=12, pady=6, **kw
    )
    btn.bind("<Enter>", lambda e: btn.config(bg=_lighten(bg)))
    btn.bind("<Leave>", lambda e: btn.config(bg=bg))
    return btn


def _lighten(hex_color: str) -> str:
    """Rengi %20 aydınlatır (hover efekti için)."""
    hex_color = hex_color.lstrip("#")
    r, g, b = (int(hex_color[i:i+2], 16) for i in (0, 2, 4))
    r = min(255, r + 40)
    g = min(255, g + 40)
    b = min(255, b + 40)
    return f"#{r:02x}{g:02x}{b:02x}"



def on_method_change(*_):
    method = method_var.get()
    if method == "AES-256":
        pw_label.config(text="Şifrə / Açar:")
        password_entry.config(state="normal")
        key_frame.grid_remove()
    else:
        pw_label.config(text="Açar şifrəsi (mütləq deyil):")
        password_entry.config(state="normal")
        key_frame.grid()
        update_key_status()


def update_key_status():
    method = method_var.get()
    if method == "RSA-2048":
        has_priv = state["rsa_private"] is not None
        has_pub  = state["rsa_public"]  is not None
        status   = ("✔ Özəl + Açıq" if has_priv and has_pub
                    else "✔ Özəl" if has_priv
                    else "✔ Açıq" if has_pub
                    else "Açar yoxdur")
        key_status_lbl.config(text=f"RSA: {status}")
    elif method == "ECC (P-256)":
        has_priv = state["ecc_private"] is not None
        has_pub  = state["ecc_public"]  is not None
        status   = ("✔ Özəl + Açıq" if has_priv and has_pub
                    else "✔ Özəl" if has_priv
                    else "✔ Açıq" if has_pub
                    else "Açar yoxdur")
        key_status_lbl.config(text=f"ECC: {status}")


def generate_keys():
    method = method_var.get()
    if method == "AES-256":
        messagebox.showinfo("Məlumat", "AES-256 üçün ayrı bir açar istehsal edilmir;\nşifrə qutusuna yazdığınız mətn açar olaraq istifadə olunur.")
        return

    if messagebox.askyesno("Açar istehsalı", f"Yeni {method} açar cütü istehsal ediləcək.\nMövcud açarlar silinəcək. Davam?"):
        if method == "RSA-2048":
            priv, pub = encrypt.rsa_generate_keypair()
            state["rsa_private"] = priv
            state["rsa_public"]  = pub
        else:
            priv, pub = encrypt.ecc_generate_keypair()
            state["ecc_private"] = priv
            state["ecc_public"]  = pub

        update_key_status()
        if messagebox.askyesno("Saxla", "Açarı faylda saxlamaq istiyirsiniz?"):
            export_keys()


def export_keys():
    method = method_var.get()
    pw = password_entry.get().strip() or None

    if method == "RSA-2048":
        priv, pub = state["rsa_private"], state["rsa_public"]
        if not priv:
            messagebox.showwarning("Məlumat", "Əvvəlcə RSA açarı istehsal edin.")
            return
        priv_pem = encrypt.rsa_private_key_to_pem(priv, pw)
        pub_pem  = encrypt.rsa_public_key_to_pem(pub)
        _save_pem("rsa_private.pem", priv_pem)
        _save_pem("rsa_public.pem",  pub_pem)

    elif method == "ECC (P-256)":
        priv, pub = state["ecc_private"], state["ecc_public"]
        if not priv:
            messagebox.showwarning("Məlumat", "Əvvəlcə ECC açarı istehsal edin.")
            return
        priv_pem = encrypt.ecc_private_key_to_pem(priv, pw)
        pub_pem  = encrypt.ecc_public_key_to_pem(pub)
        _save_pem("ecc_private.pem", priv_pem)
        _save_pem("ecc_public.pem",  pub_pem)
    else:
        messagebox.showinfo("Məlumat", "AES üçün xaricə köçürüləcək açar faylı yoxdur.")


def _save_pem(filename: str, data: bytes):
    path = os.path.join(DATA_DIR, filename)
    with open(path, "wb") as f:
        f.write(data)
    messagebox.showinfo("Saxlanıldı", f"{filename} → {DATA_DIR}")


def import_keys():
    method = method_var.get()
    if method == "AES-256":
        messagebox.showinfo("Məlumat", "AES üçün daxilə köçürüləcək açar faylı yoxdur.")
        return

    pw = password_entry.get().strip() or None

    if method == "RSA-2048":
        priv_path = os.path.join(DATA_DIR, "rsa_private.pem")
        pub_path  = os.path.join(DATA_DIR, "rsa_public.pem")
        _load_key_pair(priv_path, pub_path, "rsa", encrypt.rsa_load_private_key,
                       encrypt.rsa_load_public_key, pw)
    else:
        priv_path = os.path.join(DATA_DIR, "ecc_private.pem")
        pub_path  = os.path.join(DATA_DIR, "ecc_public.pem")
        _load_key_pair(priv_path, pub_path, "ecc", encrypt.ecc_load_private_key,
                       encrypt.ecc_load_public_key, pw)

    update_key_status()


def _load_key_pair(priv_path, pub_path, prefix, load_priv_fn, load_pub_fn, pw):
    loaded = []
    if os.path.exists(priv_path):
        try:
            with open(priv_path, "rb") as f:
                state[f"{prefix}_private"] = load_priv_fn(f.read(), pw)
            loaded.append("Özəl açar")
        except Exception as e:
            messagebox.showerror("Səhv", f"Özəl açar yüklənəmədi:\n{e}")
    if os.path.exists(pub_path):
        try:
            with open(pub_path, "rb") as f:
                state[f"{prefix}_public"] = load_pub_fn(f.read())
            loaded.append("Açıq açar")
        except Exception as e:
            messagebox.showerror("Səhv", f"Açıq açar daxilə köçürüləmedi:\n{e}")
    if loaded:
        messagebox.showinfo("Daxilə köçürüldü", f"Yükləndi: {', '.join(loaded)}")
    else:
        messagebox.showwarning("Tapılmadı", f"{DATA_DIR} içinde PEM faylı tapılmadı.")


def encrypt_and_save():
    title    = title_entry.get().strip()
    password = password_entry.get().strip()
    text     = text_box.get("1.0", "end-1c").strip()
    method   = method_var.get()

    if not title or not text:
        messagebox.showwarning("Əksik məlumat", "Başlıq və qeyd sahələrini doldurun.")
        return

    try:
        if method == "AES-256":
            if not password:
                messagebox.showwarning("Əksik məlumat", "AES üçün şifrə girməlisiniz.")
                return
            raw = encrypt.aes_encrypt(text, password)

        elif method == "RSA-2048":
            pub = state["rsa_public"]
            if pub is None:
                messagebox.showwarning("Açar yoxdur", "RSA açıq açarı yüklü deyil.\nİstehsal et və ya içə köçür düyməsini istifadə et.")
                return
            raw = encrypt.rsa_encrypt(text, pub)

        else:
            pub = state["ecc_public"]
            if pub is None:
                messagebox.showwarning("Açar yoxdur", "ECC açıq açarı yüklü deyil.\nİstehsal et və ya içə köçür düyməsini istifadə et.")
                return
            raw = encrypt.ecc_encrypt(text, pub)

        method_tag = method.encode("utf-8")
        tag_len    = len(method_tag).to_bytes(2, "big")
        payload    = tag_len + method_tag + raw

        filepath = os.path.join(DATA_DIR, f"{title}.enc")
        with open(filepath, "wb") as fh:
            fh.write(payload)

        messagebox.showinfo("Uğurlu", f"Not şifrələndi və saxlanıldı:\n{title}.enc\nMetod: {method}")
        title_entry.delete(0, tk.END)
        password_entry.delete(0, tk.END)
        text_box.delete("1.0", tk.END)

    except Exception as e:
        messagebox.showerror("Səhv", f"Şifrələmə uğursuz alındı:\n{e}")


def decrypt_and_load():
    title    = title_entry.get().strip()
    password = password_entry.get().strip()

    if not title:
        messagebox.showwarning("Əksik məlumat", "Şifrənin şifrəsini daxil edin.")
        return

    filepath = os.path.join(DATA_DIR, f"{title}.enc")
    if not os.path.exists(filepath):
        messagebox.showerror("Səhv", f"'{title}.enc' faylı tapılmadı.")
        return

    try:
        with open(filepath, "rb") as fh:
            payload = fh.read()

        tag_len  = int.from_bytes(payload[:2], "big")
        method   = payload[2: 2 + tag_len].decode("utf-8")
        raw      = payload[2 + tag_len:]

        if method == "AES-256":
            if not password:
                messagebox.showwarning("Əksik məlumat", "AES şifrəsi gerekli.")
                return
            plain = encrypt.aes_decrypt(raw, password)

        elif method == "RSA-2048":
            priv = state["rsa_private"]
            if priv is None:
                messagebox.showwarning("Açar yoxdur", "RSA özəl açarı yüklü deyil.")
                return
            plain = encrypt.rsa_decrypt(raw, priv)

        else: 
            priv = state["ecc_private"]
            if priv is None:
                messagebox.showwarning("Açar yoxdur", "ECC özəl açarı yüklü deyil.")
                return
            plain = encrypt.ecc_decrypt(raw, priv)

        text_box.delete("1.0", tk.END)
        text_box.insert("1.0", plain)
        messagebox.showinfo("Uğurlu", f"Not şifrəsi açıldı! (Metod: {method})")

    except Exception:
        messagebox.showerror("Səhv", "Şifrənin şifrəsi açılmadı! Yanlış açar/şifrə və ya bozuk dosya.")



window = tk.Tk()
window.title("Secret Notes")
window.geometry("500x680")
window.resizable(False, False)
window.config(bg=BG)

try:
    icon = tk.PhotoImage(file=ICON_PNG)
    window.iconphoto(True, icon)
except Exception:
    pass

header = tk.Frame(window, bg=ACCENT, pady=14)
header.pack(fill="x")
tk.Label(header, text="🔒 Secret Notes", font=FONT_TITLE,
         bg=ACCENT, fg=TEXT_FG).pack()
tk.Label(header, text="Şifrəli Not Meneceri", font=FONT_SMALL,
         bg=ACCENT, fg="#aaaacc").pack()

content = tk.Frame(window, bg=BG, padx=24, pady=18)
content.pack(fill="both", expand=True)

tk.Label(content, text="Şifrələmə Metodu:", font=FONT_BOLD,
         bg=BG, fg=TEXT_FG).grid(row=0, column=0, sticky="w", pady=(0, 2))

method_var = tk.StringVar(value="AES-256")
methods    = ["AES-256", "RSA-2048", "ECC (P-256)"]

method_menu = ttk.Combobox(content, textvariable=method_var, values=methods,
                            state="readonly", font=FONT_MAIN, width=18)
method_menu.grid(row=0, column=1, sticky="ew", padx=(8, 0), pady=(0, 2))
method_menu.bind("<<ComboboxSelected>>", on_method_change)

method_info = {
    "AES-256":     "Simmetrik | Sürətli | Şifrə əsaslı",
    "RSA-2048":    "Asimetrik | Açıq/Xüsusi açar cütlü",
    "ECC (P-256)": "Asimetrik | Əliptik Əyri | Kiçik açar",
}

info_lbl = tk.Label(content, text=method_info["AES-256"],
                    font=FONT_SMALL, bg=BG, fg="#8888cc")
info_lbl.grid(row=1, column=0, columnspan=2, sticky="w", pady=(0, 10))


def refresh_info(*_):
    info_lbl.config(text=method_info.get(method_var.get(), ""))
    on_method_change()


method_menu.bind("<<ComboboxSelected>>", refresh_info)

style = ttk.Style()
style.theme_use("clam")
style.configure("TCombobox",
                fieldbackground=ENTRY_BG,
                background=ACCENT,
                foreground=TEXT_FG,
                selectbackground=HIGHLIGHT,
                selectforeground="white",
                arrowcolor=TEXT_FG)

tk.Label(content, text="Not Adı:", font=FONT_BOLD,
         bg=BG, fg=TEXT_FG).grid(row=2, column=0, sticky="w", pady=(4, 2))
title_entry = tk.Entry(content, width=30, font=FONT_MAIN,
                       bg=ENTRY_BG, fg=TEXT_FG,
                       insertbackground=TEXT_FG, relief="flat",
                       highlightthickness=1, highlightcolor=HIGHLIGHT,
                       highlightbackground=ACCENT)
title_entry.grid(row=2, column=1, sticky="ew", padx=(8, 0), pady=(4, 2))

pw_label = tk.Label(content, text="Şifrə / Açar:", font=FONT_BOLD,
                    bg=BG, fg=TEXT_FG)
pw_label.grid(row=3, column=0, sticky="w", pady=(4, 2))
password_entry = tk.Entry(content, width=30, show="*", font=FONT_MAIN,
                          bg=ENTRY_BG, fg=TEXT_FG,
                          insertbackground=TEXT_FG, relief="flat",
                          highlightthickness=1, highlightcolor=HIGHLIGHT,
                          highlightbackground=ACCENT)
password_entry.grid(row=3, column=1, sticky="ew", padx=(8, 0), pady=(4, 2))

key_frame = tk.LabelFrame(content, text="Açar İdarə Etməsi",
                          font=FONT_BOLD, bg=PANEL, fg=TEXT_FG,
                          relief="groove", bd=2)
key_frame.grid(row=4, column=0, columnspan=2, sticky="ew",
               pady=(10, 4), padx=0)
key_frame.grid_remove() 

key_status_lbl = tk.Label(key_frame, text="Açar yoxdur",
                           font=FONT_SMALL, bg=PANEL, fg="#ffbb00")
key_status_lbl.grid(row=0, column=0, columnspan=3, pady=(6, 4), padx=8, sticky="w")

btn_keygen = styled_button(key_frame, "⚙ Yarat",  generate_keys, bg=BTN_KEYGEN)
btn_keygen.grid(row=1, column=0, padx=6, pady=6)

btn_export = styled_button(key_frame, "📤 Export", export_keys, bg=BTN_IMPORT)
btn_export.grid(row=1, column=1, padx=6, pady=6)

btn_import = styled_button(key_frame, "📥 Import", import_keys, bg=ACCENT)
btn_import.grid(row=1, column=2, padx=6, pady=6)

tk.Label(content, text="Not Məzmunu:", font=FONT_BOLD,
         bg=BG, fg=TEXT_FG).grid(row=5, column=0, sticky="nw", pady=(14, 2))

text_box = scrolledtext.ScrolledText(
    content, height=9, width=38, font=("Consolas", 11),
    bg=ENTRY_BG, fg=TEXT_FG, insertbackground=TEXT_FG,
    relief="flat", highlightthickness=1,
    highlightcolor=HIGHLIGHT, highlightbackground=ACCENT,
    wrap="word"
)
text_box.grid(row=5, column=1, sticky="ew", padx=(8, 0), pady=(14, 2))

btn_row = tk.Frame(content, bg=BG)
btn_row.grid(row=6, column=0, columnspan=2, pady=(20, 4))

enc_btn = styled_button(btn_row, "💾  Şifrələ & Saxla", encrypt_and_save, bg=BTN_ENC)
enc_btn.pack(side="left", padx=10)

dec_btn = styled_button(btn_row, "🔓  Şifrəni Aç & Yoxla", decrypt_and_load, bg=BTN_DEC)
dec_btn.pack(side="left", padx=10)


tk.Label(window, text="Secret Notes  •  AES-256 / RSA-2048 / ECC(P-256)",
         font=FONT_SMALL, bg=BG, fg="#555577").pack(side="bottom", pady=6)

content.columnconfigure(1, weight=1)

window.mainloop()
