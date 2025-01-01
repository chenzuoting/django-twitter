from django.contrib.auth.models import User
from rest_framework import serializers, exceptions

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('username', 'email')


class UserSerializerForTweet(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'username')


class SignupSerializer(serializers.ModelSerializer):
    username = serializers.CharField(max_length=20, min_length=6)
    password = serializers.CharField(max_length=20, min_length=6)
    email = serializers.EmailField()

    class Meta:
        # Define the model and field for serializer.save()
        model = User
        fields = ('username', 'email', 'password')

    # Will be called when is_valid() si called
    def validate(self, data):
        # TODO<HOMEWORK> Adding check that username contains required set of characters
        if User.objects.filter(username=data['username'].lower()).exists():
            raise exceptions.ValidationError({
                'message': 'This username has been occupied.'
            })
        if User.objects.filter(email=data['email'].lower()).exists():
            raise exceptions.ValidationError({
                'message': 'This email address has been occupied.'
            })
        return data

    def create(self, validated_data):
        username = validated_data['username'].lower()
        email = validated_data['email'].lower()
        password = validated_data['password']
        # Use create_user() instead of create()
        # because create_user() contains set_password() to encrypt password
        user = User.objects.create_user(
            username=username,
            email=email,
            password=password,
        )
        return user


class LoginSerializer(serializers.Serializer):
    # Set checking rules for username and password field
    username = serializers.CharField()
    password = serializers.CharField()