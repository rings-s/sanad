from drf_spectacular.utils import extend_schema, OpenApiParameter
from rest_framework import status
from rest_framework.generics import ListCreateAPIView, RetrieveUpdateDestroyAPIView
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from accounts.permissions import IsContentCreator, IsSheikh
from base.responses import SuccessResponseMixin, success
from . import services as content_services
from . import youtube as yt
from .models import Content
from .serializers import (
    ContentListSerializer,
    ContentDetailSerializer,
    ContentWriteSerializer,
)


@extend_schema(
    tags=['content'],
    summary='Fetch YouTube video metadata (title, description, duration, thumbnail)',
    parameters=[
        OpenApiParameter(
            name='url',
            description='Full YouTube video URL (any supported format)',
            required=True,
            type=str,
        )
    ],
)
class YouTubeMetadataView(APIView):
    """
    GET /api/v1/content/youtube-metadata/?url=<youtube_url>

    Returns title, description, duration_seconds, thumbnail_url, channel_title.
    Requires content-creator permission so only creators can pre-fetch metadata.
    """
    permission_classes = (IsContentCreator,)

    def get(self, request):
        url = request.query_params.get('url', '').strip()
        if not url:
            return Response(
                {'success': False, 'error': {'code': 'VALIDATION_ERROR', 'message': 'url query param is required.'}},
                status=status.HTTP_400_BAD_REQUEST,
            )
        try:
            data = yt.fetch_video_metadata(url)
        except RuntimeError as exc:
            return Response(
                {'success': False, 'error': {'code': 'SERVER_ERROR', 'message': str(exc)}},
                status=status.HTTP_503_SERVICE_UNAVAILABLE,
            )
        except ValueError as exc:
            return Response(
                {'success': False, 'error': {'code': 'VALIDATION_ERROR', 'message': str(exc)}},
                status=status.HTTP_400_BAD_REQUEST,
            )
        return success(data)


class ContentListCreateView(SuccessResponseMixin, ListCreateAPIView):
    def get_permissions(self):
        return [IsContentCreator()] if self.request.method == "POST" else [AllowAny()]

    def get_queryset(self):
        params = self.request.query_params
        user = self.request.user
        # Sheikh admin view — every item including drafts and archived.
        if params.get("scope") == "all" and user.is_authenticated and user.is_sheikh:
            return content_services.list_all(
                content_type=params.get("type"),
                search=params.get("search"),
                user=user,
            )
        if params.get("mine") and user.is_authenticated and user.is_content_creator:
            return content_services.list_for_creator(
                search=params.get("search"), user=user
            )
        return content_services.list_published(
            content_type=params.get("type"),
            search=params.get("search"),
            category=params.get("category"),
            subcategory=params.get("subcategory"),
            user=user,
        )

    def get_serializer_class(self):
        return (
            ContentWriteSerializer
            if self.request.method == "POST"
            else ContentListSerializer
        )

    def get_read_serializer_class(self):
        return ContentDetailSerializer

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)
        content_services._bust_feed_cache()

    @extend_schema(
        tags=["content"],
        summary="List published content",
        responses={200: ContentListSerializer(many=True)},
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    @extend_schema(
        tags=["content"],
        summary="Create content (content creators only)",
        request=ContentWriteSerializer,
        responses={201: ContentDetailSerializer},
    )
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)


class ContentDetailView(SuccessResponseMixin, RetrieveUpdateDestroyAPIView):
    lookup_field = "public_id"

    def get_permissions(self):
        if self.request.method in ("PUT", "PATCH"):
            return [IsContentCreator()]
        if self.request.method == "DELETE":
            return [IsSheikh()]
        return [AllowAny()]

    def get_queryset(self):
        user = self.request.user
        is_creator = user.is_authenticated and user.is_content_creator
        is_sheikh = user.is_authenticated and user.is_sheikh
        qs = Content.objects.select_related("author", "category", "subcategory")
        # The Sheikh admin can reach archived items (to view / restore them);
        # everyone else only sees non-archived content.
        if not is_sheikh:
            qs = qs.filter(is_archived=False)
        if not is_creator:
            qs = qs.filter(is_published=True)
        return qs

    def get_serializer_class(self):
        if self.request.method in ("PUT", "PATCH"):
            return ContentWriteSerializer
        return ContentDetailSerializer

    def get_read_serializer_class(self):
        return ContentDetailSerializer

    def perform_update(self, serializer):
        serializer.save()
        content_services._bust_feed_cache()

    def perform_destroy(self, instance):
        content_services.archive(instance)

    @extend_schema(
        tags=["content"],
        summary="Retrieve content",
        responses={200: ContentDetailSerializer},
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    @extend_schema(
        tags=["content"],
        summary="Update content (content creators only)",
        request=ContentWriteSerializer,
        responses={200: ContentDetailSerializer},
    )
    def put(self, request, *args, **kwargs):
        return super().put(request, *args, **kwargs)

    @extend_schema(
        tags=["content"],
        summary="Partially update content (content creators only)",
        request=ContentWriteSerializer,
        responses={200: ContentDetailSerializer},
    )
    def patch(self, request, *args, **kwargs):
        return super().patch(request, *args, **kwargs)

    @extend_schema(
        tags=["content"], summary="Archive content (Sheikh only)", responses={204: None}
    )
    def delete(self, request, *args, **kwargs):
        return super().delete(request, *args, **kwargs)
