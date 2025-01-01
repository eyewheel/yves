from sklearn.cluster import KMeans
import pandas as pd
import numpy as np

from read_openlib import Book

def genres():
    book_embeddings = Book.canon['embed'].tolist()
    kmeans = KMeans(n_clusters = 4)
    clusters = kmeans.fit_predict(book_embeddings)
    Book.canon['genre'] = clusters

    print(Book.canon.sort_values('genre'))
