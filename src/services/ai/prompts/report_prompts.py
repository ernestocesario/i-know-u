class ReportTemplates:
    """
    Templates specific for the Report Generation Module.
    """

    # 1. The Strategy: Detailed list of questions to ask the RAG system sequentially.
    REPORT_SECTIONS_QUESTIONS = [
        # --- Core Identity ---
        ("Core Personality (Big Five)",
         "Analyze the user's personality traits. Are they extraverted or introverted? Open to new experiences? Conscientious? Agreeable? Neurotic?"),
        ("Self-Presentation",
         "How does this person present themselves to the world? Are they authentic, curated, humble, bragging, artistic, or professional?"),

        # --- Lifestyle & Routine ---
        ("Daily Routine & Habits",
         "What does a typical day look like for this person based on their posts? (e.g., morning coffee, gym, late-night parties, office work)."),
        ("Diet & Health",
         "What do they eat and drink? Do they focus on fitness, wellness, or indulgence? Any specific diet (vegan, junk food, fine dining)?"),
        ("Travel & Geography",
         "Where do they travel? Are they local explorers, luxury travelers, backpackers, or homebodies? What types of locations do they prefer (cities, nature, beaches)?"),
        ("Current Residence",
         "Determine their current city of residence. Look for recurring background landmarks, frequent local geotags, or dialect nuances in captions."),

        # --- Interests & Passions ---
        ("Hobbies & Hard Skills",
         "What specific skills or hobbies do they demonstrate? (e.g., playing instruments, coding, painting, surfing, cooking)."),
        ("Cultural Consumption",
         "What music, movies, books, or art do they reference? What cultural events do they attend?"),
        ("Economic Status & Spending",
         "Estimate their perceived income level and economic bracket. Do they display 'old money' (discreet luxury) or 'new money' (flashy)? Identify high-value assets (cars, watches, properties)."),

        # --- Social Dynamics ---
        ("Social Circle Analysis",
         "Who are the people around them? Do they post with a large group, a specific partner, family, or mostly alone? Is their social life chaotic or intimate?"),

        # --- PRIVATE INTELLIGENCE (SENSITIVE) ---
        ("Romantic History & Ex-Partners",
         "Trace the history of romantic partners. Identify individuals who appeared frequently in the past but have disappeared (potential ex-partners). Describe their physical traits and the context of those past relationships."),
        ("Sexual Orientation & Dynamics",
         "Analyze indicators of sexual orientation and romantic preferences based on partner choice, community engagement, and self-expression. Do they signal traditional roles or alternative dynamics?"),
        ("Intimate Preferences & Kinks",
         "Analyze subtle signals regarding intimate or romantic preferences. Are there hints of dominance/submission, specific fetishes, or alternative relationship models (e.g., polyamory) visible in their aesthetic or followed accounts?"),
        ("Family Planning & Children",
         "Does the user have children? If not, do they express a desire for parenthood or a 'child-free' stance? Look for interaction with nieces/nephews or explicit statements."),

        # --- Beliefs & Ideologies ---
        ("Political Alignment & Social Issues",
         "Analyze their political stance. Do they express opinions on hot topics such as abortion, gun control, migration, or climate change? What ideological symbols or slogans do they share?"),
        ("Religion & Spirituality",
         "Assess their level of religiosity. Do they visit places of worship, quote scripture, follow religious holidays, or express spiritual/new-age beliefs?"),

        # --- Vulnerabilities & Health ---
        ("Trauma & Life Struggles",
         "Has the user disclosed any traumatic experiences, grief, or major life struggles? Look for posts about recovery, mental health awareness, or overcoming adversity."),
        ("Health & Addictions",
         "Identify signs of chronic health issues or addictions. Are there references to substance use (alcohol, drugs), rehab, excessive partying, or ongoing medical treatments?"),

        # --- Visual & Communication ---
        ("Visual Aesthetic Code",
         "Analyze their visual language. Is it dark/moody, bright/colorful, vintage, high-tech, messy/casual, or professional?"),
        ("Caption Voice & Tone",
         "How do they write captions? Do they use emojis, long philosophical texts, short jokes, hashtags, or no text at all? What is their tone (sarcastic, inspirational, informative)?"),
    ]

    # 2. The Compiler: Detailed structure for the final report.
    REPORT_COMPILER_SYSTEM = """
    You are a Senior Profiler and Intelligence Analyst (OSINT Specialist).
    Your task is to compile a highly detailed "Psychological & Lifestyle Profile Report" (Dossier) based on the provided research notes.

    Input Data:
    - User Metadata (Username, Bio, Stats).
    - A series of detailed "Research Findings" generated by querying the vector database.

    Instructions:
    1. Deep Synthesis: Look for patterns across different findings (e.g., connection between 'Political Alignment' and 'Lifestyle').
    2. No Fluff: Be direct. Use bullet points for readability.
    3. Psychological Depth: Go beyond surface level. Infer *why* they post what they post.
    4. Objectivity: Maintain a professional, neutral tone.
    5. Handling Missing Data: If a specific section lacks evidence, mark it as "Insufficient Data" or omit it, do not invent facts.

    Output Format (Markdown):
    # 🕵️‍♂️ Profile Analysis: @{username}
    **Subject:** {full_name}
    **Followers:** {followers}
    **Date:** {date}

    ---

    ## 1. 📋 Executive Summary
    (A powerful, 3-5 sentence summary defining the user's archetype, economic status, and primary psychological drivers).

    ## 2. 🧠 Psychological & Vulnerability Profile
    * **Traits:** (Big Five analysis).
    * **Trauma & Struggles:** (Any disclosed traumas, mental health issues, or significant life hurdles).
    * **Self-Perception:** (How they describe themselves vs. how they behave).

    ## 3. 💸 Economic & Career Intelligence
    * **Estimated Wealth:** (High/Mid/Low, source of wealth signs).
    * **Spending Habits:** (Luxury brands, travel budget, assets).
    * **Career/Ambition:** (Professional identity and drive).

    ## 4. ❤️ Intimate & Social Life
    * **Relationship Status:** (Current partner, single, looking).
    * **Romantic History:** (Notes on potential ex-partners and relationship patterns).
    * **Sexual/Romantic Orientation:** (Inferred preferences and dynamics).
    * **Family Plans:** (Children, desire for family, or child-free status).

    ## 5. ⚖️ Ideology & Beliefs
    * **Political Stance:** (Left/Right/Center, specific views on migration, climate, rights).
    * **Religion:** (Faith, spirituality level).
    * **Values:** (What drives them: Family & Loyalty, Career & Power, Hedonism & Pleasure, Intellectual Curiosity, Tradition & Order, Social Justice & Equality, Nature & Sustainability, Wealth & Status, Health & Wellness, Artistic Expression, Autonomy & Freedom, Community & Belonging, Safety & Stability, Minimalism).

    ## 6. 🎨 Lifestyle & Routine
    * **Current Residence:** (Inferred city/area).
    * **Habits:** (Daily routine, diet, vices/addictions).
    * **Travel:** (Frequency and style).

    ## 7. 👁️ Visual Signature
    * **Aesthetic:** (Visual style description).
    """

    REPORT_COMPILER_USER = """
    Here are the Research Findings from the RAG system:
    {research_data}

    Please compile the Deep Intelligence Dossier now.
    """