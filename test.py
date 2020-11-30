from cryptography.fernet import Fernet # pip install cryptography
import os
import json

#encoding stuff
def generate_key():
    key = Fernet.generate_key() # make the key
    with open("secret.txt", "wb+") as key_file:
        key_file.write(key)

def load_key():
    return open("secret.txt", "rb").read()

def encrypt_message(message):
    key = load_key()
    encoded_message = message.encode()
    f = Fernet(key)
    encrypted_message = f.encrypt(encoded_message)

    print(encrypted_message)
    return encrypted_message

def decrypt_message(encrypted_message):
    """
    Decrypts an encrypted message
    """
    key = load_key()
    f = Fernet(key)
    decrypted_message = f.decrypt(encrypted_message)

    print(decrypted_message.decode('utf-8'))

if __name__ == "__main__":
    #generate_key()
    #encrypted_message = encrypt_message("hi")
    #print(encrypted_message)
    #decrypt_message(encrypted_message)

    #putting the encrypted message here. 
    decrypt_message(b'gAAAAABfxJpWSYNUtAPOoXqpi6Tl_Ai9ZfEaETTvniNWS1VTM3Jtyt_uWQfGQeAgKiARpPz4_bIsbz46OfuLkgdTGHr1qyWRGA==')

    #next_message = input("Try: ")
    #encrypt_message(next_message)