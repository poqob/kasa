from src.model.model_cipher import ModelCipher
from src.model.model_salt import ModelSalt
from src.model.model_session import ModelSession

MODELS = {
    'cipher': ModelCipher,
    'salt': ModelSalt,
    'session': ModelSession
}
