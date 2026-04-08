class RoleManager:
    ADMIN = 'admin'
    STAFF = 'staff'
    AGENT = 'agent'

    VALID_ROLES = (ADMIN, STAFF, AGENT)
    CHOICES = [(role, role.capitalize()) for role in VALID_ROLES]

    _HIERARCHY = {
        ADMIN: 2,
        STAFF: 1,
        AGENT: 0,
    }

    @classmethod
    def is_valid(cls, role):
        return role in cls.VALID_ROLES

    @classmethod
    def has_privilege(cls, user_role, required_role):
        if not cls.is_valid(user_role) or not cls.is_valid(required_role):
            return False
        return cls._HIERARCHY[user_role] >= cls._HIERARCHY[required_role]
