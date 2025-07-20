from abc import ABC, abstractmethod

class ACyrpto(ABC):
    def __init__(self, key: str):
        self.key = key

    @abstractmethod
    def encrypt(self, data: str) -> str:
        pass

    @abstractmethod
    def decrypt(self, data: str) -> str:
        pass