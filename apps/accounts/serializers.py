from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password

from apps.accounts.models import Role

User = get_user_model()


class RoleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Role
        fields = ["id", "name", "description"]


class UserSerializer(serializers.ModelSerializer):
    role_name = serializers.CharField(source="role.name", read_only=True, allow_null=True)

    class Meta:
        model = User
        fields = ["id", "email", "username", "system_role", "role", "role_name"]
        read_only_fields = ["id"]


class UserUpdateSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=False, allow_blank=False)

    class Meta:
        model = User
        fields = ["email", "username", "system_role", "role", "password"]

    def validate_system_role(self, value):
        if value == "owner":
            raise serializers.ValidationError("Нельзя назначать owner через API.")
        return value

    def validate_password(self, value):
        validate_password(value)
        return value

    def update(self, instance, validated_data):
        password = validated_data.pop("password", None)

        for k, v in validated_data.items():
            setattr(instance, k, v)

        if password:
            instance.set_password(password)

        instance.save()
        return instance


class RegisterSerializer(serializers.ModelSerializer):
    password2 = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = [
            "id", "email", "username",
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
        email = attrs.get("email", "").strip().lower()
        password = attrs.get("password")

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            raise serializers.ValidationError("Неверный email или пароль.")

        if not user.check_password(password):
            raise serializers.ValidationError("Неверный email или пароль.")

        attrs["user"] = user
        return attrs
