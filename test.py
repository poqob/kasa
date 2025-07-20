from src.repository.cipherRepository import CipherRepository,ModelCipher
from src.cyrpto.encryptor import Encryptor
from src.cyrpto.decrptor import Decryptor
from src.repository.saltRepository import SaltRepository,ModelSalt
from src.repository.sessionRepository import SessionRepository,ModelSession
from src.utils.enviroment_variable import read_env_file
from src.cyrpto.salt import Salt
from datetime import datetime,timedelta
from src.utils.cache_manager import CacheManager

def cipher_db_test():
    sql=read_env_file().get('sqlite_db_path')
    repo = CipherRepository(sqlite_path=sql)

    salt = Salt(method="sha256")
    key = salt.apply_salt(secret_key="poqob")

    enc = Encryptor(key=key, method_name="aes256")
    print(enc.encrypt("Hello, World!"))

    dec = Decryptor(key=key, method_name="aes256")
    print(dec.decrypt(enc.encrypt("Hello, World!")))

    cipher = ModelCipher(name="Test Cipher", encrypted_cipher=enc.encrypt("Hello, World!"), method="aes256")

    cipher_id = repo.add(cipher)

    _cipher = repo.get(index=cipher_id)
    if cipher:
        print(f"Cipher ID: {_cipher.id}, Name: {_cipher.name}, Method: {_cipher.method}")
    

def salt_db_test():
    sql=read_env_file().get('sqlite_db_path')
    repo = SaltRepository(sqlite_path=sql)

    salt = Salt(method="sha256")
    key = salt.apply_salt(secret_key="poqob")
    msalt = ModelSalt(method="sha256", salt=key)
    salt_id = repo.add(msalt)

    _salt = repo.get(index=salt_id)
    if _salt:
        print(f"Salt ID: {_salt.id}, Method: {_salt.method}, Salt: {_salt.salt}")


def session_db_test():
    sql=read_env_file().get('sqlite_db_path')
    repo = SessionRepository(sqlite_path=sql)

    session = ModelSession(token="custom-token", expiration=datetime.now() + timedelta(days=1))
    session_id = repo.add(session)
    _session = repo.get(index=session_id)
    if _session:
        print(f"Session ID: {_session.id}, Token: {_session.token}, Expiration: {_session.expiration}")


def cache_manager_test():
    _models = ["cipher", "salt", "session"]
    for model in _models:
        cm = CacheManager(model_name=model)
        cm.flush_cache()
        cm.sync()

if __name__ == "__main__":
    cache_manager_test()
    session_db_test()
