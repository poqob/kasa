from src.cyrpto.aes128 import AES128
from src.cyrpto.aes256 import AES256
from src.cyrpto.chacha20 import Chacha20

class Encryptor:
    def __init__(self,method_name: str, key: str):
        self.strategies = {
            "aes128": AES128,
            "aes256": AES256,
            "chacha20": Chacha20
        }

        self.method_name = method_name.lower()
        self.key = key

        if self.method_name not in self.strategies:
            raise ValueError(f"Unknown method: {self.method_name}")
        
        
        self._method  = self.strategies.get(self.method_name)(key=self.key)

    def encrypt(self, plaintext: str) -> str:
        return self._method.encrypt(plaintext)
