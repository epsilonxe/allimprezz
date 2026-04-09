from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

from libs.auth.passwords import PasswordValidator
from libs.auth.roles import RoleManager
from libs.auth.token_utils import TokenPayloadBuilder

from .models import User


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        payload = TokenPayloadBuilder.build(user.id, user.email, user.role)
        token['email'] = payload['email']
        token['role'] = payload['role']
        token['full_name'] = user.full_name
        return token

    def validate(self, attrs):
        data = super().validate(attrs)
        data['user'] = {
            'id': self.user.id,
            'email': self.user.email,
            'first_name': self.user.first_name,
            'last_name': self.user.last_name,
            'role': self.user.role,
        }
        return data


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'email', 'first_name', 'last_name', 'role', 'is_active', 'date_joined']
        read_only_fields = ['id', 'date_joined']


class UserCreateSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    role = serializers.ChoiceField(choices=RoleManager.MANAGEABLE_CHOICES)

    class Meta:
        model = User
        fields = ['email', 'first_name', 'last_name', 'role', 'password']

    def validate_password(self, value):
        errors = PasswordValidator.validate(value)
        if errors:
            raise serializers.ValidationError(errors)
        return value

    def create(self, validated_data):
        return User.objects.create_user(**validated_data)


class ProfileUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['first_name', 'last_name']


class UserUpdateSerializer(serializers.ModelSerializer):
    role = serializers.ChoiceField(choices=RoleManager.MANAGEABLE_CHOICES)

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'role', 'is_active']


class PasswordChangeSerializer(serializers.Serializer):
    old_password = serializers.CharField(write_only=True)
    new_password = serializers.CharField(write_only=True)

    def validate_old_password(self, value):
        user = self.context['request'].user
        if not user.check_password(value):
            raise serializers.ValidationError('Current password is incorrect.')
        return value

    def validate_new_password(self, value):
        errors = PasswordValidator.validate(value)
        if errors:
            raise serializers.ValidationError(errors)
        return value
