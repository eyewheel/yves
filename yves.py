import requests
import json
import sys

base_url = "https://openlibrary.org/search.json?title={}&author={}"

class Book:
    def __init__(self, canonical_title, canonical_author):
        self.canonical_title = canonical_title
        self.canonical_author = canonical_author
        self.raw_reps = []

    def add_possible(self, doc):
        self.raw_reps.append(doc)

    def validate_possibles(self):
        print("about to validate...")


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
