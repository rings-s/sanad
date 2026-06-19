import logging

from django.contrib.auth import get_user_model
from rest_framework import serializers

from .models import UserProfile

logger = logging.getLogger(__name__)

User = get_user_model()


class RegisterSerializer(serializers.Serializer):
    email = serializers.EmailField()
    username = serializers.CharField(max_length=150)
    password = serializers.CharField(write_only=True, min_length=8)

    def validate_email(self, value):
        return value.lower()

    def validate_username(self, value):
        if User.objects.filter(username=value).exists():
            raise serializers.ValidationError('This username is already taken.')
        return value

    def validate_email_unique(self, value):
        if User.objects.filter(email=value.lower()).exists():
            raise serializers.ValidationError('An account with this email already exists.')
        return value

    def validate(self, data):
        email = data.get('email', '').lower()
        if User.objects.filter(email=email).exists():
            raise serializers.ValidationError({'email': 'An account with this email already exists.'})
        return data


class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = ('avatar', 'bio', 'nationality', 'is_email_verified')
        read_only_fields = ('is_email_verified',)


class UserSerializer(serializers.ModelSerializer):
    profile = serializers.SerializerMethodField()
    is_sheikh = serializers.BooleanField(read_only=True)
    is_content_creator = serializers.BooleanField(read_only=True)

    class Meta:
        model = User
        fields = (
            'public_id', 'email', 'username', 'role',
            'is_sheikh', 'is_content_creator', 'date_joined', 'profile',
        )
        read_only_fields = (
            'public_id', 'email', 'role',
            'is_sheikh', 'is_content_creator', 'date_joined',
        )

    def get_profile(self, obj) -> dict:
        try:
            profile = obj.profile
        except UserProfile.DoesNotExist:
            profile = UserProfile.objects.create(user=obj)
            logger.warning('Created missing UserProfile for user %s on demand.', obj.pk)
        # Propagate request context so the avatar FileField renders an absolute URL
        # (e.g. http://host/media/...) — without it the frontend resolves the
        # relative /media path against its own origin and the image 404s.
        return UserProfileSerializer(profile, context=self.context).data


class MeUpdateSerializer(serializers.ModelSerializer):
    profile = UserProfileSerializer()

    class Meta:
        model = User
        fields = ('username', 'profile')

    def update(self, instance, validated_data):
        profile_data = validated_data.pop('profile', {})

        if 'username' in validated_data:
            instance.username = validated_data['username']
            instance.save(update_fields=['username'])

        profile, _ = UserProfile.objects.get_or_create(user=instance)
        changed_fields = []
        for attr, value in profile_data.items():
            if getattr(profile, attr) != value:
                setattr(profile, attr, value)
                changed_fields.append(attr)
        if changed_fields:
            profile.save(update_fields=changed_fields)

        return instance
