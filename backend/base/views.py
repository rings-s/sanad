from drf_spectacular.utils import extend_schema, OpenApiParameter
from rest_framework import status
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from accounts.permissions import IsContentCreator
from base.responses import success
from .models import Category, Tag, SavedItem, Comment, ContentProgress
from .pagination import StandardPagination
from . import services as base_services
from .serializers import (
    CategorySerializer, CategoryTreeSerializer, TagSerializer,
    SavedItemSerializer, SavedItemCreateSerializer,
    CommentSerializer, CommentCreateSerializer,
)
from content.serializers import ContentListSerializer


# ── Taxonomy ──────────────────────────────────────────────────────────────────>

@extend_schema(tags=['library'])
class CategoryListView(APIView):
    permission_classes = (AllowAny,)

    @extend_schema(summary='List all categories', responses={200: CategoryTreeSerializer(many=True)})
    def get(self, request):
        # Nest subcategories so the client can render the category → subcategory
        # filter cascade in one round-trip. prefetch avoids the N+1.
        qs = Category.objects.prefetch_related('subcategories').all()
        return success(CategoryTreeSerializer(qs, many=True).data)


@extend_schema(tags=['library'])
class CategoryDetailView(APIView):
    permission_classes = (AllowAny,)

    @extend_schema(summary='Content by category')
    def get(self, request, slug):
        try:
            category = Category.objects.get(slug=slug)
        except Category.DoesNotExist:
            return Response(
                {'success': False, 'error': {'code': 'NOT_FOUND', 'message': 'Category not found.'}},
                status=status.HTTP_404_NOT_FOUND,
            )
        from content.models import Content
        from base.utils import published_q
        qs = (
            Content.objects.filter(published_q(), category=category)
            .select_related('author', 'category')
            .order_by('-created_at')[:20]
        )
        return success({
            'category': CategorySerializer(category).data,
            'content': ContentListSerializer(qs, many=True, context={'request': request}).data,
        })


@extend_schema(tags=['library'])
class TagListView(APIView):
    permission_classes = (AllowAny,)

    @extend_schema(summary='List all tags', responses={200: TagSerializer(many=True)})
    def get(self, request):
        return success(TagSerializer(Tag.objects.all(), many=True).data)


# ── Saves (Favorites) ─────────────────────────────────────────────────────────

@extend_schema(tags=['saves'])
class SavedItemListView(APIView):
    permission_classes = (IsAuthenticated,)

    @extend_schema(summary='List my saved content')
    def get(self, request):
        items = (
            SavedItem.objects.filter(user=request.user)
            .select_related('content__author', 'content__category')
            .order_by('-created_at')
        )
        paginator = StandardPagination()
        page = paginator.paginate_queryset(items, request)
        return paginator.get_paginated_response(
            SavedItemSerializer(page, many=True, context={'request': request}).data
        )

    @extend_schema(summary='Save a content item', request=SavedItemCreateSerializer)
    def post(self, request):
        ser = SavedItemCreateSerializer(data=request.data)
        ser.is_valid(raise_exception=True)
        try:
            saved, created = base_services.save_item(
                user=request.user,
                content_public_id=str(ser.validated_data['content_id']),
            )
        except Exception:
            return Response(
                {'success': False, 'error': {'code': 'NOT_FOUND', 'message': 'Content not found.'}},
                status=status.HTTP_404_NOT_FOUND,
            )
        return Response(
            {'success': True, 'data': SavedItemSerializer(saved, context={'request': request}).data},
            status=status.HTTP_201_CREATED if created else status.HTTP_200_OK,
        )


@extend_schema(tags=['saves'])
class SavedItemDeleteView(APIView):
    permission_classes = (IsAuthenticated,)

    @extend_schema(summary='Unsave a content item', responses={204: None})
    def delete(self, request, content_id):
        deleted = base_services.remove_save(
            user=request.user, content_public_id=str(content_id),
        )
        if not deleted:
            return Response(
                {'success': False, 'error': {'code': 'NOT_FOUND', 'message': 'Saved item not found.'}},
                status=status.HTTP_404_NOT_FOUND,
            )
        return Response(status=status.HTTP_204_NO_CONTENT)


# ── Comments ──────────────────────────────────────────────────────────────────

@extend_schema(tags=['comments'])
class CommentListView(APIView):
    def get_permissions(self):
        return [IsAuthenticated()] if self.request.method == 'POST' else [AllowAny()]

    @extend_schema(
        summary='List approved comments',
        parameters=[OpenApiParameter('content_id', str, description='Content public_id (UUID)')],
        responses={200: CommentSerializer(many=True)},
    )
    def get(self, request):
        content_id = request.query_params.get('content_id', '').strip()
        if not content_id:
            return Response(
                {'success': False, 'error': {'code': 'VALIDATION_ERROR', 'message': 'content_id is required.'}},
                status=status.HTTP_400_BAD_REQUEST,
            )
        qs = (
            Comment.objects
            .filter(content__public_id=content_id, status=Comment.STATUS_APPROVED)
            .select_related('user')
        )
        paginator = StandardPagination()
        page = paginator.paginate_queryset(qs, request)
        return paginator.get_paginated_response(CommentSerializer(page, many=True).data)

    @extend_schema(summary='Post a comment', request=CommentCreateSerializer, responses={201: CommentSerializer})
    def post(self, request):
        ser = CommentCreateSerializer(data=request.data)
        ser.is_valid(raise_exception=True)
        try:
            comment = base_services.create_comment(
                user=request.user,
                content_public_id=str(ser.validated_data['content_id']),
                text=ser.validated_data['text'],
            )
        except Exception:
            return Response(
                {'success': False, 'error': {'code': 'NOT_FOUND', 'message': 'Content not found.'}},
                status=status.HTTP_404_NOT_FOUND,
            )
        return Response({'success': True, 'data': CommentSerializer(comment).data}, status=status.HTTP_201_CREATED)


