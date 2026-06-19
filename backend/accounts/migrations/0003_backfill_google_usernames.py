"""
Backfill friendly usernames for accounts created via Google SSO before the
name-derived handle was introduced. Renames opaque ``google_<hex>`` usernames
to a readable slug derived from the stored first/last name (e.g. "Ahmed Bashir"
→ "ahmed-bashir"). Accounts with no stored name keep their opaque slug.

One-way: the reverse is a no-op (the original random slugs are not recoverable
and there is no reason to restore them).
"""
import uuid

from django.db import migrations
from django.utils.text import slugify


def backfill_google_usernames(apps, schema_editor):
    User = apps.get_model('accounts', 'User')

    # All usernames already in use — so generated handles never collide with an
    # existing Google account, a manually-registered user, or each other.
    taken = set(User.objects.values_list('username', flat=True))

    for user in User.objects.filter(username__startswith='google_').iterator():
        base = slugify(f'{user.first_name} {user.last_name}'.strip(), allow_unicode=True)
        if not base:
            continue  # no name to derive from — leave the opaque slug as-is

        taken.discard(user.username)  # free up its current name
        candidate = base
        while candidate in taken:
            candidate = f'{base}-{uuid.uuid4().hex[:6]}'

        user.username = candidate
        user.save(update_fields=['username'])
        taken.add(candidate)


def noop(apps, schema_editor):
    pass


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0002_userprofile_nationality'),
    ]

    operations = [
        migrations.RunPython(backfill_google_usernames, noop),
    ]
