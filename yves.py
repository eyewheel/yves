import requests
import json
import sys

base_url = "https://openlibrary.org/search.json?title="

class Book:
    def __init__(self, canonical_title):
        self.canonical_title = canonical_title
        self.raw_reps = []

    def add_possible(self, doc):
        self.raw_reps.append(doc)

    def __str__(self):
        return f"{self.canonical_title} - {len(self.raw_reps)} possible versions"

def import_catalog(file):
    with open(file, 'r') as f:
        lines = f.read().splitlines()

    for line in lines:
        line = line.strip()
        if line:
            import_book(line)

def import_book(title):
    book = Book(title)
    escaped_title = title.replace(' ', '+')
    url = base_url + escaped_title
    response = requests.get(url)
    data = json.loads(response.text)
    for doc in data['docs']:
        if 'title' in doc:
            book.add_possible(doc)

    print(book)
    
import_catalog(sys.argv[1])
