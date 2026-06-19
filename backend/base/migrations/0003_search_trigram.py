"""PostgreSQL-only: pg_trgm + unaccent + GIN index on content_content.search_text."""
from django.contrib.postgres.operations import TrigramExtension, UnaccentExtension
from django.db import migrations


def create(apps, schema_editor):
    if schema_editor.connection.vendor != 'postgresql':
        return
    with schema_editor.connection.cursor() as c:
        c.execute('CREATE INDEX IF NOT EXISTS content_content_search_trgm ON content_content USING gin (search_text gin_trgm_ops);')


def drop(apps, schema_editor):
    if schema_editor.connection.vendor != 'postgresql':
        return
    with schema_editor.connection.cursor() as c:
        c.execute('DROP INDEX IF EXISTS content_content_search_trgm;')


class Migration(migrations.Migration):
    dependencies = [('base', '0002_initial'), ('content', '0001_initial')]
    operations = [TrigramExtension(), UnaccentExtension(), migrations.RunPython(create, drop)]
