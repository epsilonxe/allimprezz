import re


class PasswordValidator:
    MIN_LENGTH = 8

    @classmethod
    def validate(cls, password):
        errors = []
        if len(password) < cls.MIN_LENGTH:
            errors.append(f'Password must be at least {cls.MIN_LENGTH} characters long.')
        if not re.search(r'[A-Z]', password):
            errors.append('Password must contain at least one uppercase letter.')
        if not re.search(r'[a-z]', password):
            errors.append('Password must contain at least one lowercase letter.')
        if not re.search(r'\d', password):
            errors.append('Password must contain at least one digit.')
        if not re.search(r'[!@#$%^&*(),.?":{}|<>_\-+=\[\]\\\/~`]', password):
            errors.append('Password must contain at least one special character.')
        return errors

    @classmethod
    def is_strong(cls, password):
        return len(cls.validate(password)) == 0
