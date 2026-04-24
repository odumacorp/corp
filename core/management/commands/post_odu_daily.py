"""
Daily Odu post generator — run via cron, produces 2 fresh AI-generated posts per day.
Claude writes the content AND picks image search keywords; we fetch a matching photo
from Unsplash and attach it to the post automatically.
"""
import io
import json
import random
from datetime import timedelta

from django.core.files.base import ContentFile
from django.core.management.base import BaseCommand
from django.utils import timezone


POST_TYPE_POOL = (
    ['tip']          * 4 +
    ['question']     * 4 +
    ['poll']         * 3 +
    ['resource']     * 3 +
    ['opinion']      * 2 +
    ['article']      * 2 +
    ['milestone']    * 1 +
    ['announcement'] * 1
)

INDUSTRIES = [
    'tech', 'finance', 'health', 'education', 'agriculture',
    'energy', 'manufacturing', 'retail', 'media', 'logistics',
]

SYSTEM_PROMPT = """You are Odu — the strategic voice of Oduma Corp, a platform connecting African innovators with investors.

You combine the mindset and communication styles of top entrepreneurial thinkers: disciplined like a builder, visionary like a founder, and pragmatic like an investor. You speak directly to innovators who are building ideas and seeking investment across Africa.

Your posts must go beyond inspiration and push toward execution, clarity, and strategic thinking. Every post must feel like advice from someone who has built and funded companies — confident, sharp, and grounded in reality.

Core focus areas: entrepreneurship, idea validation, risk-taking, resilience, and investor readiness.

Tone rules:
- Confident and direct. No fluff, no corporate-speak.
- No emojis. Max 2 relevant hashtags at the end.
- Avoid clichés like "never give up" unless reframed with depth.
- Second-person ("you") or first-person plural ("we") where natural.
- Full sentences throughout.

Every post must follow this structure internally (Motivation → Insight → Action) even when formatted as a continuous piece.

IMPORTANT: Every response must include an "image_query" field — 3-5 comma-separated English keywords describing a relevant professional stock photo. Think visually: "African founder pitching investors", "startup whiteboard strategy session", "entrepreneur laptop café Nairobi", "product launch team Africa"."""


