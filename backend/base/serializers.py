from rest_framework import serializers

from .models import Category, Subcategory, Tag, SavedItem, Comment


def display_name(user) -> str:
    """
    Human-friendly name for bylines. Prefers the real full name and falls back
    to the username handle — so SSO accounts whose handle is a slug (e.g.
    'ahmed-bashir') still render as 'Ahmed Bashir'. Decouples *what is shown*
    from the unique handle.
    """
    if user is None:
        return ''
    full = f'{user.first_name} {user.last_name}'.strip()
    return full or user.username


class AuthorMixin(serializers.Serializer):
    author = serializers.SerializerMethodField()

    def get_author(self, obj) -> dict:
        author = getattr(obj, 'author', None)
        if author is None:
            return None
        return {
            'name': display_name(author),
            'username': author.username,
            'public_id': str(author.public_id),
            'role': author.role,
        }


class UserInteractionMixin(serializers.Serializer):
    """
    Adds is_saved, is_completed, saves_count, completions_count to content
    serializers. All four read from queryset annotations set by
    annotate_engagement() — zero extra queries per list item.
    """
    is_saved = serializers.SerializerMethodField()
    is_completed = serializers.SerializerMethodField()
    saves_count = serializers.SerializerMethodField()
    completions_count = serializers.SerializerMethodField()

    def get_is_saved(self, obj) -> bool:
        v = getattr(obj, '_is_saved', None)
        if v is not None:
            return bool(v)
        request = self.context.get('request')
        if not request or not request.user.is_authenticated:
            return False
        from .models import SavedItem
        return SavedItem.objects.filter(user=request.user, content=obj).exists()

    def get_is_completed(self, obj) -> bool:
        v = getattr(obj, '_is_completed', None)
        if v is not None:
            return bool(v)
        request = self.context.get('request')
        if not request or not request.user.is_authenticated:
            return False
        from .models import ContentProgress
        return ContentProgress.objects.filter(user=request.user, content=obj).exists()

    def get_saves_count(self, obj) -> int:
        v = getattr(obj, '_saves_count', None)
        return v if v is not None else obj.saves.count()

    def get_completions_count(self, obj) -> int:
        v = getattr(obj, '_completions_count', None)
        return v if v is not None else obj.completions.count()


# Keep SavedStateMixin as an alias so any leftover references don't break.
SavedStateMixin = UserInteractionMixin


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ('slug', 'name', 'icon')
        read_only_fields = fields


class SubcategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Subcategory
        fields = ('slug', 'name')
        read_only_fields = fields


class CategoryTreeSerializer(CategorySerializer):
    """Category + its subcategories. Used only by the category list endpoint."""
    subcategories = SubcategorySerializer(many=True, read_only=True)

    class Meta(CategorySerializer.Meta):
        fields = CategorySerializer.Meta.fields + ('subcategories',)


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ('slug', 'name')
        read_only_fields = fields


class CommentSerializer(serializers.ModelSerializer):
    user = serializers.SerializerMethodField()

    class Meta:
        model = Comment
        fields = ('public_id', 'user', 'text', 'status', 'created_at')
        read_only_fields = fields

    def get_user(self, obj) -> dict:
        return {
            'name': display_name(obj.user),
            'username': obj.user.username,
            'public_id': str(obj.user.public_id),
        }


class CommentCreateSerializer(serializers.Serializer):
    content_id = serializers.UUIDField()
    text = serializers.CharField(max_length=1000, allow_blank=False)


class SavedItemCreateSerializer(serializers.Serializer):
    content_id = serializers.UUIDField()


class SavedItemSerializer(serializers.ModelSerializer):
    """Hydrated saved item — embeds the content summary."""
    content = serializers.SerializerMethodField()

    class Meta:
        model = SavedItem
        fields = ('public_id', 'content', 'created_at')
        read_only_fields = fields

    def get_content(self, obj):
        from content.serializers import ContentListSerializer
        return ContentListSerializer(obj.content, context=self.context).data
