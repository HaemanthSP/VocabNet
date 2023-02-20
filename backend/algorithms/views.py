import os
import sys
import json
import base64
import urllib
from rest_framework import status
from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.generics import ListCreateAPIView

import vocabby.utils as ut
from vocabby.learner import Learner
from vocabby.bookshelf import Bookshelf, Book


class PostText(APIView):
    def post(self, req):
        if not json.loads(req.body)['file'] == []:
            try:
                text = base64.b64decode(json.loads(req.body)['file']['base64'].split(",")[1]).decode('utf8')
            except UnicodeDecodeError:
                text = base64.b64decode(json.loads(req.body)['file']['base64'].split(",")[1]).decode('windows-1252')

        else:
                text = ""
        username = json.loads(req.body)['user']
        author = json.loads(req.body)['author']
        book_name = json.loads(req.body)['bookname']
        genre = json.loads(req.body)['genre']
        year = json.loads(req.body)['year']
        publisher = json.loads(req.body)['publisher']
        book_shelf = Bookshelf.load('Library')
        book_code = book_shelf.add_book(
                text, book_name, author, genre, year, publisher)
        new_book = Book.load(book_code)
        learner = Learner(username)
        learner.add_book(new_book)

        data = {'username': username,
                'bookCode': book_code,
                'stats': new_book.get_stats()}
        learner.save()
        book_shelf.save()
        return Response(data=data, status=status.HTTP_200_OK)


class AddNewBook(APIView):
    def post(self, req):

        file = urllib.request.urlopen(json.loads(req.body)["text_url"])
        try:
            text = file.read().decode('utf8')
        except UnicodeDecodeError:
            text = file.read().decode('windows-1252')

        # username = json.loads(req.body)['user']
        author = json.loads(req.body)['author']
        book_name = json.loads(req.body)['title']
        cover_img_url = json.loads(req.body)['cover_image_url']

        book_shelf = Bookshelf.load('Library')
        book_code = book_shelf.add_book(text, book_name, author, cover_img_url)
        new_book = Book.load(book_code)
        learner = Learner("Kavin")
        learner.add_book(new_book)

        data = {
                'bookCode': book_code,
                'stats': new_book.get_stats()}
        learner.save()
        book_shelf.save()
        return Response(data=data, status=status.HTTP_200_OK)


class SessionStart(APIView):
    def post(self, req):
        print("-------------------------------------")
        print(json.loads(req.body))
        username = json.loads(req.body)['username']
        book_code = json.loads(req.body)['bookCode']
        learner = Learner.load(username)
        tutor = learner.get_tutor(book_code)
        session = tutor.get_session()
        print (session.tokens.keys())
        neighbourhood, neighbourhoodwc = Book.get_graph_for_viz(book_code=book_code)
        data = {'username': username,
                'bookCode': book_code,
                'words': list(session.tokens.keys()),
                'stats': Book.load(book_code).get_stats(),
                'neighbours': neighbourhood,
                'neighboursWc': neighbourhoodwc,
                'progress': tutor.progress,
                'wordNeighbors': session.candidate_neighbours()}
        learner.save()
        return Response(data=data, status=status.HTTP_200_OK)


class GetBooks(APIView):
        def post(self, req):
            book_shelf = Bookshelf.load('Library')
            # data = {"books": book_shelf.get_index()}
            data = book_shelf.get_index()
            return Response(data=data, status=status.HTTP_200_OK)


class GetLevel(APIView):
    def post(self, req):
        username = json.loads(req.body)['username']
        learner = Learner.load(username)
        data = {'level': learner.difficulty_level}
        return Response(data=data, status=status.HTTP_200_OK)


class PostLevel(APIView):
    def post(self, req):
        username = json.loads(req.body)['username']
        level = json.loads(req.body)['level']
        learner = Learner.load(username)
        learner.difficulty_level = level
        learner.save()
        return Response(status=status.HTTP_200_OK)


class GetActivity(APIView):
    def post(self, req):
        username = json.loads(req.body)['username']
        book_code = json.loads(req.body)['bookCode']
        learner = Learner.load(username)
        tutor = learner.get_tutor(book_code)
        session = tutor.get_session()
        data = {'username': username,
                'bookCode': book_code,
                'activity': session.next_acitivity(),
                'progress': (len(session.tokens) - len(session.queue)) * 100 / len(session.tokens)}
        learner.save()
        return Response(data=data, status=status.HTTP_200_OK)


class PostActivity(APIView):
    def post(self, req):
        username = json.loads(req.body)['username']
        book_code = json.loads(req.body)['bookCode']
        activity_id = int(json.loads(req.body)['activityId'])
        selection = int(json.loads(req.body)['selection'])
        learner = Learner.load(username)
        tutor = learner.get_tutor(book_code)
        session = tutor.get_session()
        data = {'username': username,
                'bookCode': book_code,
                'result': session.evaluate(activity_id, selection)}
        learner.save()
        return Response(data=data, status=status.HTTP_200_OK)


class DictionaryLookUp(APIView):
    def post(self, req):
        username = json.loads(req.body)['username']
        word = json.loads(req.body)['word']
        data = {'username': username,
                'dictionary': ut.dictionary_lookup(word)}

        print("Output of Dict look up %s" % (data))
        return Response(data=data, status=status.HTTP_200_OK)