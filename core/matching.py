"""
Oduma Connect — Intelligent Matching Service
============================================
Computes a 0–100 match score between an investor and a project.
Designed as a pure service layer — no Django ORM calls inside;
swap the algorithm for AI embeddings later without touching views.

Score breakdown:
  Industry alignment     — 30 pts
  Funding range fit      — 25 pts
  Pipeline stage compat  — 25 pts
  Geography overlap      — 20 pts
"""

from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .models import UserProfile, Project


# ── Stage compatibility map ────────────────────────────────────────────────
# Investors have preferred_sectors as comma-separated text; stage preference
# is inferred from ticket_size: large ticket → later stages preferred.
_STAGE_ORDER = ['idea', 'validation', 'investment', 'growth']

# Funding stage → approximate USD mid-range for range matching
_FUNDING_STAGE_MID = {
    'pre_seed':    50_000,
    'seed':        500_000,
    'pre_series_a':1_500_000,
    'series_a':    5_000_000,
    'series_b':    20_000_000,
    'grant':       200_000,
    '':            0,
}


def _industry_score(investor_profile: 'UserProfile', project: 'Project') -> int:
    """
    30 pts: does the project's industry appear in the investor's preferred sectors?
    Full match → 30. Partial (project category keyword in thesis) → 15. No match → 0.
    """
    if not investor_profile:
        return 15  # neutral when no profile

    sectors_raw = investor_profile.preferred_sectors or ''
    thesis_raw  = investor_profile.investment_thesis or ''

    sectors = [s.strip().lower() for s in sectors_raw.split(',') if s.strip()]
    proj_industry = (project.industry or '').lower()

    if not sectors:
        # No preference set → partial credit
        return 15

    if proj_industry in sectors:
        return 30

    # Fuzzy: check thesis text
    if proj_industry and proj_industry in thesis_raw.lower():
        return 15

    return 0


def _funding_score(investor_profile: 'UserProfile', project: 'Project') -> int:
    """
    25 pts: does the project's funding stage fall within the investor's ticket range?
    Perfect overlap → 25. Adjacent → 12. No data → neutral 12.
    """
    if not investor_profile:
        return 12

    t_min = float(investor_profile.ticket_size_min or 0)
    t_max = float(investor_profile.ticket_size_max or 0)
    proj_stage = project.funding_stage or ''

    if not proj_stage or (t_min == 0 and t_max == 0):
        return 12  # neutral — no data

    proj_mid = _FUNDING_STAGE_MID.get(proj_stage, 0)
    if proj_mid == 0:
        return 12

    if t_max == 0:
        # Investor only set a minimum
        return 25 if proj_mid >= t_min else 8

    if t_min <= proj_mid <= t_max:
        return 25
    # Adjacent: within 2× the range
    range_size = t_max - t_min
    if range_size > 0:
        overshoot = max(proj_mid - t_max, t_min - proj_mid)
        if overshoot <= range_size:
            return 12
    return 4


def _stage_score(investor_profile: 'UserProfile', project: 'Project') -> int:
    """
    25 pts: stage compatibility heuristic.
    Large ticket investors → prefer later stages. Small ticket → early stages.
    """
    if not investor_profile:
        return 12

    t_min = float(investor_profile.ticket_size_min or 0)
    t_max = float(investor_profile.ticket_size_max or 0)
    avg_ticket = ((t_min + t_max) / 2) if t_max else t_min

    proj_stage = project.pipeline_stage or 'idea'
    stage_idx  = _STAGE_ORDER.index(proj_stage) if proj_stage in _STAGE_ORDER else 0

    # Classify investor appetite by ticket size
    if avg_ticket == 0:
        return 12  # neutral

    if avg_ticket < 200_000:
        # Early-stage investor — prefers idea/validation
        preferred_idx = [0, 1]
    elif avg_ticket < 2_000_000:
        # Seed investor — validation / investment
        preferred_idx = [1, 2]
    else:
        # Growth investor — investment / growth
        preferred_idx = [2, 3]

    if stage_idx in preferred_idx:
        return 25
    # Adjacent stage
    for pi in preferred_idx:
        if abs(stage_idx - pi) == 1:
            return 13
    return 4


def _geography_score(investor_profile: 'UserProfile', project: 'Project') -> int:
    """
    20 pts: geography overlap.
    Checks investor's geography_focus against project owner's profile location
    and project location keywords.
    """
    if not investor_profile:
        return 10

    geo_focus = (investor_profile.geography_focus or '').lower()
    if not geo_focus:
        return 10  # no preference → neutral

    # Collect geographic keywords from project and owner
    project_location_text = ''
    try:
        owner_profile = project.owner.userprofile
        project_location_text += (owner_profile.company or '') + ' '
    except Exception:
        pass

    # Check for any overlap word
    focus_words = [w.strip() for w in geo_focus.replace(',', ' ').split() if len(w) > 2]
    for word in focus_words:
        if word in project_location_text.lower():
            return 20
        # Pan-African investors match any project
        if word in ('africa', 'african', 'global', 'worldwide', 'all'):
            return 18

    return 4


def compute_match_score(investor_profile: 'UserProfile', project: 'Project') -> int:
    """
    Return a 0–100 integer match score.
    Safe to call with None investor_profile (returns neutral ~50).
    """
    score = (
        _industry_score(investor_profile, project)
        + _funding_score(investor_profile, project)
        + _stage_score(investor_profile, project)
        + _geography_score(investor_profile, project)
    )
    return min(100, max(0, score))


def score_label(score: int) -> tuple[str, str]:
    """Return (label, css_class) for a match score."""
    if score >= 80:
        return ('Excellent Match', 'excellent')
    elif score >= 60:
        return ('Strong Match', 'strong')
    elif score >= 40:
        return ('Good Match', 'good')
    elif score >= 20:
        return ('Partial Match', 'partial')
    else:
        return ('Low Match', 'low')


def get_top_matches(investor_profile: 'UserProfile', projects, n: int = 6) -> list[dict]:
    """
    Score a queryset of projects and return the top n as a list of dicts:
    {'project': Project, 'score': int, 'label': str, 'css': str}
    """
    scored = []
    for p in projects:
        s = compute_match_score(investor_profile, p)
        label, css = score_label(s)
        scored.append({'project': p, 'score': s, 'label': label, 'css': css})
    scored.sort(key=lambda x: x['score'], reverse=True)
    return scored[:n]


def get_innovator_investor_matches(project, investors_qs, n: int = 5) -> list[dict]:
    """
    For an innovator's project, find matching investors.
    Returns top n investors scored against the project.
    """
    scored = []
    for inv in investors_qs:
        profile = getattr(inv, 'userprofile', None)
        s = compute_match_score(profile, project)
        label, css = score_label(s)
        scored.append({'investor': inv, 'score': s, 'label': label, 'css': css})
    scored.sort(key=lambda x: x['score'], reverse=True)
    return scored[:n]
