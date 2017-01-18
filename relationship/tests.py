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
            
    def test_friends_operations(self):
        # Register users
        rv = self.app.post('/register', data=self.user1_dict(), follow_redirects=True)
        assert User.objects.filter(username=self.user1_dict()['username']).count() == 1
        rv = self.app.post('/register', data=self.user2_dict(), follow_redirects=True)
        assert User.objects.filter(username=self.user2_dict()['username']).count() == 1
        
        # Login the first user
        rv = self.app.post('/login', data=dict(
            username=self.user1_dict()['username'],
            password=self.user1_dict()['password']
            ))
        
        # Add the second user as a friend
        rv = self.app.get('/add_friend/' + self.user2_dict()['username'], follow_redirects=True)
        assert "relationship-friends-requested" in str(rv.data)
        
        # Check that only one record exists at this point
        relcount = Relationship.objects.count()
        assert relcount == 1
        
        # Login the second user
        rv = self.app.post('/login', data=dict(
            username=self.user2_dict()['username'],
            password=self.user2_dict()['password']
            ))
        
        # Check that a friend request is pending
        rv = self.app.get('/' + self.user1_dict()['username'])
        assert "relationship-reverse-friends-requested" in str(rv.data)
        
        # Confirm first user as a friend
        rv = self.app.get('/add_friend/' + self.user1_dict()['username'], follow_redirects=True)
        assert "relationship-friends" in str(rv.data)
        
        # Check that two records exist at this point
        relcount = Relationship.objects.count()
        assert relcount == 2
        
        # User2 unfriends User1
        rv = self.app.get('/remove_friend/' + self.user1_dict()['username'], follow_redirects=True)
        assert "relationship-add-friend" in str(rv.data)
        
        # Check that no records exist at this point
        relcount = Relationship.objects.count()
        assert relcount == 0
        
        # Login the first user
        rv = self.app.post('/login', data=dict(
            username=self.user1_dict()['username'],
            password=self.user1_dict()['password']
            ))
        
        # Check no longer friends
        rv = self.app.get('/' + self.user2_dict()['username'])
        assert "relationship-add-friend" in str(rv.data)
    
    def test_block_operations(self):
        # Register users
        rv = self.app.post('/register', data=self.user1_dict(), follow_redirects=True)
        assert User.objects.filter(username=self.user1_dict()['username']).count() == 1
        rv = self.app.post('/register', data=self.user2_dict(), follow_redirects=True)
        assert User.objects.filter(username=self.user2_dict()['username']).count() == 1
        
        # Login the first user
        rv = self.app.post('/block/', data=dict(
            username=self.user1_dict()['username'],
            password=self.user1_dict()['password']
            ))
        
        # User1 blocks User2
        rv = self.app.get('/remove_friend/' + self.user2_dict()['username'], follow_redirects=True)
        assert "relationship-blocked" in str(rv.data)
        
        # Login the second user
        rv = self.app.post('/login', data=dict(
            username=self.user2_dict()['username'],
            password=self.user2_dict()['password']
            ))
        
        # Check user1 profile reflects being blocked
        rv = self.app.get('/' + self.user1_dict()['username'])
        assert "relationship-reverse-blocked" in str(rv.data)
        
        # Try become friends with User1
        rv = self.app.get('/add_friend/' + self.user1_dict()['username'], follow_redirects=True)
        assert "relationship-reverse-blocked" in str(rv.data)
        
        # Login the first user
        rv = self.app.post('/block/', data=dict(
            username=self.user1_dict()['username'],
            password=self.user1_dict()['password']
            ))
        
        # User1 unblocks User2
        rv = self.app.get('/unblock/' + self.user2_dict()['username'], follow_redirects=True)
        assert "relationship-add-friend" in str(rv.data)