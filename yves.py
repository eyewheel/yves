import sys

from classes.canon import Canon
from classes.library import Library

canon = Canon('db.json')

if len(sys.argv) > 1:
    canon.add_catalog(sys.argv[1])

canon.save('db.json')

library = Library(canon)
# library.calculate_genres()

while True:
    query = input('> ')
    library.browse(query)