def _build_prompt(post_type, industry):
    today = timezone.now().strftime('%A %d %B %Y')
    context = f"Today is {today}. Industry focus: {industry}. Post type: {post_type}."
    image_field = '"image_query": "3-5 keywords describing a relevant professional stock photo"'
    hashtag_rule = (
        f'"hashtags": "exactly 2 hashtags with # prefix, relevant to {industry} and the post — '
        f'e.g. \\"#StartupAfrica #Fintech\\" — always include the # symbol"'
    )
    structure_note = (
        "Structure the content with these three clearly labelled sections:\n"
        "Motivation: a powerful, original opening statement (NOT a cliché).\n"
        "Insight: 2-4 sentences connecting to building ideas, attracting investors, or execution/validation.\n"
        "Action: one clear, immediately actionable next step the innovator can take today."
    )

    if post_type == 'tip':
        return f"""{context}

Write a high-impact tip for innovators in the {industry} sector who are building ideas and seeking investment.

{structure_note}

Return JSON only:
{{
  "title": "sharp tip headline (max 12 words, not a cliché)",
  "content": "Motivation: ...\\n\\nInsight: ...\\n\\nAction: ...",
  {hashtag_rule},
  {image_field}
}}"""

    if post_type == 'question':
        return f"""{context}

Write a thought-provoking question that challenges innovators in {industry} to think strategically about building or investor readiness.

{structure_note}

Return JSON only:
{{
  "title": "the question as a punchy title (max 15 words)",
  "content": "Motivation: bold framing statement.\\n\\nInsight: 2-3 sentences of context connecting to execution or investor readiness.\\n\\nAction: invite the community to answer with a specific angle.",
  {hashtag_rule},
  {image_field}
}}"""

    if post_type == 'opinion':
        return f"""{context}

Write a bold, slightly contrarian opinion about building startups or raising investment in {industry} across Africa.

{structure_note}

Return JSON only:
{{
  "title": "punchy contrarian headline (max 12 words)",
  "content": "Motivation: the bold claim.\\n\\nInsight: 2-4 sentences defending the position with strategic depth.\\n\\nAction: specific thing the reader should do or reconsider. End with: Agree or disagree? Tell us below.",
  {hashtag_rule},
  {image_field}
}}"""

    if post_type == 'resource':
        return f"""{context}

Share 3-5 genuinely useful resources (tools, frameworks, or approaches) for founders in {industry} building investor-ready startups.

{structure_note}

Return JSON only:
{{
  "title": "resource list headline (max 12 words)",
  "content": "Motivation: one sharp opening line on why these matter.\\n\\nInsight: the list with brief context for each resource.\\n\\nAction: pick one and apply it this week.",
  {hashtag_rule},
  {image_field}
}}"""

    if post_type == 'article':
        return f"""{context}

Write a sharp, high-value article for innovators in {industry} — covering execution, validation, or investor readiness.

{structure_note}

Return JSON only:
{{
  "title": "article headline (max 12 words)",
  "content": "Motivation: powerful opening.\\n\\nInsight: the core argument or how-to (200-280 words, clear paragraph structure).\\n\\nAction: one concrete next step.",
  {hashtag_rule},
  {image_field}
}}"""

    if post_type == 'poll':
        return f"""{context}

Create a poll that forces innovators in {industry} to make a strategic choice about building or funding.

{structure_note}

Return JSON only:
{{
  "title": "poll headline (max 12 words)",
  "content": "Motivation: sharp framing of the dilemma.\\n\\nInsight: 1-2 sentences on why this choice matters for execution or investor readiness.\\n\\nAction: vote and share your reasoning below.",
  "poll_question": "the decisive poll question (max 20 words)",
  "poll_options": ["option 1", "option 2", "option 3", "option 4"],
  {hashtag_rule},
  {image_field}
}}"""

    if post_type == 'milestone':
        return f"""{context}

Write a milestone post for the Oduma Corp community that connects platform growth to the mission of empowering African innovators.

{structure_note}

Return JSON only:
{{
  "title": "milestone headline (max 12 words)",
  "content": "Motivation: powerful statement about what the milestone means.\\n\\nInsight: 2-3 sentences on what it signals for innovators and investors on the platform.\\n\\nAction: one thing community members can do to build on this momentum.",
  {hashtag_rule},
  {image_field}
}}"""

    if post_type == 'announcement':
        return f"""{context}

Write a platform announcement for the {industry} community that connects the update to helping innovators build or attract investment.

{structure_note}

Return JSON only:
{{
  "title": "announcement headline (max 12 words)",
  "content": "Motivation: why this update matters to innovators.\\n\\nInsight: what it enables — for building, validation, or investor readiness.\\n\\nAction: what to do with it right now.",
  {hashtag_rule},
  {image_field}
}}"""

    return None


def _slug(query):
    import re
    return re.sub(r'[^a-z0-9]+', '-', query.lower())[:40].strip('-')


def _fetch_image(query):
    """
    Try Pexels API first (requires PEXELS_API_KEY in settings).
    Falls back to picsum.photos seeded on the query (always works, high-quality).
    Returns (filename, ContentFile) or (None, None).
    """
    import urllib.request
    import urllib.parse
    from django.conf import settings

    headers = {'User-Agent': 'OdumaCorp/1.0'}
    slug = _slug(query)
    fname = f"odu_{slug}_{int(timezone.now().timestamp())}.jpg"

    # ── 1. Pexels (relevant photos) ──────────────────────────────
    pexels_key = getattr(settings, 'PEXELS_API_KEY', '')
    if pexels_key:
        try:
            q = urllib.parse.quote(query.strip())
            api_url = f"https://api.pexels.com/v1/search?query={q}&per_page=1&orientation=landscape"
            req = urllib.request.Request(api_url, headers={**headers, 'Authorization': pexels_key})
            with urllib.request.urlopen(req, timeout=10) as r:
                result = json.loads(r.read())
            photos = result.get('photos', [])
            if photos:
                img_url = photos[0]['src']['large2x']
                req2 = urllib.request.Request(img_url, headers=headers)
                with urllib.request.urlopen(req2, timeout=15) as r2:
                    data = r2.read()
                if len(data) > 5000:
                    return fname, ContentFile(data)
        except Exception:
            pass

    # ── 2. Picsum (beautiful random photo, always works) ─────────
    try:
        seed = abs(hash(query)) % 1000
        url = f"https://picsum.photos/seed/{seed}/1200/630"
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req, timeout=15) as r:
            data = r.read()
        if len(data) > 5000:
            return fname, ContentFile(data)
    except Exception:
        pass

    return None, None


