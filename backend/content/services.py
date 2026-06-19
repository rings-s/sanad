from base.utils import published_q, annotate_engagement
from base.search import normalize_arabic
from .models import Content


def list_published(*, content_type=None, search=None, category=None, subcategory=None, user=None):
    qs = Content.objects.filter(published_q()).select_related('author', 'category', 'subcategory')
    if content_type:
        qs = qs.filter(type=content_type)
    if category:
        qs = qs.filter(category__slug=category)
    if subcategory:
        qs = qs.filter(subcategory__slug=subcategory)
    if search:
        qs = qs.filter(search_text__icontains=normalize_arabic(search))
    return annotate_engagement(qs.order_by('-created_at'), user)


def list_for_creator(*, search=None, user=None):
    """All non-archived items for the creator's studio view."""
    qs = Content.objects.filter(author=user, is_archived=False).select_related('author', 'category', 'subcategory')
    if search:
        qs = qs.filter(search_text__icontains=normalize_arabic(search))
    return annotate_engagement(qs.order_by('-created_at'), user)


def list_all(*, content_type=None, search=None, user=None):
    """Every item — published, draft and archived — for the Sheikh admin view."""
    qs = Content.objects.all().select_related('author', 'category', 'subcategory')
    if content_type:
        qs = qs.filter(type=content_type)
    if search:
        qs = qs.filter(search_text__icontains=normalize_arabic(search))
    return annotate_engagement(qs.order_by('-created_at'), user)


def archive(instance: Content) -> None:
    instance.is_archived = True
    instance.save(update_fields=['is_archived', 'updated_at'])


def _bust_feed_cache() -> None:
    from django.core.cache import cache
    from django.utils import timezone
    cache.delete(f'sanad:daily:{timezone.now().date()}')
