from rest_framework import serializers
from . models import employee
from django.utils.encoding import smart_str, force_bytes, DjangoUnicodeDecodeError
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from .utils import Util

class UserRegistrationSerializer(serializers.ModelSerializer):
    confirm_password = serializers.CharField(style={'input_type':'password'}, write_only=True)
    class Meta:
        model = employee
        fields = '__all__'
        extra_kwarg={
            'password':{'write_only':True}
        }

    def validate(self, attrs):
        password = attrs.get('password')
        confirm_password= attrs.get('confirm_password')
        if password !=confirm_password:
            raise serializers.ValidationError("password does not match")
        return attrs

    def create(self, validated_data):
        return employee.objects.create_user(**validated_data)

class UserLoginSerializer(serializers.ModelSerializer):
    email = serializers.CharField(max_length=255)
    password = serializers.CharField(max_length=150)
    class Meta:
        model = employee
        fields = ['email', 'password']
class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = employee
        fields = ['id', 'username', 'full_name', 'email']

class UserPasswordResetSerializer(serializers.ModelSerializer):
    password = serializers.CharField(max_length=150, style={'input_type':'password'}, write_only=True)
    confirm_password = serializers.CharField(max_length=150, style={'input_type':'password'}, write_only=True)

    class Meta:
        model = employee
        fields = ['password', 'confirm_password']

    def validate(self, attrs):
        password = attrs.get('password')
        confirm_password = attrs.get('confirm_password')
        user = self.context.get('user')
        if password != confirm_password:
            raise serializers.ValidationError('Password and Confirm Password does not match')
        user.set_password(password)
        user.save()
        return attrs

class SendPasswordResetEmailSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(max_length=255)

    class Meta:
        model = employee
        fields = ['email']

    def validate(self, attrs):
        email = attrs.get('email')
        if employee.objects.filter(email=email).exists():
            user = employee.objects.get(email=email)
            uid = urlsafe_base64_encode(force_bytes(str(user.id)))
            print('Encoded UID', uid)
            token = PasswordResetTokenGenerator().make_token(user)
            print('password reset token',token)
            link = 'https://localhost:3000/api/user/reset/'+uid+'/'+token
            print('password reset link', link)
            body = 'Click the following link to reset your Password ' +link
            data = {
                'subject':'Reset your password',
                'body':body,
                'to_email':user.email
            }
            Util.send_email(data)
            return attrs
        else:
            raise serializers.ValidationError('This email id is not registered, Please Register yourself')

class UserPasswordChangeSerializer(serializers.ModelSerializer):
    password = serializers.CharField(max_length=150, style={'input_type': 'password'}, write_only=True)
    confirm_password = serializers.CharField(max_length=150, style={'input_type': 'password'}, write_only=True)

    class Meta:
        model = employee
        fields = ['password', 'confirm_password']

    def validate(self, attrs):
        password = attrs.get('password')
        confirm_password = attrs.get('confirm_password')
        uid = self.context.get('uid')
        token = self.context.get('token')
        if password != confirm_password:
            raise serializers.ValidationError('Password and Confirm Password do not match')
        try:
            id = smart_str(urlsafe_base64_decode(uid))
            user = employee.objects.get(id=id)
        except (TypeError, ValueError, employee.DoesNotExist):
            raise serializers.ValidationError('Invalid user or user not found')
        if not PasswordResetTokenGenerator().check_token(user, token):
            raise serializers.ValidationError('Token is invalid or expired')
        user.set_password(password)
        user.save()
        return attrs