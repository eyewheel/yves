import requests
import json
import sys
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
from collections import OrderedDict
import jsonpickle

base_url = "https://openlibrary.org/search.json?title={}&author={}"
model = SentenceTransformer("all-MiniLM-L6-v2")

books = []

class Book:
    """
    we only care about metadata that helps us identify the book more
    precisely (across all editions of the same work, translations perhaps
    excluded) and about somewhat canonical, library-normalized subject
    descriptors such as categorization numbers (which eventually we may
    move past anyway)
    """
    openlibrary_discard_keys = [
            'cover_edition_key',
            'cover_i',
            'ebook_access',
            'ebook_count_i',
            'edition_count',
            'edition_key',
            'has_fulltext',
            'last_modified_i',
            'number_of_pages_median',
            'public_scan_b',
            'seed',
            'id_goodreads',
            'id_librarything',
            'readinglog_count',
            'want_to_read_count',
            'currently_reading_count',
            'format',
            'type',
            'ratings_count_1',
            'ratings_count_2',
            'ratings_count_3',
            'ratings_count_4',
            'ratings_count_5',
            'ratings_count',
            'ratings_average',
            'ratings_sortable',
            'already_read_count',
            'lending_edition_s',
            'lending_identifier_s',
            'ia_collection',
            'ia_collection_s',
            'ia',
            '_version_',
            'printdisabled_s',
            'subject_key',
            'key', # openlibrary attempts to make this work-unique, but many dups exist
            ]
    def __init__(self, canonical_title, canonical_author):
        self.canonical_title = canonical_title
        self.canonical_author = canonical_author
        self.raw_reps = []
        self.canonical_doc = None
        self.subject_str = None
        self.subject_embed = None

    def add_possible(self, doc):
        self.raw_reps.append(doc)

    def validate_possibles(self):
        if len(self.raw_reps) == 0:
            return
        for doc in self.raw_reps:
            for key in self.openlibrary_discard_keys:
                doc.pop(key, None)
        # eventually we'll actually concatenate the docs / select the one with
        # the most information - picking a random one is temp stopgap 
        self.canonical_doc = self.raw_reps[0] 

        if 'subject' in self.canonical_doc:
            self.subject_str = ", ".join(self.canonical_doc['subject'])
        # print(self.subject_str)
        if self.subject_str:
            # scikit-learn expects 2d arrays
            self.subject_embed = model.encode(self.subject_str).reshape(1, -1)

    def __str__(self):
        return f"{self.canonical_title} - {len(self.raw_reps)} possible versions"

def import_catalog(file):
    with open(file, 'r') as f:
        lines = f.read().splitlines()

    for line in lines:
        line = line.strip()
        if line:
            title, author = line.split("%%")
            import_book(title, author)

def import_book(title, author):
    book = Book(title, author)
    escaped_title = title.replace(' ', '+')
    escaped_author = author.replace(' ', '+')
    url = base_url.format(escaped_title, escaped_author)
    response = requests.get(url)
    data = json.loads(response.text)
    for doc in data['docs']:
        if 'title' in doc:
            book.add_possible(doc)
    book.validate_possibles()
    if book.subject_embed is not None:
        books.append(book)

    print(book)

def similarity(query_embed, book_embed):
    return cosine_similarity(query_embed, book_embed)

def search(query):
    query_embed = model.encode(query).reshape(1, -1)
    indexed = OrderedDict()
    for book in sorted(books, key=lambda book: similarity(query_embed, book.subject_embed), reverse=True):
        indexed[book] = similarity(query_embed, book.subject_embed)
    return indexed

def browse_library():
    print("Welcome to the Infinite Library.")
    while True:
        query = input("What do you seek? ")
        if query == 'quit':
            with open('db.json', 'w') as file:
                file.write(jsonpickle.encode(books))
            quit()

        results = search(query)
        for idx, (book, similarity) in enumerate(results.items()):
            if idx == 0:
                print(f"You see a copy of {book.canonical_title}.")
                print(similarity)
            elif idx < 4:
                print(f"Nearby you see a copy of {book.canonical_title}.")
                print(similarity)

def load_library(file):
    with open(file) as f:
        decode = jsonpickle.decode(f.read())
    return decode

# import_catalog(sys.argv[1])
books = load_library('db.json')

browse_library()
