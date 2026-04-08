import unittest
from libs.auth.roles import RoleManager
from libs.auth.passwords import PasswordValidator
from libs.auth.token_utils import TokenPayloadBuilder


class TestRoleManager(unittest.TestCase):
    def test_valid_roles(self):
        self.assertTrue(RoleManager.is_valid('admin'))
        self.assertTrue(RoleManager.is_valid('staff'))
        self.assertTrue(RoleManager.is_valid('agent'))

    def test_invalid_role(self):
        self.assertFalse(RoleManager.is_valid('superuser'))
        self.assertFalse(RoleManager.is_valid(''))

    def test_choices_format(self):
        self.assertEqual(len(RoleManager.CHOICES), 3)
        self.assertIn(('admin', 'Admin'), RoleManager.CHOICES)

    def test_admin_has_all_privileges(self):
        self.assertTrue(RoleManager.has_privilege('admin', 'admin'))
        self.assertTrue(RoleManager.has_privilege('admin', 'staff'))
        self.assertTrue(RoleManager.has_privilege('admin', 'agent'))

    def test_staff_privileges(self):
        self.assertFalse(RoleManager.has_privilege('staff', 'admin'))
        self.assertTrue(RoleManager.has_privilege('staff', 'staff'))
        self.assertTrue(RoleManager.has_privilege('staff', 'agent'))

    def test_agent_privileges(self):
        self.assertFalse(RoleManager.has_privilege('agent', 'admin'))
        self.assertFalse(RoleManager.has_privilege('agent', 'staff'))
        self.assertTrue(RoleManager.has_privilege('agent', 'agent'))

    def test_invalid_role_has_no_privilege(self):
        self.assertFalse(RoleManager.has_privilege('unknown', 'agent'))
        self.assertFalse(RoleManager.has_privilege('admin', 'unknown'))


class TestPasswordValidator(unittest.TestCase):
    def test_valid_password(self):
        self.assertEqual(PasswordValidator.validate('MyP@ssw0rd'), [])
        self.assertTrue(PasswordValidator.is_strong('MyP@ssw0rd'))

    def test_too_short(self):
        errors = PasswordValidator.validate('Ab1!')
        self.assertTrue(any('at least 8' in e for e in errors))

    def test_no_uppercase(self):
        errors = PasswordValidator.validate('myp@ssw0rd')
        self.assertTrue(any('uppercase' in e for e in errors))

    def test_no_lowercase(self):
        errors = PasswordValidator.validate('MYP@SSW0RD')
        self.assertTrue(any('lowercase' in e for e in errors))

    def test_no_digit(self):
        errors = PasswordValidator.validate('MyP@ssword')
        self.assertTrue(any('digit' in e for e in errors))

    def test_no_special_char(self):
        errors = PasswordValidator.validate('MyPassw0rd')
        self.assertTrue(any('special' in e for e in errors))

    def test_multiple_violations(self):
        errors = PasswordValidator.validate('abc')
        self.assertGreater(len(errors), 1)

    def test_is_strong_false(self):
        self.assertFalse(PasswordValidator.is_strong('weak'))


class TestTokenPayloadBuilder(unittest.TestCase):
    def test_build_structure(self):
        payload = TokenPayloadBuilder.build(1, 'test@example.com', 'admin')
        self.assertEqual(payload['user_id'], 1)
        self.assertEqual(payload['email'], 'test@example.com')
        self.assertEqual(payload['role'], 'admin')
        self.assertIn('iat', payload)
        self.assertIsInstance(payload['iat'], int)

    def test_is_valid_correct_payload(self):
        payload = TokenPayloadBuilder.build(1, 'test@example.com', 'staff')
        self.assertTrue(TokenPayloadBuilder.is_valid(payload))

    def test_is_valid_missing_keys(self):
        self.assertFalse(TokenPayloadBuilder.is_valid({'user_id': 1}))

    def test_is_valid_invalid_role(self):
        payload = {'user_id': 1, 'email': 'a@b.com', 'role': 'hacker', 'iat': 123}
        self.assertFalse(TokenPayloadBuilder.is_valid(payload))

    def test_is_valid_not_dict(self):
        self.assertFalse(TokenPayloadBuilder.is_valid('not a dict'))
        self.assertFalse(TokenPayloadBuilder.is_valid(None))


if __name__ == '__main__':
    unittest.main()
