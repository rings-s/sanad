"""
base/search.py — Arabic-aware, backend-aware content search.

normalize_arabic: strips tashkeel, folds alef/ya/ta-marbuta variants,
lowercases Latin. Applied to both stored search_text and incoming queries.

search_content: on PostgreSQL uses pg_trgm for ranked, typo-tolerant search;
falls back to normalized icontains on SQLite (dev/tests).
"""

import re

from django.db import connection
from django.db.models import Q

# Strip Arabic combining marks (tashkeel), Quranic annotation marks, the
# superscript alef, and the tatweel/kashida — but NOT the letters themselves.
# Expressed as explicit code points: the previous literal range spanned
# U+0610–U+064B, which swallowed the entire Arabic letter block (U+0621–U+064A)
# and reduced any Arabic text to an empty string.
_DIACRITICS = re.compile(
    "["
    "ؐ-ؚ"  # Arabic signs (honorifics, small high marks)
    "ً-ٟ"  # tashkeel + combining marks (fathatan … wavy hamza below)
    "ٰ"  # superscript alef
    "ۖ-ۭ"  # Quranic annotation / small high marks
    "ـ"  # tatweel (kashida)
    "]"
)
_WHITESPACE = re.compile(r"\s+")
_FOLD = str.maketrans(
    {
        "أ": "ا",
        "إ": "ا",
        "آ": "ا",
        "ٱ": "ا",
        "ى": "ي",
        "ئ": "ي",
        "ة": "ه",
        "ؤ": "و",
    }
)


def normalize_arabic(text) -> str:
    if not text:
        return ""
    t = _DIACRITICS.sub("", str(text))
    t = t.translate(_FOLD)
    t = t.lower()
    return _WHITESPACE.sub(" ", t).strip()


def _is_postgres() -> bool:
    return connection.vendor == "postgresql"


def _rank(qs, nq):
    if _is_postgres():
        from django.contrib.postgres.search import TrigramSimilarity

        return (
            qs.annotate(_sim=TrigramSimilarity("search_text", nq))
            .filter(Q(search_text__icontains=nq) | Q(_sim__gt=0.1))
            .order_by("-_sim", "-created_at")
        )
    return qs.filter(search_text__icontains=nq).order_by("-created_at")


def search_content(*, q: str, content_type: str = "all") -> dict:
    """
    Ranked search over published Content. Returns {type_plural: QuerySet}.
    Empty/blank query returns {}.
    """
    from content.models import Content
    from .utils import published_q

    nq = normalize_arabic(q)
    if not nq:
        return {}

    base_qs = Content.objects.filter(published_q()).select_related("author", "category")

    if content_type != "all":
        type_map = {
            "post": "post",
            "video": "video",
            "audio": "audio",
            "note": "note",
            "hadith": "hadith",
        }
        ct = type_map.get(content_type)
        if not ct:
            return {}
        return {f"{content_type}s": _rank(base_qs.filter(type=ct), nq)}

    return {
        "posts": _rank(base_qs.filter(type=Content.POST), nq),
        "videos": _rank(base_qs.filter(type=Content.VIDEO), nq),
        "audios": _rank(base_qs.filter(type=Content.AUDIO), nq),
        "hadiths": _rank(base_qs.filter(type=Content.HADITH), nq),
    }
