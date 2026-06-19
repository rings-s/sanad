"""
content/youtube.py — YouTube Data API v3 metadata fetching.

Uses the YOUTUBE_API_KEY setting (simple API key, no OAuth needed for public videos).
The API key in Google Cloud Console has an HTTP Referrer restriction, so every
server-side request includes a Referer header matching FRONTEND_URL.
"""
import re
import logging

import requests as http_requests
from django.conf import settings

logger = logging.getLogger(__name__)

_YT_API_URL = 'https://www.googleapis.com/youtube/v3/videos'

# Regex covers all common YouTube URL forms:
#   https://www.youtube.com/watch?v=ID
#   https://youtu.be/ID
#   https://www.youtube.com/embed/ID
#   https://www.youtube.com/shorts/ID
_YT_ID_RE = re.compile(
    r'(?:v=|youtu\.be/|embed/|shorts/)([A-Za-z0-9_-]{11})'
)

# ISO 8601 duration parser — PT1H2M3S → seconds
_DURATION_RE = re.compile(r'PT(?:(\d+)H)?(?:(\d+)M)?(?:(\d+)S)?')


def extract_video_id(url: str) -> str | None:
    """Return the 11-char YouTube video ID from any supported URL, or None."""
    m = _YT_ID_RE.search(url or '')
    return m.group(1) if m else None


def parse_iso8601_duration(duration: str) -> int | None:
    """Convert an ISO 8601 duration string (e.g. PT1H2M3S) to total seconds."""
    m = _DURATION_RE.match(duration or '')
    if not m:
        return None
    h = int(m.group(1) or 0)
    mi = int(m.group(2) or 0)
    s = int(m.group(3) or 0)
    return h * 3600 + mi * 60 + s


def fetch_video_metadata(url: str) -> dict:
    """
    Fetch public video metadata from the YouTube Data API v3.

    Returns a dict with keys:
        video_id, title, description, thumbnail_url,
        duration_seconds, channel_title

    Raises:
        RuntimeError — if YOUTUBE_API_KEY is not configured or the API call fails.
        ValueError   — if the URL is invalid or the video is not found / private.
    """
    video_id = extract_video_id(url)
    if not video_id:
        raise ValueError('Could not extract a valid YouTube video ID from the URL.')

    api_key = getattr(settings, 'YOUTUBE_API_KEY', '')
    if not api_key:
        raise RuntimeError('YOUTUBE_API_KEY is not configured.')

    # The API key has an HTTP Referrer restriction in Google Cloud Console.
    # Server-side requests don't carry a browser Referer, so we set it explicitly.
    frontend_url = getattr(settings, 'FRONTEND_URL', 'http://localhost:5173').rstrip('/')
    headers = {'Referer': f'{frontend_url}/'}

    try:
        response = http_requests.get(
            _YT_API_URL,
            params={'part': 'snippet,contentDetails', 'id': video_id, 'key': api_key},
            headers=headers,
            timeout=10,
        )
        response.raise_for_status()
    except http_requests.exceptions.Timeout:
        logger.error('YouTube API timed out for video %s', video_id)
        raise RuntimeError('YouTube API timed out. Please try again.')
    except http_requests.exceptions.HTTPError as exc:
        logger.error('YouTube API HTTP error for video %s: %s', video_id, exc)
        raise RuntimeError(f'YouTube API returned an error: {exc.response.status_code}')
    except http_requests.exceptions.RequestException as exc:
        logger.error('YouTube API network error for video %s: %s', video_id, exc)
        raise RuntimeError('Could not reach the YouTube API.')

    data = response.json()
    items = data.get('items', [])
    if not items:
        raise ValueError('Video not found, is private, or has been deleted.')

    item = items[0]
    snippet = item.get('snippet', {})
    content_details = item.get('contentDetails', {})

    thumbnails = snippet.get('thumbnails', {})
    thumbnail_url = (
        thumbnails.get('maxres', {}).get('url')
        or thumbnails.get('high', {}).get('url')
        or thumbnails.get('medium', {}).get('url')
        or ''
    )

    return {
        'video_id': video_id,
        'title': snippet.get('title', ''),
        'description': snippet.get('description', ''),
        'thumbnail_url': thumbnail_url,
        'duration_seconds': parse_iso8601_duration(content_details.get('duration', '')),
        'channel_title': snippet.get('channelTitle', ''),
    }
