"""
XProtect Mobile XML-RPC Protocol — Auth Layer

Implements the Diffie-Hellman key exchange + CHAP challenge-response
authentication used by the XProtect Mobile protocol.

Reference: XPMobileSDK.js/Lib/security/ (DiffieHellman.js, CHAP.js, AES.js)
"""
import os
import hashlib
import hmac
from cryptography.hazmat.primitives.asymmetric import dh
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes

# Standard DH group (2048-bit) matching Milestone's implementation
# Usually sent by server in Connect response
DH_P = int(
    "FFFFFFFFFFFFFFFFC90FDAA22168C234C4C6628B80DC1CD129024E08"
    "8A67CC74020BBEA63B139B22514A08798E3404DDEF9519B3CD3A431B"
    "302B0A6DF25F14374FE1356D6D51C245E485B576625E7EC6F44C42E9"
    "A637ED6B0BFF5CB6F406B7EDEE386BFB5A899FA5AE9F24117C4B1FE6"
    "49286651ECE65381FFFFFFFFFFFFFFFF",
    16,
)
DH_G = 2


class MobileAuth:
    """Handles DH key exchange and CHAP authentication for Mobile SDK protocol."""

    def __init__(self):
        self.shared_secret: bytes | None = None
        self.session_key: bytes | None = None
        self.server_challenge: str | None = None
        self.connection_id: str | None = None
        self._private_key: dh.DHPrivateKey | None = None

    def generate_client_key_pair(self) -> tuple[int, int]:
        """Generate DH key pair, return (public_key, private_key)."""
        params = dh.DHParameterNumbers(DH_P, DH_G)
        parameters = params.parameters()
        self._private_key = parameters.generate_private_key()
        pub_key = self._private_key.public_key()
        pub_numbers = pub_key.public_numbers()
        return pub_numbers.y, self._private_key.private_numbers().x

    def compute_shared_secret(self, server_public_key: int) -> bytes:
        """Compute the shared secret from server's public key."""
        params = dh.DHParameterNumbers(DH_P, DH_G)
        parameters = params.parameters()
        peer_pub = parameters.public_numbers(server_public_key)
        shared_key = self._private_key.exchange(peer_pub)
        # SHA256 hash to produce the 32-byte session key
        self.shared_secret = hashlib.sha256(
            shared_key.to_bytes((shared_key.bit_length() + 7) // 8, "big")
        ).digest()
        return self.shared_secret

    def compute_chap_response(self, password: str, challenge: str) -> str:
        """CHAP response: HMAC-SHA256(shared_secret, challenge + password)."""
        msg = (challenge + password).encode("utf-8")
        digest = hmac.new(self.shared_secret, msg, hashlib.sha256).hexdigest().upper()
        return digest

    def encrypt_password(self, password: str) -> str:
        """Encrypt password with AES-256-CBC using the session key."""
        iv = os.urandom(16)
        cipher = Cipher(algorithms.AES(self.shared_secret), modes.CBC(iv))
        encryptor = cipher.encryptor()
        # PKCS7 padding
        pad_len = 16 - (len(password) % 16)
        padded = password + chr(pad_len) * pad_len
        encrypted = encryptor.update(padded.encode("utf-8")) + encryptor.finalize()
        return (iv + encrypted).hex()
