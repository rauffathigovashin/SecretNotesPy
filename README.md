# Secret Notes - A Secret Note Application
## Description

Secret Notes is a simple desktop application that allows you to protect your text notes with strong encryption and store them securely on your computer. With its user-friendly interface, you can easily lock your notes with a key (password) and access them again only with the correct key.

---

## Features

- User-Friendly Interface: Built with Tkinter, Python's standard GUI library.

- Strong Encryption: Notes are encrypted using the industry-standard cryptography library (Fernet symmetric encryption).

- Password-Based Protection: The key (password) you enter is converted into a secure encryption key using the PBKDF2HMAC algorithm. This ensures your key is never stored as plain text.

- File-Based Storage: Each note is stored in a separate, encrypted file with an .enc extension, based on the title you provide.