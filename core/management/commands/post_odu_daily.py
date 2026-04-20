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

SYSTEM_PROMPT = """You are Odu — the AI voice of Oduma Corp, a platform connecting African innovators and investors.
Your posts are authoritative, warm, and practical. You speak to founders, investors, and builders across Africa.
Tone: direct, insightful, never corporate-speak. No emojis. No hashtag spam (max 2 relevant ones at the end).
Always write in full sentences. First-person plural ("we") or second-person ("you") where natural.

IMPORTANT: Every response must include an "image_query" field — 3-5 comma-separated English keywords
that describe a relevant, professional stock photo for this post. Think visually: what scene or object
best illustrates the topic? Examples: "African startup team meeting", "mobile payment Kenya",
"solar panel installation Africa", "dartboard bullseye focus", "laptop open office team"."""


def _build_prompt(post_type, industry):
    today = timezone.now().strftime('%A %d %B %Y')
    context = f"Today is {today}. Industry focus: {industry}. Post type: {post_type}."
    image_field = '"image_query": "3-5 keywords describing a relevant professional stock photo"'

    if post_type == 'tip':
        return f"""{context}

Write a practical, specific tip for African startup founders or investors. It must be immediately actionable.

Return JSON only:
{{
  "title": "short tip headline (max 12 words)",
  "content": "the tip (150-250 words, 3-4 short paragraphs, ends with a clear action step)",
  "hashtags": "2 relevant hashtags",
  {image_field}
}}"""

    if post_type == 'question':
        return f"""{context}

Write a thought-provoking open question for the Oduma Corp community. Invite genuine reflection from founders and investors.

Return JSON only:
{{
  "title": "the question as a title (max 15 words)",
  "content": "2-3 sentences of context that set up the question and invite responses (80-120 words)",
  "hashtags": "2 relevant hashtags",
  {image_field}
}}"""

    if post_type == 'opinion':
        return f"""{context}

Write a bold, slightly contrarian opinion about startups, investing, or building in Africa. End with "Agree or disagree? Tell us below."

Return JSON only:
{{
  "title": "punchy opinion headline (max 12 words)",
  "content": "the opinion piece (180-250 words, 3-4 paragraphs)",
  "hashtags": "2 relevant hashtags",
  {image_field}
}}"""

    if post_type == 'resource':
        return f"""{context}

Share 3-5 genuinely useful free resources (tools, platforms, frameworks) for African founders or investors in {industry}. Include name and one-line description.

Return JSON only:
{{
  "title": "resource list headline (max 12 words)",
  "content": "intro sentence, the list, closing sentence (150-200 words total)",
  "hashtags": "2 relevant hashtags",
  {image_field}
}}"""

    if post_type == 'article':
        return f"""{context}

Write a short, high-value how-to or explainer article for the {industry} sector.

Return JSON only:
{{
  "title": "article headline (max 12 words)",
  "content": "the article (250-320 words, numbered or clear paragraph structure)",
  "hashtags": "2 relevant hashtags",
  {image_field}
}}"""

    if post_type == 'poll':
        return f"""{context}

Create a compelling poll for African founders and investors about the {industry} sector. Options must be genuinely distinct.

Return JSON only:
{{
  "title": "poll headline (max 12 words)",
  "content": "1-2 sentences inviting people to vote and comment (40-60 words)",
  "poll_question": "the poll question (max 20 words)",
  "poll_options": ["option 1", "option 2", "option 3", "option 4"],
  "hashtags": "2 relevant hashtags",
  {image_field}
}}"""

    if post_type == 'milestone':
        return f"""{context}

Write a brief platform or community milestone post celebrating growth or achievement.

Return JSON only:
{{
  "title": "milestone headline (max 12 words)",
  "content": "the milestone post (100-150 words)",
  "hashtags": "2 relevant hashtags",
  {image_field}
}}"""

    if post_type == 'announcement':
        return f"""{context}

Write a short platform announcement about an upcoming feature, event, or improvement for the {industry} community.

Return JSON only:
{{
  "title": "announcement headline (max 12 words)",
  "content": "the announcement (100-150 words)",
  "hashtags": "2 relevant hashtags",
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
                tags        = data.get('hashtags', '').strip()
                image_query = data.get('image_query', '').strip()

                if tags:
                    content = content.rstrip() + '\n\n' + tags

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
