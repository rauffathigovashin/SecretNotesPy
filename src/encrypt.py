import os, base64
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.backends import default_backend

from cryptography.fernet import Fernet

from cryptography.hazmat.primitives.asymmetric import rsa, padding as asym_padding
from cryptography.hazmat.primitives.asymmetric.rsa import RSAPrivateKey, RSAPublicKey

from cryptography.hazmat.primitives.asymmetric.ec import (
    ECDH, SECP256R1, generate_private_key as ec_generate_private_key,
    EllipticCurvePrivateKey, EllipticCurvePublicKey,
)
from cryptography.hazmat.primitives.ciphers.aead import AESGCM


SALT = b""  


def derive_key(password: str, salt: bytes) -> bytes:
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=100_000,
        backend=default_backend(),
    )
    return base64.urlsafe_b64encode(kdf.derive(password.encode()))


def aes_encrypt(plaintext: str, password: str) -> bytes:
    key = derive_key(password, SALT)
    return Fernet(key).encrypt(plaintext.encode("utf-8"))


def aes_decrypt(ciphertext: bytes, password: str) -> str:
    key = derive_key(password, SALT)
    return Fernet(key).decrypt(ciphertext).decode("utf-8")


def rsa_generate_keypair():
    private_key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=2048,
        backend=default_backend(),
    )
    return private_key, private_key.public_key()


def rsa_private_key_to_pem(private_key: RSAPrivateKey, password: str | None = None) -> bytes:
    enc = (
        serialization.BestAvailableEncryption(password.encode())
        if password
        else serialization.NoEncryption()
    )
    return private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=enc,
    )


def rsa_public_key_to_pem(public_key: RSAPublicKey) -> bytes:
    return public_key.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo,
    )


def rsa_load_private_key(pem: bytes, password: str | None = None) -> RSAPrivateKey:
    pwd = password.encode() if password else None
    key = serialization.load_pem_private_key(pem, password=pwd, backend=default_backend())
    if not isinstance(key, RSAPrivateKey):
        raise TypeError("Yüklənən açar RSA özəl açarı deyil!")
    return key


def rsa_load_public_key(pem: bytes) -> RSAPublicKey:
    key = serialization.load_pem_public_key(pem, backend=default_backend())
    if not isinstance(key, RSAPublicKey):
        raise TypeError("Yüklənən açar RSA açıq açarı deyil!")
    return key


def rsa_encrypt(plaintext: str, public_key: RSAPublicKey) -> bytes:
    aes_key = os.urandom(32)
    nonce   = os.urandom(12)
    ct      = AESGCM(aes_key).encrypt(nonce, plaintext.encode("utf-8"), None)

    enc_aes_key = public_key.encrypt(
        aes_key,
        asym_padding.OAEP(
            mgf=asym_padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None,
        ),
    )
    key_len = len(enc_aes_key).to_bytes(4, "big")
    return key_len + enc_aes_key + nonce + ct


def rsa_decrypt(ciphertext: bytes, private_key: RSAPrivateKey) -> str:
    key_len     = int.from_bytes(ciphertext[:4], "big")
    enc_aes_key = ciphertext[4: 4 + key_len]
    nonce       = ciphertext[4 + key_len: 4 + key_len + 12]
    ct          = ciphertext[4 + key_len + 12:]

    aes_key = private_key.decrypt(
        enc_aes_key,
        asym_padding.OAEP(
            mgf=asym_padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None,
        ),
    )
    return AESGCM(aes_key).decrypt(nonce, ct, None).decode("utf-8")


def ecc_generate_keypair():
    private_key = ec_generate_private_key(SECP256R1(), default_backend())
    return private_key, private_key.public_key()


def ecc_private_key_to_pem(private_key: EllipticCurvePrivateKey, password: str | None = None) -> bytes:
    enc = (
        serialization.BestAvailableEncryption(password.encode())
        if password
        else serialization.NoEncryption()
    )
    return private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=enc,
    )


def ecc_public_key_to_pem(public_key: EllipticCurvePublicKey) -> bytes:
    return public_key.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo,
    )


def ecc_load_private_key(pem: bytes, password: str | None = None) -> EllipticCurvePrivateKey:
    pwd = password.encode() if password else None
    key = serialization.load_pem_private_key(pem, password=pwd, backend=default_backend())
    if not isinstance(key, EllipticCurvePrivateKey):
        raise TypeError("Yüklənən açar ECC özəl açarı deyil!")
    return key


def ecc_load_public_key(pem: bytes) -> EllipticCurvePublicKey:
    key = serialization.load_pem_public_key(pem, backend=default_backend())
    if not isinstance(key, EllipticCurvePublicKey):
        raise TypeError("Yüklənən açar ECC açıq açarı deyil!")
    return key


def _ecdh_shared_key(private_key, peer_public_key) -> bytes:
    from cryptography.hazmat.primitives.kdf.hkdf import HKDF
    shared = private_key.exchange(ECDH(), peer_public_key)
    return HKDF(
        algorithm=hashes.SHA256(),
        length=32,
        salt=None,
        info=b"secret-notes-ecc",
        backend=default_backend(),
    ).derive(shared)


def ecc_encrypt(plaintext: str, recipient_public_key: EllipticCurvePublicKey) -> bytes:
    ephemeral_priv = ec_generate_private_key(SECP256R1(), default_backend())
    ephemeral_pub_pem = ecc_public_key_to_pem(ephemeral_priv.public_key())
    aes_key = _ecdh_shared_key(ephemeral_priv, recipient_public_key)

    nonce = os.urandom(12)
    ct = AESGCM(aes_key).encrypt(nonce, plaintext.encode("utf-8"), None)

    pub_len = len(ephemeral_pub_pem).to_bytes(4, "big")
    return pub_len + ephemeral_pub_pem + nonce + ct


def ecc_decrypt(payload: bytes, recipient_private_key: EllipticCurvePrivateKey) -> str:
    pub_len = int.from_bytes(payload[:4], "big")
    ephemeral_pub_pem = payload[4: 4 + pub_len]
    nonce = payload[4 + pub_len: 4 + pub_len + 12]
    ct = payload[4 + pub_len + 12:]

    ephemeral_pub = ecc_load_public_key(ephemeral_pub_pem)
    aes_key = _ecdh_shared_key(recipient_private_key, ephemeral_pub)
    return AESGCM(aes_key).decrypt(nonce, ct, None).decode("utf-8")
