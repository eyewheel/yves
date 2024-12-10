import requests
import json
import sys

base_url = "https://openlibrary.org/search.json?title={}&author={}"

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
            'subject', # always duplicates subject_key, which formats more canonically
            'key', # openlibrary attempts to make this work-unique, but many dups exist
            ]
    def __init__(self, canonical_title, canonical_author):
        self.canonical_title = canonical_title
        self.canonical_author = canonical_author
        self.raw_reps = []
        self.canonical_doc = None

    def add_possible(self, doc):
        self.raw_reps.append(doc)

    def validate_possibles(self):
        if len(self.raw_reps) == 0:
            return
        for doc in self.raw_reps:
            for key in self.openlibrary_discard_keys:
                doc.pop(key, None)
        self.canonical_doc = self.raw_reps[0] 

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
    print(url)
    response = requests.get(url)
    data = json.loads(response.text)
    for doc in data['docs']:
        if 'title' in doc:
            book.add_possible(doc)
    book.validate_possibles()

    print(book)
    
import_catalog(sys.argv[1])
