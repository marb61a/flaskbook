from application import create_app as create_app_base
from mongoengine.connection import _get_db
import unittest
from flask import session

from user.models import User
from relationship.models import Relationship

class FeedTest(unittest.TestCase):
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
    
    def user3_dict(self):
        return dict(
            first_name="jack",
            last_name="black",
            username="joebloggs",
            email="jackblack@example.com",
            password="abcd1234",
            confirm="abcd1234"
            )
    
    def test_feed_posts(self):
        # Register the first user
        rv = self.app.post('/register', data = self.user1_dict(), follow_redirects = True)
        
        # Login the first user
        rv = self.app.post('/login', data=dict(
            username = self.user1_dict()['username'],
            password = self.user1_dict()['password']
            ))
        
        # Post a message
        rv = self.app.post('/message/add', data = dict(
            post="Test Post #1 User 1",
            to_user = self.user1_dict()['username']
            ), follow_redirects = True)
        assert "Test Post #1 User 1" in str(rv.data)
        
        # Register second user 
        rv = self.app.post('/register', data=self.user2_dict(), follow_redirects = True)
        
        # Make friends with user2
        rv = self.app.get('/add_friend/' + self.user2_dict()['username'], follow_redirects = True)
        
        # Login user2 and confirm user1 as friend
        rv = self.app.post('/login', data=dict(
            username = self.user2_dict()['username'],
            password = self.user2_dict()['password']
            ))
        rv = self.app.get('/add_friend/' + self.user1_dict()['username'], follow_redirects = True)
        
        # Login the first user again
        rv = self.app.post('/login', data=dict(
            username = self.user1_dict()['username'],
            password = self.user1_dict()['password']
            ))
        
        # Post a message
        rv = self.app.post('/message/add', data = dict(
            post = "Test Post #2 User 1",
            to_user = self.user1_dict()['username']
            ), follow_redirects = True)
        assert "Test Post #2 User 1" in str(rv.data)
        
        # Post a message to user 2
        rv = self.app.post('/message/add', data=dict(
            post="Test Post User 1 to User 2",
            to_user = self.user1_dict()['username']
            ), follow_redirects = True)
        
        # Login user2 
        rv = self.app.post('/login', data = dict(
            username = self.user2_dict()['username'],
            password = self.user2_dict()['password']
            ))
        rv = self.app.get('/')
        assert "Test Post #2 User 1" in str(rv.data)
        assert "Test Post User 1 to User 2" in str(rv.data)
        
        # Register third user 
        rv = self.app.post('/register', data=self.user3_dict(), follow_redirects = True)
        
        # Make friends with User2
        rv = self.app.get('/add_friend/' + self.user2_dict()['username'], follow_redirects = True)
        
        # Login the first user 
        rv = self.app.post('/login', data=dict(
            username = self.user1_dict()['username'],
            password = self.user1_dict()['password']
            ))
        
        # Block User3
        rv = self.app.get('/block/' + self.user3_dict()['username'], follow_redirects = True)
        
        # Login user2 
        rv = self.app.post('/login', data = dict(
            username = self.user2_dict()['username'],
            password = self.user2_dict()['password']
            ))
        
        # User2 confirm friend User3
        rv = self.app.get('/add_friend/' + self.user3_dict()['username'], follow_redirects = True)
        
        # Post a message to User3
        rv = self.app.post('/message/add', data=dict(
            post="Test Post User 2 to User 3",
            to_user = self.user3_dict()['username']
            ), follow_redirects = True)
        
        # Login the first user 
        rv = self.app.post('/login', data=dict(
            username = self.user1_dict()['username'],
            password = self.user1_dict()['password']
            ))
        
        # Check User1 doesn't see User2's post to User3 (blocked)
        rv = self.app.get('/')
        assert "Test Post User 2 to User 3" not in str(rv.data)