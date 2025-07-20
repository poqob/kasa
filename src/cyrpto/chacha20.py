from Crypto.Cipher import ChaCha20
from src.cyrpto.cyrpto import ACyrpto

class Chacha20(ACyrpto):
    def __init__(self, key: str):
        # ChaCha20 requires a 32-byte key
        super().__init__(key)
        self.key_bytes = self.key.encode('utf-8')[:32].ljust(32, b'0')

    def encrypt(self, data: str) -> str:
        cipher = ChaCha20.new(key=self.key_bytes)
        ciphertext = cipher.encrypt(data.encode('utf-8'))
        nonce = cipher.nonce.hex()
        return f"{nonce}:{ciphertext.hex()}"

    def decrypt(self, data: str) -> str:
        nonce_hex, ciphertext_hex = data.split(":")
        nonce = bytes.fromhex(nonce_hex)
        ciphertext = bytes.fromhex(ciphertext_hex)
        cipher = ChaCha20.new(key=self.key_bytes, nonce=nonce)
        plaintext = cipher.decrypt(ciphertext)
        return plaintext.decode('utf-8')
