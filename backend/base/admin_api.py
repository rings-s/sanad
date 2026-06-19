"""
base/admin_api.py — in-app admin CRUD for the Sheikh (taxonomy + daily guidance).

This is the application's own admin surface (exposed under /api/v1/admin/ and
driven by the Studio UI). It is deliberately separate from Django's built-in
admin site (base/admin.py), which is left untouched. Every endpoint here is
gated by IsSheikh.
"""
from rest_framework import serializers
from rest_framework.generics import ListCreateAPIView, RetrieveUpdateDestroyAPIView
from rest_framework.views import APIView

from accounts.permissions import IsSheikh
from base.pagination import StandardPagination
from base.responses import SuccessResponseMixin
from content.models import Content
from content.serializers import ContentListSerializer
from .models import Category, Subcategory, Tag, DailyGuidance, Comment
from .serializers import CategoryTreeSerializer, display_name


# ── Write serializers ─────────────────────────────────────────────────────────

class CategoryWriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ('slug', 'name', 'icon')
        read_only_fields = ('slug',)


class SubcategoryWriteSerializer(serializers.ModelSerializer):
    category = serializers.SlugRelatedField(slug_field='slug', queryset=Category.objects.all())

    class Meta:
        model = Subcategory
        fields = ('slug', 'name', 'category')
        read_only_fields = ('slug',)


class TagWriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ('slug', 'name')
        read_only_fields = ('slug',)


class DailyGuidanceSerializer(serializers.ModelSerializer):
    """Items are addressed by Content public_id on write; hydrated on read."""
    items = serializers.SlugRelatedField(
        slug_field='public_id', queryset=Content.objects.all(), many=True, required=False,
    )
    items_detail = ContentListSerializer(source='items', many=True, read_only=True)

    class Meta:
        model = DailyGuidance
        fields = ('public_id', 'date', 'items', 'items_detail', 'created_at')
        read_only_fields = ('public_id', 'items_detail', 'created_at')


def _bust_daily_cache(date) -> None:
    from django.core.cache import cache
    cache.delete(f'sanad:daily:{date}')


# ── Categories ────────────────────────────────────────────────────────────────

class CategoryAdminListCreateView(SuccessResponseMixin, ListCreateAPIView):
    permission_classes = (IsSheikh,)
    queryset = Category.objects.prefetch_related('subcategories').all()

    def get_serializer_class(self):
        return CategoryTreeSerializer if self.request.method == 'GET' else CategoryWriteSerializer

    def get_read_serializer_class(self):
        return CategoryTreeSerializer


class CategoryAdminDetailView(SuccessResponseMixin, RetrieveUpdateDestroyAPIView):
    permission_classes = (IsSheikh,)
    queryset = Category.objects.prefetch_related('subcategories').all()
    serializer_class = CategoryWriteSerializer
    lookup_field = 'slug'

    def get_read_serializer_class(self):
        return CategoryTreeSerializer


# ── Subcategories ─────────────────────────────────────────────────────────────

class SubcategoryAdminListCreateView(SuccessResponseMixin, ListCreateAPIView):
    permission_classes = (IsSheikh,)
    serializer_class = SubcategoryWriteSerializer

    def get_queryset(self):
        qs = Subcategory.objects.select_related('category').all()
        category = self.request.query_params.get('category')
        return qs.filter(category__slug=category) if category else qs


class SubcategoryAdminDetailView(SuccessResponseMixin, RetrieveUpdateDestroyAPIView):
    permission_classes = (IsSheikh,)
    queryset = Subcategory.objects.select_related('category').all()
    serializer_class = SubcategoryWriteSerializer
    lookup_field = 'slug'


# ── Tags ──────────────────────────────────────────────────────────────────────

class TagAdminListCreateView(SuccessResponseMixin, ListCreateAPIView):
    permission_classes = (IsSheikh,)
    queryset = Tag.objects.all()
    serializer_class = TagWriteSerializer


class TagAdminDetailView(SuccessResponseMixin, RetrieveUpdateDestroyAPIView):
    permission_classes = (IsSheikh,)
    queryset = Tag.objects.all()
    serializer_class = TagWriteSerializer
    lookup_field = 'slug'


# ── Daily guidance ────────────────────────────────────────────────────────────

class DailyGuidanceAdminListCreateView(SuccessResponseMixin, ListCreateAPIView):
    permission_classes = (IsSheikh,)
    queryset = DailyGuidance.objects.prefetch_related('items__author', 'items__category').all()
    serializer_class = DailyGuidanceSerializer

    def perform_create(self, serializer):
        instance = serializer.save()
        _bust_daily_cache(instance.date)


class DailyGuidanceAdminDetailView(SuccessResponseMixin, RetrieveUpdateDestroyAPIView):
    permission_classes = (IsSheikh,)
    queryset = DailyGuidance.objects.prefetch_related('items__author', 'items__category').all()
    serializer_class = DailyGuidanceSerializer
    lookup_field = 'public_id'

    def perform_update(self, serializer):
        instance = serializer.save()
        _bust_daily_cache(instance.date)

    def perform_destroy(self, instance):
        date = instance.date
        instance.delete()
        _bust_daily_cache(date)


# ── Comments (full moderation list — any status) ──────────────────────────────

class AdminCommentSerializer(serializers.ModelSerializer):
    user = serializers.SerializerMethodField()
    content = serializers.SerializerMethodField()

    class Meta:
        model = Comment
        fields = ('public_id', 'user', 'content', 'text', 'status', 'created_at')
        read_only_fields = fields

    def get_user(self, obj) -> dict:
        return {'name': display_name(obj.user), 'username': obj.user.username}

    def get_content(self, obj) -> dict:
        return {'public_id': str(obj.content.public_id), 'title': obj.content.title}


class AdminCommentListView(APIView):
    """Every comment (any status) for the Sheikh moderation table. Actions reuse
    the existing approve / reject / delete comment endpoints."""
    permission_classes = (IsSheikh,)

    def get(self, request):
        qs = Comment.objects.select_related('user', 'content').order_by('-created_at')
        status_filter = request.query_params.get('status', '').strip()
        if status_filter:
            qs = qs.filter(status=status_filter)
        paginator = StandardPagination()
        page = paginator.paginate_queryset(qs, request)
        return paginator.get_paginated_response(AdminCommentSerializer(page, many=True).data)
