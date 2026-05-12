import string
import secrets


def generate_token(length=16):
    alphabet = string.ascii_letters + string.digits + "!@#$%^&*()_-+=[]{}"
    token = ''.join(secrets.choice(alphabet) for _ in range(length))
    return token


def convert_to_octets(key):

    octets = []
    num_octets = len(key) // 8

    for i in range(num_octets):
        start = i * 8
        end = start + 8
        octet = key[start:end]
        octets.append(int(octet, 2))

    return bytearray(octets)