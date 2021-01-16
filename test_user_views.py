import os
from unittest import TestCase

from models import db, connect_db, Message, User, Likes, Follows
from bs4 import BeautifulSoup

os.environ["DATABASE_URL"] = "postgresql:///warbler-test"

from app import app, CURR_USER_KEY

db.create_all()

app.config["WTF_CSRF_ENABLED"] = False


class MessageViewTestCase(TestCase):

    def setUp(self):

        db.drop_all()
        db.create_all()

        self.client = app.test_client()

        self.testuser = User.signup(username="testuser",
                                    email="test@test.com",
                                    password="testuser",
                                    image_url=None,
                                    bio=None,
                                    header_image_url= None,
                                    location=None)
        self.testuser_id = 8989
        self.testuser.id = self.testuser_id

        self.u1 = User.signup("abc", "test1@test.com", "password", None,None,None,None)
        self.u1_id = 778
        self.u1.id = self.u1_id
        self.u2 = User.signup("efg", "test2@test.com", "password", None,None,None,None)
        self.u2_id = 884
        self.u2.id = self.u2_id
        self.u3 = User.signup("hij", "test3@test.com", "password", None,None,None,None)
        self.u4 = User.signup("testing", "test4@test.com", "password", None,None,None,None)

        db.session.commit()

    def tearDown(self):
        resp = super().tearDown()
        db.session.rollback()
        return resp

    def test_users_index(self):
        with self.client as c:
            resp = c.get("/users")
            html = resp.get_data(as_text=True)

            self.assertIn("@abc",html)
            self.assertIn("@testuser", html)
            self.assertIn("@testing",html)

    def test_users_query(self):
        """ Testing users view query"""
        with self.client as c:
            resp = c.get("/users?q=test")
            html = resp.get_data(as_text=True)

            self.assertIn("@testing", html)
            self.assertIn("@testuser", html)

            self.assertNotIn("@abc", html)
            self.assertNotIn("@efg", html)

    def test_user_show(self):
        with self.client as c:
            resp = c.get(f"/users/{self.u1.id}")
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code,200)
            self.assertIn("@abc", html)

    def setup_likes(self):
        m1 = Message(text="trending warble", user_id=self.testuser_id)
        m2 = Message(text="Eating some lunch", user_id=self.testuser_id)
        m3 = Message(id=9876, text="likable warble", user_id=self.u1_id)
        db.session.add_all([m1, m2, m3])
        db.session.commit()

        l1 = Likes(user_id=self.testuser_id, message_id=9876)

        db.session.add(l1)
        db.session.commit()

    def test_user_show_with_likes(self):
        self.setup_likes()

        with self.client as c:
            resp = c.get(f"/users/{self.testuser_id}")

            self.assertEqual(resp.status_code, 200)

            self.assertIn("@testuser", str(resp.data))
            soup = BeautifulSoup(str(resp.data), 'html.parser')
            found = soup.find_all("li", {"class": "stat"})
            self.assertEqual(len(found), 4)

    def test_add_like(self):
        m = Message(id=1984, text="The earth is round", user_id=self.u1_id)
        db.session.add(m)
        db.session.commit()

        with self.client as c:
            with c.session_transaction() as session:
                session[CURR_USER_KEY] = self.testuser_id

            resp = c.post("/users/add_like/1984", follow_redirects=True)

            self.assertEqual(resp.status_code, 200)

            html = resp.get_data(as_text=True)
            likes = Likes.query.filter(Likes.message_id==1984).all()
            
            self.assertEqual(len(likes),1)
            self.assertEqual(likes[0].user_id, self.testuser_id)

    