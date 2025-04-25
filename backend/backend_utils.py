import hashlib


def generate_id(key: str | None = None, init: str | None = None, max_length: int = 32):
    # instantiates the sha object
    sha512 = hashlib.sha512(key.encode())
    sha512.update(init.encode())
    return sha512.hexdigest()[:max_length].zfill(max_length)
