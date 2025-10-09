Secret Notes - A Secret Note Application
Description
Secret Notes is a simple desktop application that allows you to protect your text notes with strong encryption and store them securely on your computer. With its user-friendly interface, you can easily lock your notes with a key (password) and access them again only with the correct key.

Features
User-Friendly Interface: Built with Tkinter, Python's standard GUI library.

Strong Encryption: Notes are encrypted using the industry-standard cryptography library (Fernet symmetric encryption).

Password-Based Protection: The key (password) you enter is converted into a secure encryption key using the PBKDF2HMAC algorithm. This ensures your key is never stored as plain text.

File-Based Storage: Each note is stored in a separate, encrypted file with an .enc extension, based on the title you provide.

Requirements
To run the application, you need to have the following libraries installed on your computer:

Python 3.x

Pillow (For image processing)

cryptography (For encryption operations)

Installation
To install the required libraries, type the following command into your terminal or command prompt:

pip install Pillow cryptography

Then you can run the Python script (secret_notes_app.py).

How to Use
Encrypting and Saving a Note:

Enter a title for your note in the "Enter your title" field. This will also be the filename.

Set a key (password) to lock your note in the "Enter your key" field.

Write your secret note in the "Enter your note" area.

Click the "Save & Encrypt" button. Your note will be encrypted and saved in the project's directory.

Decrypting and Viewing a Note:

Enter the title of the note you want to open in the "Enter your title" field.

Enter the correct key you used when saving that note in the "Enter your key" field.

Click the "Decrypt & Load" button. If the title and key are correct, your note will appear in the text box.

IMPORTANT SECURITY WARNING: If you forget the key (password) you have set, you will never be able to access your encrypted notes again. Please make sure to keep your key in a safe place.
