import requests
import json
import sys
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
import atexit

from read_openlib import *

def save():
    Book.save()

# remembering the library...
atexit.register(save)

if len(sys.argv) > 1:
    import_catalog(sys.argv[1])
else:
    Book.load()

print(json.dumps(Book.canon, indent=4))