class Command(BaseCommand):
    help = 'Generate and publish 2 AI-written Odu posts with matching images'

    def handle(self, *args, **options):
        import anthropic
        from django.conf import settings
        from core.models import CustomUser, Post, Poll, PollOption

        api_key = getattr(settings, 'ANTHROPIC_API_KEY', '')
        if not api_key:
            self.stderr.write('ANTHROPIC_API_KEY not configured.')
            return

        odu = CustomUser.objects.filter(username__iexact='odu').first()
        if not odu:
            self.stderr.write('Odu user not found. Run seed_data first.')
            return

        client = anthropic.Anthropic(api_key=api_key)

        # Pick 2 different types
        pool = list(set(POST_TYPE_POOL))
        types = random.sample(pool, 2)

        published = 0
        for post_type in types:
            industry = random.choice(INDUSTRIES)
            prompt = _build_prompt(post_type, industry)
            if not prompt:
                continue

            try:
                resp = client.messages.create(
                    model='claude-haiku-4-5-20251001',
                    max_tokens=900,
                    system=SYSTEM_PROMPT,
                    messages=[{'role': 'user', 'content': prompt}],
                )
                raw = resp.content[0].text.strip() if resp.content else ''

                # Strip markdown code fences if present
                if raw.startswith('```'):
                    raw = raw.split('\n', 1)[-1]
                    raw = raw.rsplit('```', 1)[0].strip()

                data = json.loads(raw)

                title       = data.get('title', '').strip()[:255]
                content     = data.get('content', '').strip()
                raw_tags    = data.get('hashtags', '').strip()
                image_query = data.get('image_query', '').strip()

                # Ensure every tag token starts with #
                if raw_tags:
                    tokens = raw_tags.split()
                    tags = ' '.join(t if t.startswith('#') else '#' + t for t in tokens)
                    content = content.rstrip() + '\n\n' + tags
                else:
                    tags = ''

                if not content:
                    self.stderr.write(f'Empty content for {post_type}, skipping.')
                    continue

                post = Post.objects.create(
                    user=odu,
                    title=title,
                    content=content,
                    post_type=post_type,
                    industry=industry,
                )

                # Attach image
                if image_query:
                    fname, img_file = _fetch_image(image_query)
                    if fname and img_file:
                        post.image.save(fname, img_file, save=True)
                        self.stdout.write(f'  Image attached: "{image_query}"')
                    else:
                        self.stderr.write(f'  Image fetch failed for query: "{image_query}"')

                # Build poll if needed
                if post_type == 'poll':
                    poll_q  = data.get('poll_question', title)
                    options = data.get('poll_options', [])
                    if options:
                        poll = Poll.objects.create(
                            post=post,
                            question=poll_q[:300],
                            closes_at=timezone.now() + timedelta(days=5),
                        )
                        for i, opt_text in enumerate(options[:6]):
                            PollOption.objects.create(poll=poll, text=opt_text[:150], order=i)

                published += 1
                self.stdout.write(self.style.SUCCESS(
                    f'Published [{post_type}/{industry}] "{title[:60]}"'
                ))

            except json.JSONDecodeError as e:
                self.stderr.write(f'JSON parse error for {post_type}: {e}\nRaw: {raw[:300]}')
            except Exception as e:
                import traceback
                self.stderr.write(f'Error for {post_type}: {e}\n{traceback.format_exc()}')

        self.stdout.write(self.style.SUCCESS(f'Done — {published}/2 posts published.'))
