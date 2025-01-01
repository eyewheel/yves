import requests
import json
import sys
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
import atexit

from read_openlib import *

# def save():
 #   Book.save()

# remembering the library...
# atexit.register(save)

import_catalog(sys.argv[1])
print(Book.canon)
