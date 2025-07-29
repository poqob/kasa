from src.model.model_salt import ModelSalt
from src.repository.sqlite import SqliteRepository
from src.services.saltService import SaltService
from src.utils.enviroment_variable import read_env_file
from src.cyrpto.salt import Salt
from src.services.cipherService import CipherService

def salt_create_test(method="sha256", secret_key="poqob"):
    salt = Salt(method=method)
    key = salt.apply_salt(secret_key=secret_key)
    msalt = ModelSalt(method=method, salt=key)
    print(msalt)
    return msalt

def all_salt_from_db():
    sql = read_env_file().get('sqlite_db_path')
    repo = SqliteRepository(db_url=f'sqlite:///{sql}', model_name='salt')
    
    salts = repo.get_all()
    for salt in salts:
        print(f"Salt ID: {salt.id}, Method: {salt.method}, Salt: {salt.salt}")

# service level test
def salt_service_test():
    salt_service = SaltService(config_path=".env")
    salt = salt_service.get_salt(salt_id=1)
    print(f"Salted Key: {salt}")


def salt_create_test():
    salt_service = SaltService(config_path=".env")
    msalt=salt_service.create_salt(method='sha512')

def list_salt_methods_test():
    salt_service = SaltService(config_path=".env")
    print(salt_service.get_supported_methods())

def list_all_salts():
    salt_service = SaltService(config_path=".env")
    salts = salt_service.list_all_salts()
    for salt in salts:
        print(salt)

def generate_salt_test():
    salt_service = SaltService(config_path=".env")
    print(salt_service.generate_salt_for_key(secret_key="test_key", method="sha256"))
