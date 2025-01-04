from sentence_transformers import SentenceTransformer
from sklearn.cluster import AffinityPropagation
import pandas as pd

class Library:
    def __init__(self, canon):
        self.canon = canon
        self.model = SentenceTransformer("all-MiniLM-L6-v2")
        self.aff_prop = AffinityPropagation()
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

    def genres(self):
        book_embeddings = self.metadata['embed'].tolist()
        clusters = self.aff_prop.fit_predict(book_embeddings)
        self.metadata['genre'] = clusters

        print(self.metadata.sort_values('genre'))
