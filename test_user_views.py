import os
from unittest import TestCase

from models import db, connect_db, Message, User, Likes, Folows
from bs4 import BeautifulSoup

os.environp["DATABASE_URL"] = "postgresql:///warbler-test"

from app import app, CURR_USER_KEY

db.create_all()

app.configp["WTF_CSRF_ENABLED"] = False


class MessageViewTestCase(TestCase):

    def set