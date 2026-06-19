from django.core.validators import FileExtensionValidator
from django.db import models
from django.utils.text import slugify

from base.models import PublishableContent

# Documents only — PDF and Word. Anything else is rejected at validation time.
DOCUMENT_EXTENSIONS = ('pdf', 'doc', 'docx')


class Content(PublishableContent):
    VIDEO = 'video'
    AUDIO = 'audio'
    POST = 'post'
    NOTE = 'note'
    HADITH = 'hadith'

    TYPE_CHOICES = [
        (VIDEO, 'Video'),
        (AUDIO, 'Audio'),
        (POST, 'Post'),
        (NOTE, 'Note'),
        (HADITH, 'Hadith / Verse'),
    ]

    type = models.CharField(max_length=10, choices=TYPE_CHOICES, db_index=True)
    title = models.CharField(max_length=300)
    slug = models.SlugField(max_length=300, unique=True, blank=True, allow_unicode=True)
    body = models.TextField(blank=True)
    featured_image = models.ImageField(upload_to='featured_images/', null=True, blank=True)

    # Media — only one populated per item
    youtube_url = models.URLField(max_length=500, null=True, blank=True)
    audio_file = models.FileField(upload_to='audios/%Y/%m/%d/', null=True, blank=True)
    duration_seconds = models.PositiveIntegerField(null=True, blank=True)

    # Attached document — restricted to PDF / Word (.pdf, .doc, .docx) only.
    document = models.FileField(
        upload_to='documents/%Y/%m/%d/', null=True, blank=True,
        validators=[FileExtensionValidator(allowed_extensions=list(DOCUMENT_EXTENSIONS))],
    )

    # Bilingual — hadith only
    original_text = models.TextField(blank=True)
    translated_text = models.TextField(blank=True)

    # Source credibility — hadith and posts
    source_attribution = models.CharField(max_length=300, blank=True)

    class Meta(PublishableContent.Meta):
        verbose_name = 'Content'
        verbose_name_plural = 'Content'
        indexes = PublishableContent.Meta.indexes + [
            models.Index(fields=['type', 'is_published', 'is_archived']),
        ]

    def save(self, *args, **kwargs):
        if not self.slug:
            base = slugify(self.title, allow_unicode=True)[:290]
            self.slug = base or self.public_id.hex[:12]
        super().save(*args, **kwargs)

    def build_search_text(self) -> str:
        return ' '.join(filter(None, [
            self.title, self.body,
            self.original_text, self.translated_text,
            self.source_attribution,
        ]))

    def __str__(self):
        return f"[{self.type}] {self.title[:60]}"
