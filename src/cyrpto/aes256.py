from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad
from src.cyrpto.cyrpto import ACyrpto

class AES256(ACyrpto):
    def __init__(self, key: str):
        # AES256 requires a 32-byte key
        super().__init__(key)
        self.key_bytes = self.key.encode('utf-8')[:32].ljust(32, b'0')

    def encrypt(self, data: str) -> str:
        cipher = AES.new(self.key_bytes, AES.MODE_ECB)
        padded_data = pad(data.encode('utf-8'), AES.block_size)
        encrypted = cipher.encrypt(padded_data)
        return encrypted.hex()

    def decrypt(self, data: str) -> str:
        cipher = AES.new(self.key_bytes, AES.MODE_ECB)
        decrypted = cipher.decrypt(bytes.fromhex(data))
        unpadded = unpad(decrypted, AES.block_size)
        return unpadded.decode('utf-8')
