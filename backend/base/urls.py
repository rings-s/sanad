from django.urls import path
from .views import (
    CategoryListView, CategoryDetailView, TagListView,
    SavedItemListView, SavedItemDeleteView,
    CommentListView, CommentDeleteView,
    PendingCommentsView, CommentApproveView, CommentRejectView,
    MarkCompleteView, SearchView, DailyGuidanceView,
)
from .admin_api import (
    CategoryAdminListCreateView, CategoryAdminDetailView,
    SubcategoryAdminListCreateView, SubcategoryAdminDetailView,
    TagAdminListCreateView, TagAdminDetailView,
    DailyGuidanceAdminListCreateView, DailyGuidanceAdminDetailView,
    AdminCommentListView,
)
from accounts.admin_api import AdminUserListView, AdminUserDetailView

urlpatterns = [
    # Taxonomy
    path('categories/', CategoryListView.as_view(), name='category-list'),
    path('categories/<slug:slug>/', CategoryDetailView.as_view(), name='category-detail'),
    path('tags/', TagListView.as_view(), name='tag-list'),

    # Saves / Favorites
    path('saves/', SavedItemListView.as_view(), name='saved-list'),
    path('saves/<uuid:content_id>/', SavedItemDeleteView.as_view(), name='saved-delete'),

    # Comments
    path('comments/', CommentListView.as_view(), name='comment-list'),
    path('comments/pending/', PendingCommentsView.as_view(), name='comment-pending'),
    path('comments/<uuid:public_id>/approve/', CommentApproveView.as_view(), name='comment-approve'),
    path('comments/<uuid:public_id>/reject/', CommentRejectView.as_view(), name='comment-reject'),
    path('comments/<uuid:public_id>/', CommentDeleteView.as_view(), name='comment-delete'),

    # Progress
    path('progress/', MarkCompleteView.as_view(), name='mark-complete'),

    # Discovery
    path('daily/', DailyGuidanceView.as_view(), name='daily-guidance'),
    path('search/', SearchView.as_view(), name='search'),

    # ── In-app admin (Sheikh only) — separate from Django's admin site ──────────
    path('admin/categories/', CategoryAdminListCreateView.as_view(), name='admin-category-list'),
    path('admin/categories/<slug:slug>/', CategoryAdminDetailView.as_view(), name='admin-category-detail'),
    path('admin/subcategories/', SubcategoryAdminListCreateView.as_view(), name='admin-subcategory-list'),
    path('admin/subcategories/<slug:slug>/', SubcategoryAdminDetailView.as_view(), name='admin-subcategory-detail'),
    path('admin/tags/', TagAdminListCreateView.as_view(), name='admin-tag-list'),
    path('admin/tags/<slug:slug>/', TagAdminDetailView.as_view(), name='admin-tag-detail'),
    path('admin/daily/', DailyGuidanceAdminListCreateView.as_view(), name='admin-daily-list'),
    path('admin/daily/<uuid:public_id>/', DailyGuidanceAdminDetailView.as_view(), name='admin-daily-detail'),
    path('admin/comments/', AdminCommentListView.as_view(), name='admin-comment-list'),
    path('admin/users/', AdminUserListView.as_view(), name='admin-user-list'),
    path('admin/users/<uuid:public_id>/', AdminUserDetailView.as_view(), name='admin-user-detail'),
]
