"""Recompute Content.search_text for existing rows.

The previous normalize_arabic() regex stripped all Arabic letters, so every
row's search_text was stored empty and Arabic search returned nothing. With the
regex fixed, repopulate search_text from the source fields.
"""

from django.db import migrations


def backfill_search_text(apps, schema_editor):
    from base.search import normalize_arabic

    Content = apps.get_model("content", "Content")
    batch = []
    for obj in Content.objects.all().iterator(chunk_size=500):
        text = " ".join(
            filter(
                None,
                [
                    obj.title,
                    obj.body,
                    obj.original_text,
                    obj.translated_text,
                    obj.source_attribution,
                ],
            )
        )
        obj.search_text = normalize_arabic(text)
        batch.append(obj)
        if len(batch) >= 500:
            Content.objects.bulk_update(batch, ["search_text"])
            batch = []
    if batch:
        Content.objects.bulk_update(batch, ["search_text"])


class Migration(migrations.Migration):
    dependencies = [
        ("content", "0003_content_document"),
    ]

    operations = [
        migrations.RunPython(backfill_search_text, migrations.RunPython.noop),
    ]
