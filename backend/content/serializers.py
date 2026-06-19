from rest_framework import serializers

from base.serializers import (
    AuthorMixin,
    UserInteractionMixin,
    CategorySerializer,
    SubcategorySerializer,
    TagSerializer,
)
from base.models import Category, Subcategory, Tag
from .models import Content


class ContentListSerializer(
    AuthorMixin, UserInteractionMixin, serializers.ModelSerializer
):
    """Compact serializer for lists, cards, and search results."""

    category = CategorySerializer(read_only=True)
    subcategory = SubcategorySerializer(read_only=True)

    class Meta:
        model = Content
        fields = (
            "public_id",
            "type",
            "title",
            "slug",
            "body",
            "featured_image",
            "youtube_url",
            "duration_seconds",
            "source_attribution",
            "category",
            "subcategory",
            "author",
            "is_saved",
            "is_completed",
            "saves_count",
            "completions_count",
            "is_published",
            "publish_at",
            "created_at",
        )
        read_only_fields = fields


class ContentDetailSerializer(
    AuthorMixin, UserInteractionMixin, serializers.ModelSerializer
):
    """Full serializer for detail pages."""

    category = CategorySerializer(read_only=True)
    subcategory = SubcategorySerializer(read_only=True)
    tags = TagSerializer(many=True, read_only=True)

    class Meta:
        model = Content
        fields = (
            "public_id",
            "type",
            "title",
            "slug",
            "body",
            "featured_image",
            "youtube_url",
            "audio_file",
            "duration_seconds",
            "document",
            "original_text",
            "translated_text",
            "source_attribution",
            "category",
            "subcategory",
            "tags",
            "author",
            "is_saved",
            "is_completed",
            "saves_count",
            "completions_count",
            "is_published",
            "publish_at",
            "is_archived",
            "created_at",
            "updated_at",
        )
        read_only_fields = ("public_id", "slug", "author", "created_at", "updated_at")


class ContentWriteSerializer(serializers.ModelSerializer):
    """Create / update. Validates required media fields per type."""

    category = serializers.SlugRelatedField(
        slug_field="slug",
        queryset=Category.objects.all(),
        required=False,
        allow_null=True,
    )
    subcategory = serializers.SlugRelatedField(
        slug_field="slug",
        queryset=Subcategory.objects.all(),
        required=False,
        allow_null=True,
    )
    tags = serializers.SlugRelatedField(
        slug_field="slug",
        queryset=Tag.objects.all(),
        many=True,
        required=False,
    )
    # Write-only flag to clear an existing featured image on update. A DRF
    # ImageField rejects an empty string, so an explicit flag is the clean way
    # to express "remove the current image" over multipart.
    remove_featured_image = serializers.BooleanField(
        write_only=True,
        required=False,
        default=False,
    )

    class Meta:
        model = Content
        fields = (
            "type",
            "title",
            "body",
            "featured_image",
            "remove_featured_image",
            "youtube_url",
            "audio_file",
            "duration_seconds",
            "document",
            "original_text",
            "translated_text",
            "source_attribution",
            "category",
            "subcategory",
            "tags",
            "is_published",
            "publish_at",
            "is_archived",
        )

    def create(self, validated_data):
        validated_data.pop("remove_featured_image", None)
        return super().create(validated_data)

    def update(self, instance, validated_data):
        remove_image = validated_data.pop("remove_featured_image", False)
        # An explicit removal only applies when no replacement file was sent.
        if remove_image and "featured_image" not in validated_data:
            instance.featured_image.delete(save=False)
            validated_data["featured_image"] = None
        return super().update(instance, validated_data)

    def validate(self, data):
        t = data.get("type") or getattr(self.instance, "type", None)
        if (
            t == Content.VIDEO
            and not data.get("youtube_url")
            and not getattr(self.instance, "youtube_url", None)
        ):
            raise serializers.ValidationError(
                {"youtube_url": "Required for video content."}
            )
        if (
            t == Content.AUDIO
            and not data.get("audio_file")
            and not getattr(self.instance, "audio_file", None)
        ):
            raise serializers.ValidationError(
                {"audio_file": "Required for audio content."}
            )

        category = data.get("category") or getattr(self.instance, "category", None)
        subcategory = data.get("subcategory")
        if subcategory is not None:
            if category is None:
                raise serializers.ValidationError(
                    {"subcategory": "A category is required when a subcategory is set."}
                )
            if subcategory.category_id != category.id:
                raise serializers.ValidationError(
                    {
                        "subcategory": "Subcategory does not belong to the selected category."
                    }
                )
        return data
