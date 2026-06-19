from django.db.models import BooleanField, Count, Exists, OuterRef, Q, Value
from django.utils import timezone


def published_q(**extra_filters):
    now = timezone.now()
    return Q(
        is_published=True,
        is_archived=False,
        **extra_filters,
    ) & (Q(publish_at__isnull=True) | Q(publish_at__lte=now))


def annotate_is_saved(qs, user):
    """Annotate _is_saved in one EXISTS query — prevents N+1 on list views."""
    from .models import SavedItem
    if not (user and getattr(user, 'is_authenticated', False)):
        return qs.annotate(_is_saved=Value(False, output_field=BooleanField()))
    return qs.annotate(_is_saved=Exists(
        SavedItem.objects.filter(user=user, content_id=OuterRef('pk'))
    ))


def annotate_is_completed(qs, user):
    """Annotate _is_completed in one EXISTS query."""
    from .models import ContentProgress
    if not (user and getattr(user, 'is_authenticated', False)):
        return qs.annotate(_is_completed=Value(False, output_field=BooleanField()))
    return qs.annotate(_is_completed=Exists(
        ContentProgress.objects.filter(user=user, content_id=OuterRef('pk'))
    ))


def annotate_engagement(qs, user):
    """
    Single-pass annotation: is_saved, is_completed, saves_count, completions_count.
    Call this on any Content queryset before serialization to avoid N+1.
    """
    qs = annotate_is_saved(qs, user)
    qs = annotate_is_completed(qs, user)
    qs = qs.annotate(
        _saves_count=Count('saves', distinct=True),
        _completions_count=Count('completions', distinct=True),
    )
    return qs
