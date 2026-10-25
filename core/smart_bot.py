#!/usr/bin/env python3
"""
core/smart_bot.py
Intelligent, zero-LLM automated dialogue assistant.
Uses deterministic NLP, bilingual intent classification, token intersection,
and pre-analyzed dialectical answer keys to provide instant, persuasive answers
with verbatim evidence and exact YouTube timestamp links.
"""

import re
import json
from typing import List, Dict, Any, Optional, Tuple
from db.database import search_qa, get_db_connection

# Category translations
CATEGORY_TRANSLATIONS = {
    "Theology & God's Existence": "العقيدة ووجود الله",
    "Problem of Evil & Suffering": "مشكلة الشر والمعاناة",
    "Comparative Religion & Christianity": "مقارنة الأديان والنصرانية",
    "Objective Morality & Ethics": "الأخلاق الموضوعية والإلحاد",
    "Epistemology & Science": "المعرفة والعلم التجريبي",
    "Shariah & Social Inquiries": "الشريعة والشبهات الاجتماعية"
}

INTERLOCUTOR_TRANSLATIONS = {
    "Atheist / Materialist": "ملحد / مادي",
    "Christian / Trinitarian": "مسيحي / نصراني",
    "Agnostic / Skeptic": "لاأدري / متشكك",
    "Secular Humanist / Christian": "علماني / نصراني",
    "Secular Humanist": "علماني إنسانوي",
    "Inquiring Seeker": "باحث عن الحق",
    "Muslim with Doubts": "مسلم يطلب دليلاً"
}

# Bilingual Intent Concept Graph
THEOLOGICAL_INTENT_MAP = [
    {
        "category": "Theology & God's Existence",
        "subcategory": "First Cause & Who Created God",
        "keywords_en": ["who created god", "first cause", "beginning of universe", "infinite regress", "category mistake", "contingency", "kalam"],
        "keywords_ar": ["من خلق الله", "السبب الاول", "بدايه الكون", "تسلسل لا نهائي", "خالق الله", "الواجب الوجود", "السببيه", "علة الوجود"],
        "default_question_id": "theology_001"
    },
    {
        "category": "Problem of Evil & Suffering",
        "subcategory": "Divine Wisdom & Purpose of Suffering",
        "keywords_en": ["problem of evil", "why suffering", "innocent children", "cancer", "evil and good", "bad things happen", "god allows evil"],
        "keywords_ar": ["مشكله الشر", "لماذا الالم", "معاناه الاطفال", "الشر والخير", "لماذا يسمح الله بالشر", "المصائب", "حكمه الشر"],
        "default_question_id": "evil_001"
    },
    {
        "category": "Comparative Religion & Christianity",
        "subcategory": "Trinity Contradictions & Jesus in Islam",
        "keywords_en": ["trinity", "jesus is god", "son of god", "father son", "three in one", "crucifixion", "god died"],
        "keywords_ar": ["التثليث", "يسوع هو الله", "ابن الله", "الثالوث", "ثلاثه في واحد", "صلب المسيح", "موت الله", "الوهيه المسيح"],
        "default_question_id": "trinity_001"
    },
    {
        "category": "Comparative Religion & Christianity",
        "subcategory": "Textual Preservation: Quran vs Bible",
        "keywords_en": ["bible changed", "quran preserved", "manuscripts", "bible corruption", "anonymous authors", "council of nicaea"],
        "keywords_ar": ["تحريف الانجيل", "حفظ القران", "مخطوطات الكتاب المقدس", "التحريف", "مجمع نيقيه", "اسانيد القران"],
        "default_question_id": "preservation_001"
    },
    {
        "category": "Objective Morality & Ethics",
        "subcategory": "Grounding Morality Without God",
        "keywords_en": ["objective morality", "moral without god", "atheist ethics", "subjective morals", "good and bad", "right and wrong"],
        "keywords_ar": ["مصدر الاخلاق", "اخلاق الملحد", "الاخلاق بدون اله", "الاخلاق الموضوعيه", "النسبيه الاخلاقيه"],
        "default_question_id": "morality_001"
    },
    {
        "category": "Epistemology & Science",
        "subcategory": "Scientism vs Metaphysics",
        "keywords_en": ["science proves", "scientism", "empirical proof", "scientific method", "only believe in science", "evolution vs creation"],
        "keywords_ar": ["العلمويه", "اثبات علمي", "المنهج التجريبي", "التطور والخلق", "هل العلم يفسر كل شيء"],
        "default_question_id": "epist_001"
    },
    {
        "category": "Shariah & Social Inquiries",
        "subcategory": "Women in Islam & Social Jurisprudence",
        "keywords_en": ["women in islam", "hijab", "four wives", "polygamy", "inheritance", "female rights", "oppression"],
        "keywords_ar": ["المراه في الاسلام", "الحجاب", "تعدد الزوجات", "حقوق المراه", "الميراث", "اضطهاد المراه"],
        "default_question_id": "women_001"
    }
]


def normalize_text(text: str) -> str:
    if not text:
        return ""
    t = text.strip().lower()
    t = re.sub(r"[\u064B-\u065F\u0670]", "", t)
    t = t.replace("أ", "ا").replace("إ", "ا").replace("آ", "ا").replace("ء", "")
    t = t.replace("ة", "ه").replace("ى", "ي").replace("ؤ", "و").replace("ئ", "ي")
    t = re.sub(r"[^\w\s\u0600-\u06FF]", " ", t)
    t = re.sub(r"\s+", " ", t).strip()
    return t


def detect_language(text: str) -> str:
    arabic_chars = len(re.findall(r"[\u0600-\u06FF]", text))
    latin_chars = len(re.findall(r"[a-zA-Z]", text))
    return "ar" if arabic_chars > latin_chars else "en"


