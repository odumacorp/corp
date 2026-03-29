"""
Zoom Server-to-Server OAuth helpers.

Set in .env:
  ZOOM_ACCOUNT_ID    = <your account id>
  ZOOM_CLIENT_ID     = <your client id>
  ZOOM_CLIENT_SECRET = <your client secret>

Marketplace app scopes required:
  meeting:write:admin
  meeting:read:admin
  recording:read:admin
"""

import base64
import logging
import requests
from django.conf import settings

log = logging.getLogger(__name__)

ZOOM_API = 'https://api.zoom.us/v2'
TOKEN_URL = 'https://zoom.us/oauth/token'

# ── Token ─────────────────────────────────────────────────────────────────

def _get_access_token():
    """Fetch a short-lived Server-to-Server OAuth access token."""
    account_id    = getattr(settings, 'ZOOM_ACCOUNT_ID', '')
    client_id     = getattr(settings, 'ZOOM_CLIENT_ID', '')
    client_secret = getattr(settings, 'ZOOM_CLIENT_SECRET', '')

    if not all([account_id, client_id, client_secret]):
        raise ZoomConfigError(
            'Zoom credentials not configured. '
            'Add ZOOM_ACCOUNT_ID, ZOOM_CLIENT_ID, ZOOM_CLIENT_SECRET to your .env file.'
        )

    creds = base64.b64encode(f'{client_id}:{client_secret}'.encode()).decode()
    resp = requests.post(
        TOKEN_URL,
        params={'grant_type': 'account_credentials', 'account_id': account_id},
        headers={'Authorization': f'Basic {creds}'},
        timeout=10,
    )
    resp.raise_for_status()
    return resp.json()['access_token']


def _headers():
    return {
        'Authorization': f'Bearer {_get_access_token()}',
        'Content-Type': 'application/json',
    }


# ── Errors ────────────────────────────────────────────────────────────────

class ZoomConfigError(Exception):
    """Raised when Zoom credentials are missing from settings."""

class ZoomAPIError(Exception):
    """Raised when the Zoom API returns an unexpected error."""


# ── Meeting creation ──────────────────────────────────────────────────────

def create_meeting(title, scheduled_at=None, duration_minutes=60, host_email=None):
    """
    Create a Zoom meeting.

    Returns the full Zoom API response dict, which includes:
      id          — numeric Zoom meeting ID
      join_url    — URL for participants
      start_url   — URL for the host (contains auth token, expires in ~90 days)
      password    — meeting password
      topic       — meeting title
    """
    payload = {
        'topic': title or 'Oduma Connect Meeting',
        'type': 2 if scheduled_at else 1,   # 1 = instant, 2 = scheduled
        'duration': duration_minutes,
        'settings': {
            'host_video': True,
            'participant_video': True,
            'join_before_host': True,
            'mute_upon_entry': False,
            'auto_recording': 'cloud',          # cloud recording enabled
            'waiting_room': False,
            'approval_type': 2,                 # no registration required
            'audio': 'both',
            'allow_multiple_devices': True,
        },
    }

    if scheduled_at:
        payload['start_time'] = scheduled_at.strftime('%Y-%m-%dT%H:%M:%S')
        payload['timezone'] = 'UTC'

    # Use /users/me to create under the authenticated account's default user
    user_path = f'/users/{host_email}/meetings' if host_email else '/users/me/meetings'
    resp = requests.post(
        ZOOM_API + user_path,
        json=payload,
        headers=_headers(),
        timeout=15,
    )

    if not resp.ok:
        log.error('Zoom create_meeting error %s: %s', resp.status_code, resp.text)
        raise ZoomAPIError(f'Zoom API error {resp.status_code}: {resp.text}')

    return resp.json()


# ── Recordings ────────────────────────────────────────────────────────────

def get_recordings(zoom_meeting_id):
    """
    Fetch cloud recording files for a Zoom meeting.

    Returns a list of recording file dicts (or empty list if none found).
    Each dict contains:
      recording_type  — e.g. 'shared_screen_with_speaker_view'
      file_type       — 'MP4' | 'M4A' | 'TIMELINE' etc.
      play_url        — URL to play the recording (if available)
      download_url    — URL to download
      status          — 'completed' | 'processing'
    """
    resp = requests.get(
        f'{ZOOM_API}/meetings/{zoom_meeting_id}/recordings',
        headers=_headers(),
        timeout=15,
    )
    if resp.status_code == 404:
        return []
    if not resp.ok:
        log.warning('Zoom get_recordings error %s: %s', resp.status_code, resp.text)
        return []
    data = resp.json()
    return data.get('recording_files', [])


# ── Delete ────────────────────────────────────────────────────────────────

def delete_meeting(zoom_meeting_id):
    """Delete a Zoom meeting (best-effort, ignores errors)."""
    try:
        requests.delete(
            f'{ZOOM_API}/meetings/{zoom_meeting_id}',
            headers=_headers(),
            timeout=10,
        )
    except Exception as exc:
        log.warning('Zoom delete_meeting failed: %s', exc)
