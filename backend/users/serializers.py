from rest_framework import serializers
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

User = get_user_model()


class RegisterSerializer(serializers.ModelSerializer):
    """Kayıt serializer — email/password/username alır, email asla döndürülmez."""
    password = serializers.CharField(write_only=True, min_length=8)

    class Meta:
        model = User
        fields = ('username', 'email', 'password')
        extra_kwargs = {
            'email': {'write_only': True},  # email response'a asla girmez
        }

    def create(self, validated_data):
        user = User.objects.create_user(
            email=validated_data['email'],
            username=validated_data['username'],
            password=validated_data['password'],
        )
        return user


class PublicUserSerializer(serializers.ModelSerializer):
    """Sadece username döner — email ve diğer hassas alanlar hiç yoktur."""
    class Meta:
        model = User
        fields = ('id', 'username')


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    """Login sonrası token + kullanıcı adı döner, email dönmez."""

    def validate(self, attrs):
        data = super().validate(attrs)
        data['username'] = self.user.username
        return data
