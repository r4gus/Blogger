import unittest
from app.models import User, Permission

class UserModelTestCase(unittest.TestCase):
    def test_password_verification(self):
        u = User()
        u.set_password('cat')
        self.assertTrue(u.check_password('cat'))
        self.assertFalse(u.check_password('dog'))

    def test_password_salts_are_random(self):
        u = User()
        u2 = User()
        u.set_password('cat')
        u2.set_password('cat')
        self.assertTrue(u.password_hash != u2.password_hash)

