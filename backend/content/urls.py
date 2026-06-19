from django.urls import path

from .views import ContentListCreateView, ContentDetailView, YouTubeMetadataView

app_name = 'content'

urlpatterns = [
    path('', ContentListCreateView.as_view(), name='content-list'),
    path('youtube-metadata/', YouTubeMetadataView.as_view(), name='youtube-metadata'),
    path('<uuid:public_id>/', ContentDetailView.as_view(), name='content-detail'),
]
