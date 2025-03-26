from django.contrib.auth import get_user_model
from rest_framework import serializers

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'phone_number', 'username', 'is_active')


class RegisterSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('phone_number', 'username')

    def create(self, validated_data):
        return User.objects.create(**validated_data)


class LoginSerializer(serializers.Serializer):
    phone_number = serializers.CharField()

    def validate(self, data):
        phone_number = data.get('phone_number')
        user = User.objects.filter(phone_number=phone_number).first()

        if user is None:
            raise serializers.ValidationError("Foydalanuvchi topilmadi.")
        if not user.is_active:
            raise serializers.ValidationError("Foydalanuvchi hali tasdiqlanmagan.")

        data['user'] = user
        return data