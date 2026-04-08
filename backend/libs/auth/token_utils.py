from datetime import datetime, timezone


class TokenPayloadBuilder:
    REQUIRED_KEYS = {'user_id', 'email', 'role', 'iat'}

    @classmethod
    def build(cls, user_id, email, role):
        return {
            'user_id': user_id,
            'email': email,
            'role': role,
            'iat': int(datetime.now(timezone.utc).timestamp()),
        }

    @classmethod
    def is_valid(cls, payload):
        if not isinstance(payload, dict):
            return False
        if not cls.REQUIRED_KEYS.issubset(payload.keys()):
            return False
        from .roles import RoleManager
        return RoleManager.is_valid(payload.get('role', ''))
