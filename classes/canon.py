import requests
import json
from tqdm import tqdm

base_url = "https://openlibrary.org/search.json?title={}&author={}"

# The Book and Canon classes only deal with metadata representations which
# are persisted in database files

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
            # temporarily using key as unique id
            # 'key', # openlibrary attempts to make this work-unique, but many dups exist
            ]

    def __init__(self, canonical_title, canonical_author):
        self.canonical_title = canonical_title
        self.canonical_author = canonical_author
        self.possible_docs = []
        self.canonical_doc = None
        # have we selected a canonical metadata representation?
        self.canon = False

    def add_possible(self, doc):
        self.possible_docs.append(doc)

    def choose_doc(self):
        if len(self.possible_docs) == 0:
            return False
        for doc in self.possible_docs:
            for key in self.openlibrary_discard_keys:
                doc.pop(key, None)
        # eventually we'll actually concatenate the docs / select the one with
        # the most information - picking a random one is temp stopgap
        self.canonical_doc = self.possible_docs[0]
        self.canonical_doc['canonical_title'] = self.canonical_title
        self.canonical_doc['canonical_author'] = self.canonical_author
        self.canon = True
        return True

    def __str__(self):
        if self.canon:
            return f"{self.canonical_title} by {self.canonical_author}"
        else:
            return f"{self.canonical_title} - {len(self.possible_docs)} possible versions"

class Canon:
    def __init__(self, db):
        self.list = []
        with open(db) as f:
            text = f.read()
            if text.strip():
                self.list = json.loads(text)

    def add_catalog(self, source):
        # should add duplicate protection
        
        with open(source) as f:
            lines = f.read().splitlines()

        for line in tqdm(lines, "importing catalog"):
            line = line.strip()
            if line:
                title, author = line.split("%%")
                self.add_book(title, author)

    def add_book(self, title, author):
        book = Book(title, author)
        escaped_title = title.replace(' ', '+')
        escaped_author = author.replace(' ', '+')
        url = base_url.format(escaped_title, escaped_author)
        response = requests.get(url)
        if response.text and response.text.strip():
            data = json.loads(response.text)
            # print(f"looking for {title} by {author} - {len(data['docs'])} possible copies")
            for doc in data['docs']:
                if 'title' in doc:
                    book.add_possible(doc)
            if book.choose_doc():
                self.list.append(book.canonical_doc)

    def save(self, db):
        with open(db, 'w') as f:
            f.write(json.dumps(self.list, indent=4))
