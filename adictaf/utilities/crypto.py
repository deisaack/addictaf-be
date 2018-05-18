import base64
import os

from cryptography.fernet import Fernet
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from django.conf import settings

__all__ = ['SafiCrypto']


class SafiCrypto(object):
    def __init__(self):
        self.password = settings.SECRET_KEY.encode('utf-8')
        self.f = Fernet(settings.CRYPTO_KEY.encode('utf-8'))

    def generate_new_key(self):
        '''
        This method generates a new key for use later
        This is what was used to create the CRYPTO_KEY that was put in the .env
        :return:
        '''
        salt = os.urandom(16)
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
            backend=default_backend()
        )
        key = base64.urlsafe_b64encode(kdf.derive(self.password))
        return key

    def make_token(self, message):
        token = self.f.encrypt(message.encode('utf-8'))
        return token.decode('utf-8')

    def decode_token(self, token):
        msg = self.f.decrypt(token.encode('utf-8'))
        return msg.decode('utf-8')
