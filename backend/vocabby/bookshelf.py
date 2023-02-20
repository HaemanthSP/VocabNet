"""
Module to prepare and maintain book for vocabulary learning.

:author: Haemanth Santhi Ponnusamy <haemanthsp@gmail.com>
"""
import os
import pickle
from random import randint
import sys
sys.setrecursionlimit(10000)

from vocabby.vocab_builder import Vocab


class Book:
    """Prepare a book for reading."""

    def __init__(self, text, title, author, cover_img_url, topic, code):
        self.text = text
        self.title = title
        self.author = author
        self.topic = topic
        self.cover_img_url = cover_img_url
        # self.year = year
        # self.publisher = publisher
        self.code = code

        # Internal
        self.vocab = Vocab(text)
        self.words = self.vocab.words
        self.families = self.vocab.families
        self.network = self.vocab.network

    def get_stats(self):
        """Get the statistics on vocabulary of the book."""
        stats = self.vocab.stats()
        return stats

    @staticmethod
    def load(book_code):
        """Loads the processed book from shelf."""
        with open('data/books/' + book_code + '.p', 'rb') as book_file:
            book = pickle.load(book_file)
        return book

    @staticmethod
    def get_graph_for_viz(book_code):
        """Loads the processed book from shelf."""

        book = Book.load(book_code)

        # Building the entire graph for visualization
        node_list = {name: idx for idx, name in enumerate(book.network.nodes)}
        sorted_node_list = sorted(node_list.items(), key=lambda x: x[1])
        print(sorted_node_list[:5])
        nodes = [{'id': node_list[token],
                  'name': token,
                  'score': book.network.node[token]['mastery'],
                  'child': False}
                 for token, _ in sorted_node_list]
        print('Node list:', nodes[:5])
        edges = []
        for source, target, attrb in book.network.edges.data():
            if attrb['weight'] < 0.6:
                continue
            edges.append({"source": node_list[source],
                          "target": node_list[target],
                          "weight": attrb['weight']})

        children = []
        child_edges = []
        families = {}
        for parent in nodes:
            families[parent['id']] = set()
            family = book.families.get(parent['name'], {})
            if not family:
                print("No family for ", parent['name'])
                print(parent)
                break
            for child in family.members:
                child_pos = len(nodes) + len(children)
                children.append({'id': child_pos,
                                 'name': child.text + "_" + child.pos,
                                 'score': parent['score'],
                                 'child': True})
                child_edges.append({"source": parent['id'],
                                    "target": child_pos,
                                    "weight": 1})
                families[parent['id']].add(child_pos)

        neighbourhood = {"nodes": nodes + children, "links": edges + child_edges, "families": families}
        neighbourhoodwc = {"nodes": nodes, "links": edges, "families": families}
        print("Graph details: nodes: %s, edges: %s, families: %s" % (len(nodes), len(edges), len(families)))
        return neighbourhood, neighbourhoodwc

    def save(self):
        """Save the book for future use."""
        with open('data/books/' + self.code + '.p', 'wb') as book_file:
            pickle.dump(self, book_file)


class Bookshelf:
    """Organizes book for future learners to fetch."""

    def __init__(self, name):
        self.name = name
        self.books = {}

    def add_book(self, text, title, author, cover_img_url, topic="Fiction", year="2000", publisher="ABC"):
        """Add a new book to the shelf."""
        code = self._generate_code(title, author, year)

        matching_code = self.find_book(
                title, author, topic, year, publisher)
        if matching_code:
            return matching_code

        self.books.update(
            {code: {'title': title,
                    'author': author,
                    'cover_img_url': cover_img_url,
                    'gener': topic,
                    'year': year,
                    'publisher': publisher}})
        book = Book(text, title, author, cover_img_url, topic, code)
        book.save()
        return code

    def remove_book(self, code):
        # Remove the book from the index
        self.books.pop(code)

        # Remove the book file from the storage space
        os.remove('data/books/' + code + '.p')

    def _generate_code(self, title, author, year):
        """Generate a unique code for the book."""
        samples = [self.name[:4], title[:5], author[:5],
                   year[:4], str(randint(0, 9999))]

        return '_'.join(samples)

    def find_book(self, title, author, gener, year, publisher):
        """Find whether a book exists in the shelf."""
        # raise NotImplementedError
        for code, attrb in self.books.items():
            if attrb['title'] == title and \
               attrb['author'] == author and \
               attrb['gener'] == gener and \
               attrb['year'] == year:
                return code
        return None

    def get_book(self, book_code):
        """Get the book corresponding to the code."""
        return Book.load(book_code)

    def get_index(self):
        """Get details of all book in this shelf"""
        index = []
        for code, book in self.books.items():
            book.update({'code': code})
            index.append(book)
        return index

    @staticmethod
    def load(shelf_name):
        """Loads the processed book from shelf."""
        shelf_file = 'data/books/' + shelf_name + '.p'
        if os.path.isfile(shelf_file):
            with open(shelf_file, 'rb') as shelf_file:
                shelf = pickle.load(shelf_file)
        else:
            shelf = Bookshelf(shelf_name)
        return shelf

    def save(self):
        """Save the book for future use."""
        shelf_file = 'data/books/' + self.name + '.p'
        with open(shelf_file, 'wb') as shelf_file:
            pickle.dump(self, shelf_file)
