# 🕌 Dawah Dialectics (جدليات الدعوة الإسلامية)
### Applied Islamic Apologetics Knowledge Base & Dialectical Search Engine

Transforming 2,360+ live street debate and dialogue transcripts (over 6 million words) from channels like *SCDawah Arabic* into an accurate, structured, searchable **Islamic Apologetics Q&A Engine & Smart Assistant**.

---

## 🌟 Key Features

1. **Dual-Language Interface (English & العربية)**:
   - Instant toggle between English and Arabic with full dynamic RTL / LTR layout switching.
   - Dual-language search: search in Arabic or English to find matching dialectical arguments.

2. **Accurate Street Dialogue Distillation**:
   - Reconstructs noisy, fragmented transcripts without data loss using overlapping conversational windows.
   - Preserves **logical deductive sequences** (Premises 1, 2, Conclusion), **intuitive analogies/parables**, and **socratic counter-questions**.
   - Every answer is linked to its exact **YouTube video timestamp** (`watch?v=...&t=...s`) so the user can verify the actual spoken dialogue in real life!

3. **Zero-LLM Instant Smart Assistant**:
   - Zero-cost, zero-latency automated smart bot running entirely offline on your device.
   - Uses deterministic NLP, theological intent classification, token intersection, and pre-indexed answer keys to deliver structured dialectical responses in milliseconds.

4. **Zero-Cost Scaling via Local Colab GPU (No API Keys)**:
   - Includes a ready-to-run notebook ([`dawah_knowledge_extractor_colab.ipynb`](file:///c:/Users/ibrah/Documents/GitHub/yt-ch/dawah_knowledge_extractor_colab.ipynb)) to batch-process all 2,360+ videos on Google Colab using a **local open-weight AI model (`Qwen/Qwen2.5-7B-Instruct` in 4-bit)** running directly on the free **Nvidia T4 GPU**.
   - **Zero API keys, zero rate limits, zero costs**.
   - Checkpointing directly into mounted **Google Drive** ensures that multi-day sessions resume seamlessly each day without losing a single finished video.

---

## 🚀 Quick Start (Running Locally)

### 1. Launch the Web Application
```powershell
python run_app.py
```
Open your browser at **`http://127.0.0.1:8000`** to browse questions, filter by topic, or chat with the assistant.

### 2. Run Automated Verification Tests
```powershell
python tests/test_endpoints.py
```

---

## 📂 Repository Structure

```
yt-ch/
├── all_channels_videos.csv            # Original source metadata for 2,640 videos
├── download_videos.py                 # Subtitle fetcher and cleaner via yt-dlp
├── run_app.py                         # One-click launcher for the web application
├── dawah_knowledge_extractor_colab.ipynb # Free-tier Google Colab batch extraction notebook
│
├── core/
│   ├── srt_parser.py                  # Parses subtitle cues, removes duplicates & chunks dialogues
│   ├── metadata_linker.py             # Links SRT files to Arabic titles and YouTube URLs
│   ├── extractor_prompt.py            # Standardized schema for dialectical arguments & analogies
│   ├── colab_runner.py                # Checkpointed batch processor for Google Colab
│   └── smart_bot.py                   # Zero-LLM intelligent dialogue assistant
│
├── db/
│   └── database.py                    # SQLite engine with FTS5 dual-language BM25 search
│
├── data/
│   ├── video_manifest.json            # Unified inventory of 2,363 linked videos
│   ├── pilot_qa_dataset.json          # Pre-analyzed dialectical Q&A units across 6 pillars
│   └── dawah_knowledge.db             # SQLite database with FTS5 search index
│
├── web/
│   ├── app.py                         # FastAPI REST application
│   ├── templates/
│   │   └── index.html                 # Responsive bilingual web portal
│   └── static/
│       ├── css/style.css              # Dark slate theme, RTL/LTR styling & card layouts
│       └── js/app.js                  # Dynamic search, language switcher & chat client
│
└── tests/
    └── test_endpoints.py              # Automated test suite for all endpoints
```

---

## 🏛️ The 6 Foundational Dialectical Pillars

1. **Theology & God's Existence (`العقيدة والإلهيات`)**: First Cause, Contingency Argument, Fine-Tuning, Refuting "Who created God?", Pure Monotheism (Tawhid).
2. **Comparative Religion & Christianity (`مقارنة الأديان والنصرانية`)**: Logical contradictions of the Trinity, Nature of Christ, Biblical manuscript preservation vs. Quranic preservation.
3. **Problem of Evil & Suffering (`مشكلة الشر والمعاناة`)**: Divine Wisdom (Hikmah), Purpose of earthly trials, Justice in the Hereafter.
4. **Objective Morality & Ethics (`الأخلاق الموضوعية والإلحاد`)**: Grounding objective moral duty without God, Moral epistemology vs. ontology.
5. **Epistemology & Science (`المعرفة والعلم التجريبي`)**: Limits of scientism, Rational deduction vs. empirical testing, Darwinian materialism.
6. **Shariah & Social Inquiries (`الشبهات والشريعة الإسلامية`)**: Women's financial and legal rights in Islam, Hijab, Complementary justice.
