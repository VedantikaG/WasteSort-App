# serializers.py
from django.contrib.auth.hashers import make_password
from rest_framework import serializers
from .models import ScmsUser, ScmsComplaint


class ScmsUserSerializer(serializers.ModelSerializer):
    u_password = serializers.CharField(
        required=True,
        style={'input_type': 'password', 'placeholder': 'Password'}
    )

    class Meta:
        model = ScmsUser
        fields = '__all__'

    def create(self, validated_data):
        validated_data['u_password'] = make_password(validated_data['u_password'])
        return super().create(validated_data)

    def update(self, instance, validated_data):
        if 'u_password' in validated_data:
            validated_data['u_password'] = make_password(validated_data['u_password'])
        return super().update(instance, validated_data)



class ScmsComplaintSerializer(serializers.ModelSerializer):
    class Meta:
        model = ScmsComplaint
        fields = '__all__'
