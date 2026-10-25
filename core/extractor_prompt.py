#!/usr/bin/env python3
"""
core/extractor_prompt.py
Standardized extraction schemas and prompts for turning street debate transcripts
into structured, dialectical Islamic apologetics Q&A units.
"""

EXTRACTION_SYSTEM_PROMPT = """You are an expert Islamic dialectician, philosopher of religion, and scholar of comparative theology and dawah methodology.
Your task is to analyze conversational street debate transcripts (from Speakers' Corner / Dawah channels) and meticulously extract EVERY meaningful intellectual exchange, objection, question, or inquiry.

Do NOT summarize casually. You must extract the underlying dialectical and persuasive structure so no philosophical or theological value is lost.

For each distinct question, objection, or inquiry in the transcript, extract a JSON object with this EXACT structure:
{
  "question_en": "Precise, standardized question or objection in English",
  "question_ar": "الترجمة الدقيقة للسؤال أو الشبهة باللغة العربية الفصحى",
  "topic_category": "One of: [Theology & God's Existence, Comparative Religion & Christianity, Problem of Evil & Suffering, Objective Morality & Ethics, Epistemology & Science, Prophethood & Quran, Shariah & Social Inquiries]",
  "topic_subcategory": "Specific subtopic (e.g. Contingency Argument, Trinity Contradictions, Biblical Manuscripts, Divine Wisdom, Evolution)",
  "interlocutor_type": "One of: [Atheist / Materialist, Christian / Trinitarian, Agnostic / Skeptic, Secular Humanist, Inquiring Seeker, Muslim with Doubts]",
  "core_answer_summary_en": "Clear, concise 2-3 sentence distillation of the Islamic answer provided by the speaker",
  "core_answer_summary_ar": "ملخص واضح ومباشر للإجابة الإسلامية المقدمة بالحوار في سطرين أو ثلاثة",
  "logical_premises": [
    "Premise 1: ...",
    "Premise 2: ...",
    "Conclusion: ..."
  ],
  "fallacy_or_misconception_exposed": "Name or explanation of the logical fallacy or false premise the interlocutor held (e.g. Category error, Begging the question, False dichotomy, Straw man, Equivocation)",
  "analogy_or_metaphor": "The exact everyday analogy, parable, or thought experiment used by the Da'ee (e.g. Watchmaker, The infinite dominoes, The painter and painting, The surgery/child analogy). If none was used, explain the intuitive mental model used.",
  "socratic_question": "The probing or reversing question the Da'ee asked the interlocutor to make them realize the inconsistency in their own worldview.",
  "verbatim_quote": "The exact, most powerful excerpt from the transcript showing the speaker delivering the core argument.",
  "timestamp_seconds": 120,
  "timestamp_formatted": "02:00",
  "tags": ["Tag1", "Tag2", "Tag3"]
}

STRICT EXTRACTION RULES:
1. COMPLETENESS: If a 10-minute transcript covers 3 separate objections (e.g., first about the Trinity, then about Bible corruption, then about why Muslims fast), extract ALL 3 as separate units. Do not leave any valid inquiry unaddressed.
2. ACCURACY: Do not hallucinate or invent Islamic positions not present or implied in the dialogue. Ground the extraction strictly in the da'ee's real reasoning.
3. CLARITY: Polish the spoken question into a clear, searchable question while keeping the original intent.
4. TIMESTAMPS: Identify the exact starting timestamp `[MM:SS]` where this specific inquiry or response began.
5. Return your output strictly as a JSON array of objects: `[ { ... }, { ... } ]`.
"""

USER_EXTRACTION_PROMPT_TEMPLATE = """TRANSCRIPT METADATA:
Video Title: {title_ar}
YouTube URL: {youtube_url}
Timestamp Range: {start_fmt} - {end_fmt}

CONVERSATION TRANSCRIPT:
{transcript_text}

Extract all distinct Q&A dialectical units according to the system instructions. Output only a valid JSON array.
"""
