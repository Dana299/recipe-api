from dj_rest_auth.registration.serializers import RegisterSerializer
from dj_rest_auth.serializers import UserDetailsSerializer
from rest_framework import serializers


class CustomRegisterSerialiazer(RegisterSerializer):

    def save(self, request):
        user = super().save(request)
        user.is_active = True
        user.save()
        return user


class CustomUserDetailsSerializer(serializers.Serializer):
    """
    Login serializer.
    """
    user = serializers.SerializerMethodField()

    def get_user(self, obj):
        user_data = UserDetailsSerializer(obj['user'], context=self.context).data
        return user_data
