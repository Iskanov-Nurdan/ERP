from rest_framework import serializers
from django.contrib.auth import get_user_model, authenticate
from django.contrib.auth.password_validation import validate_password
from rest_framework.validators import UniqueValidator
from apps.accounts.models import Role
from rest_framework_simplejwt.tokens import RefreshToken

User = get_user_model()

class RoleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Role
        fields = ["id", "name", "description"]


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "username", "system_role", "role"]


class RegisterSerializer(serializers.ModelSerializer):
    password2 = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = [
            "id", "username", "email",
            "password", "password2",
            "system_role", "role"
        ]

    def validate(self, attrs):
        if attrs["password"] != attrs["password2"]:
            raise serializers.ValidationError("Пароли не совпадают")
        return attrs

    def validate_system_role(self, value):
        if value not in ["admin", "user"]:
            raise serializers.ValidationError(
                "Можно создать только admin или user. Owner создаётся только вручную."
            )
        return value

    def validate_role(self, value):
        if value and not Role.objects.filter(id=value.id).exists():
            raise serializers.ValidationError("Такой роли не существует")
        return value

    def create(self, validated_data):
        validated_data.pop("password2")
        return User.objects.create_user(**validated_data)


class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

    def validate(self, attrs):
        email = attrs.get("email")
        password = attrs.get("password")

        User = get_user_model()

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            raise serializers.ValidationError("Неверный email или пароль.")

        if not user.check_password(password):
            raise serializers.ValidationError("Неверный email или пароль.")

        attrs['user'] = user
        return attrs