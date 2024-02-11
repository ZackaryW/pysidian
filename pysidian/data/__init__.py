import os
data_mod = os.path.dirname(os.path.realpath(__file__))

def getFile(filename : str):
    return os.path.join(data_mod, filename)
