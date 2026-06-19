import uuid

from django.conf import settings
from django.db import models
from django.utils.text import slugify


class TimeStampedModel(models.Model):
    public_id = models.UUIDField(default=uuid.uuid4, unique=True, db_index=True, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class SluggedModel(models.Model):
    """
    Taxonomy base for Category and Tag.
    Uses slug (not UUID) as the external identifier — slugs are human-readable
    and stable. No public_id or updated_at needed on taxonomy rows.
    """
    name = models.CharField(max_length=100)
    slug = models.SlugField(max_length=120, unique=True, blank=True, allow_unicode=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        abstract = True
        ordering = ('name',)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name, allow_unicode=True) or uuid.uuid4().hex[:12]
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class Category(SluggedModel):
    icon = models.CharField(max_length=50, blank=True)

    class Meta(SluggedModel.Meta):
        verbose_name_plural = 'categories'


class Subcategory(SluggedModel):
    category = models.ForeignKey(
        Category, on_delete=models.CASCADE, related_name='subcategories',
    )

    class Meta(SluggedModel.Meta):
        verbose_name_plural = 'subcategories'


class Tag(SluggedModel):
    name = models.CharField(max_length=50, unique=True)


class PublishableContent(TimeStampedModel):
    """
    Abstract base for Content. Owns authorship, taxonomy, publish lifecycle,
    and the normalized search_text index column.
    """
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='%(class)ss',
    )
    category = models.ForeignKey(
        Category, on_delete=models.SET_NULL, null=True, blank=True, related_name='%(class)ss',
    )
    subcategory = models.ForeignKey(
        Subcategory, on_delete=models.SET_NULL, null=True, blank=True, related_name='%(class)ss',
    )
    tags = models.ManyToManyField(Tag, blank=True, related_name='%(class)ss')
    is_published = models.BooleanField(default=False, db_index=True)
    publish_at = models.DateTimeField(null=True, blank=True)
    is_archived = models.BooleanField(default=False, db_index=True)
    search_text = models.TextField(blank=True, default='', editable=False)

    class Meta:
        abstract = True
        ordering = ('-created_at',)
        indexes = [
            models.Index(fields=['is_published', 'is_archived', 'created_at']),
            models.Index(fields=['is_published', 'is_archived', 'publish_at']),
        ]

    def build_search_text(self) -> str:
        return ''

    def save(self, *args, **kwargs):
        from .search import normalize_arabic
        self.search_text = normalize_arabic(self.build_search_text())
        update_fields = kwargs.get('update_fields')
        if update_fields is not None and 'search_text' not in update_fields:
            kwargs['update_fields'] = list(update_fields) + ['search_text']
        super().save(*args, **kwargs)


# ── Engagement ────────────────────────────────────────────────────────────────

class SavedItem(TimeStampedModel):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='saved_items',
    )
    content = models.ForeignKey(
        'content.Content', on_delete=models.CASCADE, related_name='saves',
    )

    class Meta:
        unique_together = ('user', 'content')
        ordering = ('-created_at',)

    def __str__(self):
        return f"{self.user.email} saved → {self.content_id}"


class Comment(TimeStampedModel):
    STATUS_PENDING = 'pending'
    STATUS_APPROVED = 'approved'
    STATUS_REJECTED = 'rejected'
    STATUS_CHOICES = [
        (STATUS_PENDING, 'Pending'),
        (STATUS_APPROVED, 'Approved'),
        (STATUS_REJECTED, 'Rejected'),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='comments',
    )
    content = models.ForeignKey(
        'content.Content', on_delete=models.CASCADE, related_name='comments',
    )
    text = models.TextField(max_length=1000)
    status = models.CharField(
        max_length=10, choices=STATUS_CHOICES, default=STATUS_PENDING, db_index=True,
    )

    class Meta:
        ordering = ('-created_at',)
        indexes = [
            models.Index(fields=['content', 'status']),
        ]

    def __str__(self):
        return f"Comment by {self.user.email} [{self.status}]"


class ContentProgress(TimeStampedModel):
    """User marks content as completed — the primary learning metric."""
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='progress',
    )
    content = models.ForeignKey(
        'content.Content', on_delete=models.CASCADE, related_name='completions',
    )

    class Meta:
        unique_together = ('user', 'content')
        ordering = ('-created_at',)

    def __str__(self):
        return f"{self.user.email} completed → {self.content_id}"


class DailyGuidance(TimeStampedModel):
    """
    Editors curate a set of content items for each date. The discovery API
    returns today's entry (or the most recent past one as fallback).
    """
    date = models.DateField(unique=True, db_index=True)
    items = models.ManyToManyField('content.Content', blank=True, related_name='daily_guidances')

    class Meta:
        ordering = ('-date',)
        verbose_name = 'Daily guidance'
        verbose_name_plural = 'Daily guidance'

    def __str__(self):
        return f"Daily guidance — {self.date}"
