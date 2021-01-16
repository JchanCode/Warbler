import os   
from unittest import TestCase
from sqlalchemy import exc
from models import db, User, Message, Follows, Likes


os.environ["DATABASE_URL"] = "postgresql:///warbler-test"

from app import app

db.create_all()


class UserModelTestCase(TestCase):
    """Test User Model"""

    def setUp(self):
        """Create test client, add sample data."""

        db.drop_all()
        db.create_all()

        self.uid = 1234
        u = User.signup("testing","test@test.com","password",None,None,None,None)
        u.id = self.uid
        db.session.commit()

        self.u = User.query.get(self.uid)

        self.client = app.test_client()

    def tearDown(self):
        res = super().tearDown()
        db.session.rollback()
        return res

    def test_message_model(self):

        m = Message(
            text = "a warble",
            user_id = self.uid
        )
        
        m.id = 12
        db.session.add(m)
        db.session.commit()
        
        msg = Message.query.all()

        self.assertEqual(len(self.u.messages),1)
        self.assertEqual(self.u.messages[0].id,12)
        self.assertEqual(len(msg),1)

    def test_message_likes(self):
        m1 = Message(
            text="testing",
            user_id=self.uid
        )

        m2 = Message(
            text="testing m2",
            user_id=self.uid
        )

        u = User.signup("Ny","a@email.com","password",None,None,None,None)
        uid = 888
        u.id = uid
        db.session.add_all([m1,m2,u])
        db.session.commit()

        u.likes.append(m1)
        db.session.commit()

        l = Likes.query.filter(Likes.user_id == uid).all()
        self.assertEqual(len(l),1)
        self.assertEqual(l[0].message_id, m1.id)