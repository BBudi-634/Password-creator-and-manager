from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import base64 # convert binary data to plain text
import os

class PasswordEncryptor:
    def __init__(self, master_password, salt = None): # salt = random data added to a password before encryption
        self.salt = salt if salt else os.urandom(16)
        self.key = self._derive_key(master_password)
        self.cipher = Fernet(self.key)

    def _derive_key(self, master_password): # get master password and salt
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=self.salt,
            iterations=100000,  # Slows down brute-force
        )
        key = base64.urlsafe_b64encode(kdf.derive(master_password.encode()))
        return key

    def encrypt(self, plaintext):
        return self.cipher.encrypt(plaintext.encode()).decode()

    def decrypt(self, encrypted_text):
        return self.cipher.decrypt(encrypted_text.encode()).decode()

    def get_salt(self):
        return self.salt


'''
def write_key():
    key = Fernet.generate_key()
    with open("secret.key", "wb") as key_file: # wb = write binary
        key_file.write(key) # save to key file, or if not available, will make one.

#uncomment to generate new key
#write_key()

def load_key():
    return open("secret.key", "rb").read() # rb = read binary

def encrypt_file(filename):
    key = load_key()
    fernet = Fernet(key) # creates fernet obj with key
    with open(filename, "rb") as file: # read the data
        original_data = file.read() # stored as original data
    encrypted_data = fernet.encrypt(original_data) # encrypt file
    with open(filename, "wb") as file:
        file.write(encrypted_data) #rewrite with encrypted data


#uncomment to encrypt
#encrypt_file("SECRETS.TXT")

def decrypt_file(filename):
    key = load_key() # load key
    fernet = Fernet(key) # create fernet obj with key
    with open(filename, "rb") as file: # open file
        encrypted_data = file.read() # read file
    decrypted_data = fernet.decrypt(encrypted_data) # decrypt
    with open(filename, "wb") as file:
        file.write(decrypted_data) # overwrite file with decrypted key

decrypt_file("SECRETS.TXT")
'''