def compute_match_score(query_norm: str, item: Dict[str, Any], query_lang: str) -> float:
    score = 0.0
    q_tokens = set(query_norm.split())
    if not q_tokens:
        return 0.0

    target_q = normalize_text(item.get("question_ar" if query_lang == "ar" else "question_en", ""))
    target_tokens = set(target_q.split())

    if query_norm in target_q:
        score += 80.0

    overlap = len(q_tokens.intersection(target_tokens))
    if overlap > 0:
        score += (overlap / len(q_tokens)) * 50.0

    summary_text = normalize_text(
        (item.get("core_answer_summary_ar") if query_lang == "ar" else item.get("core_answer_summary_en")) or ""
    )
    summary_tokens = set(summary_text.split())
    sum_overlap = len(q_tokens.intersection(summary_tokens))
    score += sum_overlap * 5.0

    tags = [normalize_text(t) for t in item.get("tags", [])]
    for tag in tags:
        if tag in query_norm or any(tok in tag for tok in q_tokens):
            score += 15.0

    return score


class SmartDialecticBot:
    def answer_query(self, user_query: str) -> Dict[str, Any]:
        user_query = user_query.strip()
        if not user_query:
            return {
                "status": "empty",
                "message": "Please enter a question or topic to search."
            }

        query_lang = detect_language(user_query)
        query_norm = normalize_text(user_query)

        candidates = search_qa(query=user_query, limit=20)
        if not candidates:
            candidates = search_qa(query="", limit=50)

        intent_category = None
        for intent in THEOLOGICAL_INTENT_MAP:
            kw_list = intent["keywords_ar"] if query_lang == "ar" else intent["keywords_en"]
            for kw in kw_list:
                norm_kw = normalize_text(kw)
                if norm_kw in query_norm or all(part in query_norm for part in norm_kw.split()):
                    intent_category = intent["category"]
                    break
            if intent_category:
                break

        scored_candidates = []
        for c in candidates:
            sc = compute_match_score(query_norm, c, query_lang)
            if intent_category and c.get("topic_category") == intent_category:
                sc += 25.0
            scored_candidates.append((sc, c))

        scored_candidates.sort(key=lambda x: x[0], reverse=True)

        if scored_candidates and scored_candidates[0][0] > 5.0:
            best_match = scored_candidates[0][1]
            related = [c[1] for c in scored_candidates[1:4] if c[0] > 0]
            
            return {
                "status": "success",
                "query": user_query,
                "language": query_lang,
                "confidence_score": round(scored_candidates[0][0], 2),
                "matched_qa": best_match,
                "response_package": self._format_response_package(best_match, query_lang),
                "related_questions": [
                    {
                        "id": r["id"],
                        "question": r["question_ar"] if query_lang == "ar" else r["question_en"],
                        "category": CATEGORY_TRANSLATIONS.get(r["topic_category"], r["topic_category"]) if query_lang == "ar" else r["topic_category"]
                    } for r in related
                ]
            }
        else:
            top_default = candidates[0] if candidates else None
            return {
                "status": "partial_match",
                "query": user_query,
                "language": query_lang,
                "message": "لم أجد تطابقاً حرفياً مباشراً، ولكن هذه أقرب مناظرة فلسفية تجيب عن سياق سؤالك:" if query_lang == "ar" else "No exact match was found, but here is the closest philosophical dialogue addressing your inquiry:",
                "matched_qa": top_default,
                "response_package": self._format_response_package(top_default, query_lang) if top_default else None,
                "related_questions": [
                    {
                        "id": c["id"],
                        "question": c["question_ar"] if query_lang == "ar" else c["question_en"],
                        "category": CATEGORY_TRANSLATIONS.get(c["topic_category"], c["topic_category"]) if query_lang == "ar" else c["topic_category"]
                    } for c in candidates[:4]
                ]
            }

    def _format_response_package(self, qa: Dict[str, Any], lang: str) -> Dict[str, Any]:
        is_ar = (lang == "ar")
        premises = qa.get("logical_premises_ar") if is_ar and qa.get("logical_premises_ar") else qa.get("logical_premises", [])
        analogy = qa.get("analogy_or_metaphor_ar") if is_ar and qa.get("analogy_or_metaphor_ar") else qa.get("analogy_or_metaphor")
        socratic = qa.get("socratic_question_ar") if is_ar and qa.get("socratic_question_ar") else qa.get("socratic_question")
        verbatim = qa.get("verbatim_quote_ar") if is_ar and qa.get("verbatim_quote_ar") else qa.get("verbatim_quote")
        cat = CATEGORY_TRANSLATIONS.get(qa.get("topic_category"), qa.get("topic_category")) if is_ar else qa.get("topic_category")
        interlocutor = INTERLOCUTOR_TRANSLATIONS.get(qa.get("interlocutor_type"), qa.get("interlocutor_type")) if is_ar else qa.get("interlocutor_type")

        return {
            "title": qa.get("question_ar" if is_ar else "question_en"),
            "interlocutor": interlocutor,
            "category": cat,
            "summary": qa.get("core_answer_summary_ar" if is_ar else "core_answer_summary_en"),
            "logical_premises": premises,
            "fallacy_exposed": qa.get("fallacy_or_misconception_exposed_ar" if is_ar else "fallacy_or_misconception_exposed"),
            "analogy": analogy,
            "socratic_question": socratic,
            "verbatim_quote": verbatim,
            "video_title": qa.get("video_title_ar"),
            "timestamp": qa.get("timestamp_formatted"),
            "timestamp_url": qa.get("timestamp_url")
        }


smart_bot = SmartDialecticBot()
