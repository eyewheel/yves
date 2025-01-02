from sklearn.cluster import AffinityPropagation
import pandas as pd
import numpy as np

from read_openlib import Book

def genres():
    book_embeddings = Book.canon['embed'].tolist()
    aff_prop = AffinityPropagation()
    clusters = aff_prop.fit_predict(book_embeddings)
    Book.canon['genre'] = clusters

    print(Book.canon.sort_values('genre'))
