"""User model tests."""

# run these tests like:
#
#    python -m unittest test_user_model.py


import os
from unittest import TestCase
from sqlalchemy import exc
from models import db, User, Message, Follows

# BEFORE we import our app, let's set an environmental variable
# to use a different database for tests (we need to do this
# before we import our app, since that will have already
# connected to the database

os.environ['DATABASE_URL'] = "postgresql:///warbler-test"


# Now we can import app

from app import app

# Create our tables (we do this here, so we only create the tables
# once for all tests --- in each test, we'll delete the data
# and create fresh new clean test data

db.create_all()


class UserModelTestCase(TestCase):
    """Test views for messages."""

    def setUp(self):
        """Create test client, add sample data."""

        db.drop_all()
        db.create_all()

        u1 = User.signup("test1","test1@email.com","password",None,None,None,None)
        uid1 = 111
        u1.id = uid1

        u2 = User.signup("test2","test2@email.com","password",None,None,None,None)
        uid2 = 222
        u2.id = uid2

        db.session.commit()

        self.u1 = u1
        self.uid1 = uid1
        self.u2 = u2
        self.uid2 = uid2

        self.client = app.test_client()

    def tearDown(self):
        """Clean up transaction."""
        res = super().tearDown()
        db.session.rollback()

        return res


    def test_user_model(self):
        """Does basic model work?"""

        u = User(
            email="test@test.com",
            username="testuser",
            password="HASHED_PASSWORD"
        )

        db.session.add(u)
        db.session.commit()

        # User should have no messages & no followers
        self.assertEqual(len(u.messages), 0)
        self.assertEqual(len(u.followers), 0)

    def test_user_repr(self):
        """__repr__ testing"""

        u = User(
            email="test@test.com",
            username="testuser",
            password="HASHED_PASSWORD"
        )

        db.session.add(u)
        db.session.commit()

        self.assertEqual(
            repr(u), f"<User #{u.id}: testuser, test@test.com>")

    
    def test_user_follows(self):
        """Test is this user following `other_use`?"""

        self.u1.following.append(self.u2)
        db.session.commit()

        self.assertEqual(len(self.u2.following),0)
        self.assertEqual(len(self.u2.followers),1)
        self.assertEqual(len(self.u1.followers),0)
        self.assertEqual(len(self.u1.following),1)

        self.assertEqual(self.u2.followers[0].id,self.u1.id)
        self.assertEqual(self.u1.following[0].id,self.u2.id)

    def test_is_following(self):
        self.u1.following.append(self.u2)
        db.session.commit()

        self.assertTrue(self.u1.is_following(self.u2))
        self.assertFalse(self.u2.is_following(self.u1))

    def test_is_followed_by(self):
        self.u1.following.append(self.u2)
        db.session.commit()

        self.assertFalse(self.u1.is_followed_by(self.u2))
        self.assertTrue(self.u2.is_followed_by(self.u1))

    def test_signup(self):
        tony = User.signup("tony", "tony@email.com", "password",
                           None, None, None, None)
        tid = 1234
        tony.id = tid
        db.session.commit()

        tony = User.query.get(tid)
        self.assertEqual(tony.username, "tony")
        self.assertNotEqual(tony.password,"password")
        self.assertTrue(tony.password.startswith("$2b$"))

    def test_invalid_username(self):
        invalid = User.signup(None,"test@test.com","password", None, None, None, None)
        uid = 1122
        invalid.id = uid
        with self.assertRaises(exc.IntegrityError) as context:  db.session.commit()

    def test_invalid_password_signup(self):
        with self.assertRaises(ValueError) as context: 
            User.signup("test","test@email.com","",None,None,None,None)

        with self.assertRaises(ValueError) as context:
            User.signup("test","test@email.com",None,None,None,None,None)

    def test_invalid_username_login(self):
        self.assertFalse(User.authenticate("badusername","password"))   

    def test_wrong_password(self):
        self.assertFalse(User.authenticate(self.u1.username,"badpassword"))