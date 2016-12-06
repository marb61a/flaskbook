from application import create_app as create_app_base
from mongoengine.connection import _get_db
import unittest

from user.models import User

class UserTest(unittest.TestCase):
    def create_app(self):
        self.db_name = 'flaskbook_test'
        return create_app_base(
            MONGODB_SETTINGS={'DB': self.db_name},
            TESTING=True,
            WTF_CSRF_ENABLED=False,
            SECRET_KEY=''
            )
            
    def setUp(self):
        self.app_factory = self.create_app()
        self.app = self.app_factory.test_client()

    def tearDown(self):
        db = _get_db()
        db.client.drop_database(db)
        
    def user_dict(self):
        return dict(
            first_name="joe",
            last_name="bloggs",
            username="joebloggs",
            email="joebloggs@example.com",
            password="abcd1234",
            confirm="abcd1234"
            )
        
    def test_register_user(self):
        # basic registration
        rv = self.app.post('/register', data=self.user_dict(), follow_redirects=True)
        assert User.objects.filter(username="joebloggs").count() == 1
        
        # Invalid username characters
        user2 = self.user_dict()
        user2['username'] = "test test"
        user2['email'] = "test@example.com"
        rv = self.app.post('/register', data=user2, follow_redirects=True)
        assert "Invalid username" in str(rv.data)
        
        # Is username being saved in lowercase?
        user3 = self.user_dict()
        user2['username'] = "TestUser"
        user2['email'] = "test2@example.com"
        rv = self.app.post('/register', data=user3, follow_redirects=True)
        assert User.objects.filter(username=user3['username'].lower()).count() == 1
        
        # Confirm the user
        user = User.objects.get(username=self.user_dict()['username'])
        code = user.change_configuration.get('confirmation_code')
        rv = self.app.get('/confirm/' + user.username + '/' + code)
        assert "Your email has been confirmed" in str(rv.data)
        
        # Try again to confirm
        rv = self.app.get('/confirm/' + user.username + '/' + code)
        assert rv.status_code == 404
        
        # Check change configuration is empty
        user = User.objects.get(username=self.user_dict()['username'])
        assert user.change_configuration == {}
        
        
    def test_login_user(self):
        # create user
        self.app.post('/register', data = self.user_dict())
        # login user
        rv = self.app.post('/login', data=dict(
            username=self.user_dict()['username'],
            password=self.user_dict()['password']
            ))
        # check the session is set
        with self.app as c:
                rv = c.get('/')
                assert session.get('username') == self.user_dict()['username']
                
    def test_edit_profile(self):
        # create user
        self.app.post('/register', data = self.user_dict())
        # login user
        rv = self.app.post('/login', data=dict(
            username=self.user_dict()['username'],
            password=self.user_dict()['password']
            ))
        # check user has edit button on their own profile
        rv = self.app.get('/', self.user_dict()['username'])
        assert "Edit profile" in str(rv.data)
        
        # edit fields
        user = self.user_dict()
        user['first_name'] = "Test First"
        user['last_name'] = "Test Last"
        user['username'] = "TestUsername"
        user['email'] = "Test@Example.com"
        
        # edit user
        rv = self.app.post('/edit', data=user)
        assert "Profile updated" in str(rv.data)
        edited_user = User.objects.first()
        assert edited_user.first_name == "Test First"
        assert edited_user.last_name == "Test Last"
        assert edited_user.username == "testusername"
        assert edited_user.email == "test@example.com"
        
        # Check new mail is in the change configuration
        user['email'] = "test@example.com"
        rv = self.app.post('/edit', data=user)
        assert "You will need to confirm the new email to complete this change" in str(rv.data)
        db_user = User.objects.first()
        code = db_user.change_configuration.get('confirmation_code')
        new_email = db_user.change_configuration.get('new_email')
        assert new_email == user['email']
        
        # create a second user
        self.app.post('/register', data = self.user_dict())
        # login user
        rv = self.app.post('/login', data=dict(
            username=self.user_dict()['username'],
            password=self.user_dict()['password']
            ))
            
        # try to save same email address
        user = self.user_dict()
        user['email'] = "test@example.com"
        rv = self.app.post('/edit', data=user)
        assert "Email already exists" in str(rv.data)
        
        # try to save same username
        user = self.user_dict()
        user['username'] = "TestUsername"
        rv = self.app.post('/edit', data=user)
        assert "Username already exists" in str(rv.data)
        
        
        
        