@extend_schema(tags=['comments'])
class CommentDeleteView(APIView):
    permission_classes = (IsAuthenticated,)

    @extend_schema(summary='Delete (archive) a comment', responses={204: None})
    def delete(self, request, public_id):
        try:
            comment = Comment.objects.get(public_id=public_id, status__in=(Comment.STATUS_PENDING, Comment.STATUS_APPROVED))
        except Comment.DoesNotExist:
            return Response(
                {'success': False, 'error': {'code': 'NOT_FOUND', 'message': 'Comment not found.'}},
                status=status.HTTP_404_NOT_FOUND,
            )
        if comment.user != request.user and not request.user.is_content_creator:
            return Response(status=status.HTTP_403_FORBIDDEN)
        comment.status = Comment.STATUS_REJECTED
        comment.save(update_fields=['status', 'updated_at'])
        return Response(status=status.HTTP_204_NO_CONTENT)


@extend_schema(tags=['comments'])
class PendingCommentsView(APIView):
    permission_classes = (IsContentCreator,)

    @extend_schema(summary='Moderation queue — pending comments', responses={200: CommentSerializer(many=True)})
    def get(self, request):
        qs = (
            Comment.objects
            .filter(status=Comment.STATUS_PENDING)
            .select_related('user', 'content')
            .order_by('created_at')
        )
        paginator = StandardPagination()
        page = paginator.paginate_queryset(qs, request)
        return paginator.get_paginated_response(CommentSerializer(page, many=True).data)


@extend_schema(tags=['comments'])
class CommentApproveView(APIView):
    permission_classes = (IsContentCreator,)

    @extend_schema(summary='Approve a comment', responses={200: CommentSerializer})
    def post(self, request, public_id):
        comment = base_services.set_comment_status(public_id=public_id, status=Comment.STATUS_APPROVED)
        if comment is None:
            return Response(
                {'success': False, 'error': {'code': 'NOT_FOUND', 'message': 'Comment not found.'}},
                status=status.HTTP_404_NOT_FOUND,
            )
        return success(CommentSerializer(comment).data)


@extend_schema(tags=['comments'])
class CommentRejectView(APIView):
    permission_classes = (IsContentCreator,)

    @extend_schema(summary='Reject (archive) a comment', responses={204: None})
    def post(self, request, public_id):
        if not base_services.set_comment_status(public_id=public_id, status=Comment.STATUS_REJECTED):
            return Response(
                {'success': False, 'error': {'code': 'NOT_FOUND', 'message': 'Comment not found.'}},
                status=status.HTTP_404_NOT_FOUND,
            )
        return Response(status=status.HTTP_204_NO_CONTENT)


# ── Progress (mark complete) ──────────────────────────────────────────────────

@extend_schema(tags=['progress'])
class MarkCompleteView(APIView):
    permission_classes = (IsAuthenticated,)

    @extend_schema(summary='Mark content as completed')
    def post(self, request):
        content_id = (request.data.get('content_id') or '').strip()
        if not content_id:
            return Response(
                {'success': False, 'error': {'code': 'VALIDATION_ERROR', 'message': 'content_id is required.'}},
                status=status.HTTP_400_BAD_REQUEST,
            )
        try:
            _, created = base_services.mark_complete(user=request.user, content_public_id=content_id)
        except Exception:
            return Response(
                {'success': False, 'error': {'code': 'NOT_FOUND', 'message': 'Content not found.'}},
                status=status.HTTP_404_NOT_FOUND,
            )
        return success({'marked': True, 'first_time': created})


# ── Search ────────────────────────────────────────────────────────────────────

@extend_schema(tags=['search'])
class SearchView(APIView):
    permission_classes = (AllowAny,)
    VALID_TYPES = frozenset(('all', 'post', 'video', 'audio', 'note', 'hadith'))

    @extend_schema(
        summary='Search across all published content',
        parameters=[
            OpenApiParameter('q', str, required=True, description='Search query'),
            OpenApiParameter('type', str, description='all | post | video | audio | note | hadith'),
        ],
    )
    def get(self, request):
        q = request.query_params.get('q', '').strip()
        content_type = request.query_params.get('type', 'all')
        if not q:
            return Response(
                {'success': False, 'error': {'code': 'VALIDATION_ERROR', 'message': 'q is required.'}},
                status=status.HTTP_400_BAD_REQUEST,
            )
        if content_type not in self.VALID_TYPES:
            return Response(
                {'success': False, 'error': {'code': 'VALIDATION_ERROR', 'message': f'type must be one of {sorted(self.VALID_TYPES)}.'}},
                status=status.HTTP_400_BAD_REQUEST,
            )
        raw = base_services.search(q=q, content_type=content_type)
        return success({
            k: ContentListSerializer(v, many=True, context={'request': request}).data
            for k, v in raw.items()
        })


# ── Daily guidance ────────────────────────────────────────────────────────────

@extend_schema(tags=['discovery'])
class DailyGuidanceView(APIView):
    permission_classes = (AllowAny,)

    @extend_schema(summary="Today's curated content picks")
    def get(self, request):
        from django.utils import timezone
        from .models import DailyGuidance

        today = timezone.now().date()
        dg = (
            DailyGuidance.objects.filter(date__lte=today)
            .prefetch_related('items__author', 'items__category')
            .order_by('-date')
            .first()
        )
        items = dg.items.filter(is_published=True, is_archived=False) if dg else []
        return success({
            'date': str(dg.date if dg else today),
            'items': ContentListSerializer(items, many=True, context={'request': request}).data,
        })
