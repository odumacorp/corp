from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta


ODU_POSTS = [
    # ── Tips ──
    dict(post_type='tip', industry='tech',
         title='Profile tip: add a photo and bio',
         content=(
             "Did you know profiles with a photo get 3× more connection requests?\n\n"
             "Take 5 minutes to:\n"
             "• Upload a clear headshot\n"
             "• Write a 2-sentence bio\n"
             "• Add your industry and company\n\n"
             "Investors check the founder before the idea. Make your first impression count.\n\n"
             "#ProfileTip #Oduma"
         )),
    dict(post_type='tip', industry='finance',
         title='Fundraising tip: lead with traction',
         content=(
             "When pitching to investors, traction beats everything.\n\n"
             "Even small numbers signal momentum:\n"
             "• 50 beta users > 0 users\n"
             "• 3 paying customers > 100 sign-ups\n"
             "• A letter of intent > 'we have interest'\n\n"
             "Lead with what's real. Build from there.\n\n"
             "#FundraisingTip #StartupAfrica"
         )),
    dict(post_type='tip', industry='tech',
         title='Project visibility tip: use a cover image',
         content=(
             "Projects with a high-quality cover image get 3× more views on Oduma Corp.\n\n"
             "Best sizes: 1200 × 630px (16:9 landscape)\n\n"
             "What works:\n"
             "• A clean product mockup or prototype\n"
             "• A problem-solution graphic\n"
             "• An infographic with your key metric\n\n"
             "Free tool: canva.com has startup templates that take 10 minutes.\n\n"
             "#VisibilityTip #ProjectTip"
         )),
    dict(post_type='tip', industry='tech',
         title='Content tip: post 3-5 times per week',
         content=(
             "Consistency beats frequency on Oduma Corp.\n\n"
             "3 solid posts per week > 10 rushed ones.\n\n"
             "Best performing post types:\n"
             "1. Progress updates — real numbers, honest lessons\n"
             "2. Industry insights — what you've observed\n"
             "3. Questions — invite your network to respond\n\n"
             "Start this week. One post. See what happens.\n\n"
             "#ContentTip #Consistency"
         )),

    # ── Resources ──
    dict(post_type='resource', industry='finance',
         title='Free pitch deck resources for African startups',
         content=(
             "Building your pitch deck? Here are the best free resources:\n\n"
             "Templates:\n"
             "• Canva Startup Pitch Deck — canva.com\n"
             "• Gamma.app — AI turns a prompt into a full deck\n"
             "• Google Slides — simple, shareable, free\n\n"
             "Frameworks:\n"
             "• The 10-slide pitch: Problem, Solution, Market, Product, Traction, "
             "Business Model, Team, Competition, Financials, Ask\n\n"
             "Remember: investors fund the team as much as the idea.\n\n"
             "#PitchDeck #StartupResources"
         )),
    dict(post_type='resource', industry='tech',
         title='Free tools to create project images and videos',
         content=(
             "You don't need a designer to look professional. Here's your toolkit:\n\n"
             "Images:\n"
             "• Canva — templates for every format\n"
             "• Adobe Express — professional quality, free\n"
             "• Pexels / Unsplash — free stock photos\n\n"
             "AI image generation:\n"
             "• Microsoft Designer — free AI images\n"
             "• Ideogram — great for text in images\n\n"
             "Video:\n"
             "• Loom — screen + camera recording in seconds\n"
             "• CapCut — mobile video editing with templates\n"
             "• Descript — edit video by editing the transcript\n\n"
             "#FreeTools #ContentCreation"
         )),

    # ── Questions ──
    dict(post_type='question', industry='tech',
         title='What is the single biggest challenge you face as a founder in Africa?',
         content=(
             "We want to hear from you.\n\n"
             "Is it funding? Talent? Market access? Regulation? Infrastructure?\n\n"
             "Drop your answer below — your insight helps shape what Oduma Corp builds next.\n\n"
             "#FounderLife #AfricaStartups #BuildingInAfrica"
         )),
    dict(post_type='question', industry='finance',
         title='Investors: what makes you pass on a startup in the first 60 seconds?',
         content=(
             "To every investor on the platform:\n\n"
             "What's the fastest dealbreaker when reviewing a startup pitch?\n\n"
             "Share one thing that makes you close the deck immediately. "
             "This will help innovators on the platform sharpen their pitch.\n\n"
             "#InvestorInsight #StartupPitch #AfricaVC"
         )),
    dict(post_type='question', industry='tech',
         title='What tool or resource do you wish existed when you started?',
         content=(
             "Think back to day one.\n\n"
             "What tool, resource, or connection would have saved you 6 months?\n\n"
             "Share it below — someone reading this right now needs exactly what you needed then.\n\n"
             "#BuildInPublic #FounderAdvice #StartupTips"
         )),

    # ── Milestones (Odu/platform) ──
    dict(post_type='milestone', industry='tech',
         title='Oduma Corp is live — connecting African innovators and investors',
         content=(
             "Today marks the beginning of something we believe in deeply.\n\n"
             "Oduma Corp is built on a simple premise: the right connections change everything.\n\n"
             "Africa has no shortage of brilliant founders, game-changing ideas, or untapped markets. "
             "What it needs is the infrastructure to match the right people, at the right time.\n\n"
             "That is what we are building.\n\n"
             "If you are an innovator — welcome. Post your project, pitch your idea, find your co-founder.\n"
             "If you are an investor — welcome. Discover your next deal, meet your next founder.\n\n"
             "We are glad you are here.\n\n"
             "#OdumaCorp #AfricaStartups #Innovation"
         )),

    # ── Polls ──
    dict(post_type='poll', industry='tech',
         title='Which industry has the most untapped potential in Africa right now?',
         content='Cast your vote and tell us why in the comments.',
         poll_question='Which industry has the most untapped potential in Africa right now?',
         poll_options=['Agri-tech', 'Fintech', 'Healthtech', 'Edtech', 'Cleantech / Energy'],
         poll_days=7),
    dict(post_type='poll', industry='finance',
         title='What stage are you at in your startup journey?',
         content='We want to understand where most of our community is right now.',
         poll_question='What stage are you at in your startup journey?',
         poll_options=['Idea stage', 'Building MVP', 'Early revenue', 'Scaling', 'Raising funding'],
         poll_days=5),
    dict(post_type='poll', industry='tech',
         title='How did you hear about Oduma Corp?',
         content='Help us understand how our community finds us.',
         poll_question='How did you hear about Oduma Corp?',
         poll_options=['Friend or referral', 'Social media', 'Search / Google', 'Event or conference', 'Other'],
         poll_days=0),

    # ── Opinions ──
    dict(post_type='opinion', industry='finance',
         title='Unpopular opinion: most African startups raise too early',
         content=(
             "Here's a take that may sting: raising venture funding before you have "
             "real revenue often slows you down more than it helps.\n\n"
             "Why?\n"
             "• Investor reporting takes time away from building\n"
             "• Valuations create pressure to grow faster than the market allows\n"
             "• Revenue-based growth forces discipline that equity doesn't\n\n"
             "The best African startups I've seen bootstrapped to $50K MRR before "
             "taking a single external dollar.\n\n"
             "Disagree? Tell me below.\n\n"
             "#StartupOpinion #VentureCapital #AfricaStartups"
         )),
    dict(post_type='opinion', industry='tech',
         title='The best co-founder skill is not technical — it is sales',
         content=(
             "Founders debate this endlessly: do you need a technical co-founder?\n\n"
             "My view: the more important hire is someone who can sell.\n\n"
             "You can hire engineers. You cannot hire founder-level conviction.\n\n"
             "The startups that die are rarely the ones that couldn't build. "
             "They're the ones that couldn't get their first 10 customers.\n\n"
             "Agree or disagree? What did you wish your co-founder was better at?\n\n"
             "#Cofounder #StartupAdvice #Sales"
         )),

    # ── Articles ──
    dict(post_type='article', industry='tech',
         title='How to get your first investor connection on Oduma Corp',
         content=(
             "You have created your account. Now what?\n\n"
             "Here is the fastest path to a meaningful investor connection:\n\n"
             "1. Complete your profile — photo, bio, industry, company\n"
             "   Investors check the founder before the idea.\n\n"
             "2. Post your project — a clear title, problem statement, and funding ask\n"
             "   Add a cover image and attach a pitch deck.\n\n"
             "3. Browse the Investor directory — filter by industry that matches yours\n"
             "   Read their profile to understand what they back.\n\n"
             "4. Send a personalised connection request — mention one specific thing "
             "from their profile\n\n"
             "5. Once connected — message them with a one-paragraph summary, "
             "not your full deck\n\n"
             "The goal of every touchpoint is the next touchpoint. Not a yes.\n\n"
             "#InvestorRelations #Fundraising #OdumaGuide"
         )),
    dict(post_type='article', industry='tech',
         title='5 things investors look at before reading your pitch deck',
         content=(
             "Before an investor opens your deck, they have already formed an opinion. "
             "Here's what they check:\n\n"
             "1. Your profile photo and headline\n"
             "   A blurry photo or an empty bio signals you don't take presentation seriously.\n\n"
             "2. Your industry and location\n"
             "   Most investors have a thesis. If you're outside it, the deck won't change that.\n\n"
             "3. Your connections and activity\n"
             "   An active profile signals you're engaged and building in public.\n\n"
             "4. What others say about you\n"
             "   Endorsements, collaboration history, and proposals sent signal credibility.\n\n"
             "5. Your project title and one-liner\n"
             "   If they can't explain what you do in one sentence after reading yours, "
             "you've already lost them.\n\n"
             "Fix these five things before you send a single cold message.\n\n"
             "#InvestorReady #PitchDeck #StartupAfrica"
         )),
]


class Command(BaseCommand):
    help = 'Seed Odu bot posts — tips, resources, polls, questions, and articles'

    def handle(self, *args, **options):
        from core.models import CustomUser, Post, Poll, PollOption

        odu = CustomUser.objects.filter(username__iexact='odu').first()
        if not odu:
            self.stderr.write('Odu user not found. Run seed_data first.')
            return

        created = 0
        for spec in ODU_POSTS:
            poll_question = spec.pop('poll_question', None)
            poll_options  = spec.pop('poll_options', [])
            poll_days     = spec.pop('poll_days', 3)

            if Post.objects.filter(user=odu, title=spec['title']).exists():
                continue

            post = Post.objects.create(user=odu, **spec)

            if spec['post_type'] == 'poll' and poll_options:
                closes_at = timezone.now() + timedelta(days=poll_days) if poll_days else None
                poll = Poll.objects.create(
                    post=post,
                    question=poll_question or spec['title'],
                    closes_at=closes_at,
                )
                for i, opt_text in enumerate(poll_options):
                    PollOption.objects.create(poll=poll, text=opt_text, order=i)

            created += 1

        self.stdout.write(self.style.SUCCESS(f'Created {created} Odu posts.'))
