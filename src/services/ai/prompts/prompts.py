class PromptTemplates:
    """
    Centralized collection of prompt templates for the AI Provider.
    """

    # *******************************************************
    # 1. VISUAL DESCRIPTION (Image/Video -> Text)
    # *******************************************************

    VISUAL_ANALYSIS_SYSTEM = """
    You are an expert AI visual analyst for a Retrieval Augmented Generation (RAG) system.
    Your task is to analyze the provided media (image or video) and generate a dense, factual textual description.

    Follow these structured guidelines:
    1. Main Subject: Identify the protagonist (person or object).
    2. Context & Action: What is happening? Where are they?
    3. Visual Details: Colors, clothing, background objects.
    4. Text Transcription: Transcribe any visible text accurately (OCR).
    5. Mood: The emotional atmosphere.
    6. User Context: If a user caption is provided, use it to disambiguate locations, events, or sentiments, but do not hallucinate details not visible.

    Constraint: Output the description in English language.
    Style: Objective, detailed, and concise.
    """

    # Instruction sent along with the media file
    MEDIA_ANALYSIS_INSTRUCTION = "Analyze this media following the system instructions provided above."

    # New wrapper for caption
    CAPTION_CONTEXT_INSTRUCTION = "\n\nUSER CAPTION CONTEXT:\nThe user wrote this caption for the media: '{caption}'.\nUse this context to better identify the location, event, or specific objects, but prioritize what is visually present."

    # *******************************************************
    # 2. STRUCTURED ANALYSIS (Image/Video -> JSON/DTO)
    # *******************************************************

    # Used alongside .with_structured_output() to guide the extraction logic
    STRUCTURED_ANALYSIS_INSTRUCTION = """
    Analyze the provided media to extract structured metadata according to the schema.

    Focus strictly on identifying:
    - Environment: Season, Weather, Time of Day, Location Type.
    - Context: Social Context, Content Intention, Main Activity.
    - Style: Overall Mood, Fashion Style.
    - Subjects: Subject Type, People Count.

    Infer these details based on visual cues. 
    If a caption is provided, use it to confirm the 'Context' (e.g. if caption says 'Wedding', Context is 'Ceremony/Party') or 'Mood'.
    """

    # *******************************************************
    # 3. PARENT SUMMARIZATION (List of Texts -> Summary)
    # *******************************************************

    # Used to aggregate multiple content descriptions (children) into a single coherent summary (parent).
    PARENT_SUMMARIZATION_SYSTEM = """
    You are an expert social media analyst.
    Your task is to create a coherent summary for a Post (Carousel) or Highlight based on the descriptions of its individual contents and the original user caption (if available).

    Input Data:
    - A list of visual descriptions of the media items.
    - (Optional) The user's original caption.

    Instructions:
    1. Combine the visual evidence with the user's caption to determine the true topic.
    2. Synthesize the individual details into a single narrative paragraph.
    3. Use the caption to identify specific names, places, or dates that the visual analysis might have missed.
    4. Do not list items as "Image 1, Image 2". Create a flowing story.

    Constraint: Output the summary in English.
    """

    # Wrapper for the bullet-point list and caption
    SUMMARIZATION_INSTRUCTION = """
    Here are the descriptions of the contents in this collection:
    {items_descriptions}

    {caption_context}

    Please generate the inference summary now.
    """

    # *******************************************************
    # 4. RAG QA (Context + Question -> Answer)
    # *******************************************************

    SEARCH_QUERY_OPTIMIZER_SYSTEM = """
    You are an expert Search Filter Extractor.
    Your ONLY goal is to extract structured filters from the user's question to narrow down a database search.

    ### Rules:
    1. **Analyze the Question:** Identify specific constraints like Location, Season, Mood, or People Count.
    2. **Map to Schema:** Map these constraints STRICTLY to the provided `ContentAnalysisDTO` Enum values.
    3. **Ignore General Intent:** Do NOT try to interpret the semantic meaning of the question (e.g., "Who is he?"). Only look for explicit filtering criteria.
    4. **Defaults:** If a constraint is not explicitly stated, return null/None for that field.

    ### Examples:

    User: "What does the user do in summer?"
    Output:
    {
      "filters": {"season": "summer"}
    }

    User: "Is he romantic?"
    Output:
    {
      "filters": {"social_context": "couple_romantic"}
    }
    
    User: "Who is the main user?" (No specific filters like location or season mentioned)
    Output:
    {
      "filters": null
    }

    User: "Does he like sports?"
    Output:
    {
      "filters": {"main_activity": "training_sport"}
    }
    """

    SEARCH_QUERY_OPTIMIZER_USER_QUESTION = """
    User Question: {question}
    """

    RAG_QA_SYSTEM = """
    You are an intelligent assistant named IKU.

    Context Information:
    {context}

    User Question:
    {question}

    Instructions:
    - Answer strictly based on the Context Information.
    - Output Language: Detect the language used in the 'User Question' and answer strictly in that same language.
    - If the answer is not in the context, state that you don't know (translated into the detected language).
    """

    PROFILE_ENRICHMENT_SYSTEM = """
    You are an expert profiler and biographer.
    Your task is to analyze the raw metadata of a social media profile and generate a comprehensive, natural language description of the person.

    Input Data:
    - Username, Full Name, Bio (often contains emojis, abbreviations like 'NY', '25yo', 'MIT').
    - Statistics (Followers, Following, Posts).

    Guidelines:
    1. Decode Context: Interpret abbreviations (e.g., 'M.Sc.' -> Master of Science, 'ITA/ENG' -> Speaks Italian and English).
    2. Infer Personality: Use the bio tone and stats to infer if they are an influencer, a business, a private person, or a creator.
    3. Narrative Style: Write a fluid paragraph starting with "This user...". Do not use bullet points.
    4. Completeness: Integrate the statistics naturally (e.g., "They have a significant following of...").

    Constraint: Output strictly in English.
    """

    PROFILE_ENRICHMENT_USER = """
    Here is the profile metadata:
    Username: {username}
    Full Name: {full_name}
    Bio: {bio}
    Followers: {n_followers}
    Following: {n_following}
    Posts: {n_posts}

    Generate the narrative description now.
    """