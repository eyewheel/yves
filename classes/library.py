from sentence_transformers import SentenceTransformer
from sklearn.cluster import AffinityPropagation
from sklearn.neighbors import NearestNeighbors
import pandas as pd

class Library:
    def __init__(self, canon):
        self.canon = canon
        self.model = SentenceTransformer("all-MiniLM-L6-v2")
        self.aff_prop = AffinityPropagation()
        self.nn = NearestNeighbors(n_neighbors = 3)
        self.metadata = None
        self.embed_canon()

    def embed_canon(self):
        raw_embeds = []
        for book_doc in self.canon.list:
            if 'subject' in book_doc and len(book_doc['subject']) > 0:
                subject_str = ', '.join(book_doc['subject'])
                subject_embed = self.model.encode(subject_str)
                raw_embeds.append({'title': book_doc['canonical_title'], 'author': book_doc['canonical_author'], 'embed': subject_embed})

        self.metadata = pd.DataFrame(raw_embeds)

    def calculate_genres(self):
        book_embeddings = self.metadata['embed'].tolist()
        # todo: avoid unnecessary repeated fitting
        clusters = self.aff_prop.fit_predict(book_embeddings)
        self.metadata['genre'] = clusters

    def browse(self, query_str):
        book_embeddings = self.metadata['embed'].tolist()
        self.nn.fit(book_embeddings)

        query = self.model.encode(query_str).reshape(1, -1)
        distances, indices = self.nn.kneighbors(query)

        nearby = self.metadata['title'].iloc[indices.flatten()]
        for book in nearby:
            print(book)
