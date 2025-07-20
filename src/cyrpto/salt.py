import hashlib
from src.model.model_salt import ModelSalt as DTOSalt

class Salt:
    _methods = ["sha256", "sha512", "md5", "argon2"]

    def __init__(self, method="sha256", salt=None):
        if method not in self._methods:
            raise ValueError(f"Unsupported method: {method}")
        if method == "argon2":
            raise ImportError("argon2-cffi is required for argon2 method.")
        self.method = method
        self.salt = salt or self._generate_salt()

    def _generate_salt(self, length=16):
        import os
        return os.urandom(length).hex()

    def apply_salt(self, secret_key: str) -> str:
        """
        Apply the salt to the data using the specified method.
        """
        if self.method == "sha256":
            return hashlib.sha256((self.salt + secret_key).encode()).hexdigest()
        elif self.method == "sha512":
            return hashlib.sha512((self.salt + secret_key).encode()).hexdigest()
        elif self.method == "md5":
            return hashlib.md5((self.salt + secret_key).encode()).hexdigest()
        else:
            raise ValueError(f"Unsupported method: {self.method}")
    
    def get_methods(self):
        """
        Return the list of supported methods.
        """
        return self._methods
    
    def toDTO(self):
        """
        Convert the current instance to a DTO (Data Transfer Object).
        """
        return DTOSalt(method=self.method, salt=self.salt)

if __name__ == "__main__":
    # Example usage
    salt_instance = Salt(method="sha256")
    salted_data = salt_instance.apply_salt(secret_key="poqob")
    print(f"Salted data: {salted_data}")