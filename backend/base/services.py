"""
base/services.py — engagement: saves, comments, progress.
"""
import logging

from .models import SavedItem, Comment, ContentProgress

logger = logging.getLogger(__name__)


def save_item(*, user, content_public_id: str) -> tuple:
    from content.models import Content
    content = Content.objects.get(public_id=content_public_id, is_published=True, is_archived=False)
    return SavedItem.objects.get_or_create(user=user, content=content)


def remove_save(*, user, content_public_id: str) -> bool:
    deleted, _ = SavedItem.objects.filter(
        user=user, content__public_id=content_public_id,
    ).delete()
    return bool(deleted)


def create_comment(*, user, content_public_id: str, text: str) -> Comment:
    from content.models import Content
    content = Content.objects.get(public_id=content_public_id, is_published=True, is_archived=False)
    return Comment.objects.create(user=user, content=content, text=text)


def set_comment_status(*, public_id, status: str):
    """Set comment status to approved/rejected/pending. Returns Comment or None."""
    try:
        comment = Comment.objects.select_related('user').get(
            public_id=public_id, status__in=(Comment.STATUS_PENDING, Comment.STATUS_APPROVED),
        )
    except Comment.DoesNotExist:
        return None
    if comment.status != status:
        comment.status = status
        comment.save(update_fields=['status', 'updated_at'])
    return comment


def mark_complete(*, user, content_public_id: str) -> tuple:
    from content.models import Content
    content = Content.objects.get(public_id=content_public_id, is_published=True, is_archived=False)
    return ContentProgress.objects.get_or_create(user=user, content=content)


def search(*, q: str, content_type: str = 'all') -> dict:
    from .search import search_content
    return search_content(q=q, content_type=content_type)
