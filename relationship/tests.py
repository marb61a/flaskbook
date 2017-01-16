from application import create_app as create_app_base
from mongoengine.connection import _get_db
import unittest
from flask import session

from user.models import User
from relationship.models import Relationship

class RelationshipTest(unittest.TestCase):
    def create_app(self):
        self.db_name = 'flaskbook_test'
        return create_app_base(
            MONGODB_SETTINGS={'DB': self.db_name},
            TESTING=True,
            WTF_CSRF_ENABLED=False,
            SECRET_KEY='mySecret!'    
        )
    
    def setup(self):
        self.app_factory = self.create_app()
        self.app = self.app_factory.test_client()
        
    def tearDown(self):
        db = _get_db()
        db.client.drop_database(db)
    
    def user1_dict(self):
        return dict(
            first_name="joe",
            last_name="bloggs",
            username="joebloggs",
            email="joebloggs@example.com",
            password="abcd1234",
            confirm="abcd1234"
            )
    
    def user2_dict(self):
        return dict(
            first_name="jim",
            last_name="beam",
            username="jimbeam",
            email="jimbeam@example.com",
            password="abcd1234",
            confirm="abcd1234"
            )