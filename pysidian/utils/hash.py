import hashlib

def hash_bytes(data : bytes):
    return hashlib.sha256(data).hexdigest()

def hash_file(path : str):
    hashed = None
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            if hashed is None:
                hashed = hashlib.sha256(chunk)
            else:
                hashed.update(chunk)

    return hashed.hexdigest()

def check_hash_bytes(data : bytes, hash : str):
    return hash_bytes(data) == hash

def check_hash_file(path : str, hash : str):
    return hash_file(path) == hash