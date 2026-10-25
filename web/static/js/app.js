/**
 * web/static/js/app.js
 * 100% Complete Dual-Language Localization & Interaction Engine
 */

let currentLang = "en";
let currentCategory = "all";
let searchDebounceTimeout = null;

const CATEGORY_MAP = {
  "Theology & God's Existence": { en: "God's Existence", ar: "العقيدة ووجود الله" },
  "Problem of Evil & Suffering": { en: "Problem of Evil", ar: "مشكلة الشر والمعاناة" },
  "Comparative Religion & Christianity": { en: "Christianity & Trinity", ar: "مقارنة الأديان والنصرانية" },
  "Objective Morality & Ethics": { en: "Morality", ar: "الأخلاق الموضوعية والإلحاد" },
  "Epistemology & Science": { en: "Science", ar: "المعرفة والعلم التجريبي" },
  "Shariah & Social Inquiries": { en: "Shariah & Women", ar: "الشريعة والشبهات الاجتماعية" }
};

const INTERLOCUTOR_MAP = {
  "Atheist / Materialist": { en: "Atheist / Materialist", ar: "ملحد / مادي" },
  "Christian / Trinitarian": { en: "Christian / Trinitarian", ar: "مسيحي / نصراني" },
  "Agnostic / Skeptic": { en: "Agnostic / Skeptic", ar: "لاأدري / متشكك" },
  "Secular Humanist / Christian": { en: "Secular / Christian", ar: "علماني / نصراني" },
  "Secular Humanist": { en: "Secular Humanist", ar: "علماني إنسانوي" },
  "Inquiring Seeker": { en: "Inquiring Seeker", ar: "باحث عن الحق" },
  "Muslim with Doubts": { en: "Muslim with Doubts", ar: "مسلم يطلب دليلاً" }
};

const translations = {
  en: {
    navTitle: "Dawah Dialectics",
    navSubtitle: "Applied Islamic Apologetics & Street Debate Archive",
    langLabel: "العربية",
    tabSearch: "Search & Knowledge Base",
    tabChat: "Smart Dawah Assistant",
    tabStats: "Corpus & Video Archive",
    searchHeading: "Find Clear, Logical Answers to Any Inquiry About Islam",
    searchSubheading: "Distilled from 2,360+ live street debates, dialogues, and philosophical encounters.",
    searchPlaceholder: "Search questions (e.g., 'Who created God', 'Problem of evil', 'من خلق الله', 'التثليث')...",
    filterTopicLabel: "Topic:",
    allTopicsLabel: "All Topics",
    showingResults: "Showing dialectical Q&A units:",
    assistantTitle: "Smart Dialectical Assistant",
    assistantDesc: "Instant answers, deductive logic, intuitive analogies & exact debate timestamps (Zero-latency).",
    chipHint: "Try asking:",
    welcomeText: "Assalamu Alaikum! Ask me any theological objection, philosophical doubt, or inquiry about Islam. I will retrieve the exact logical deductions, concrete analogies, and the real-life debate video timestamps used by the team.",
    chatPlaceholder: "Type your question or objection here (English or Arabic)...",
    sendLabel: "Send",
    premisesLabel: "Deductive Logical Breakdown",
    analogyLabel: "The Analogy / Metaphor",
    socraticLabel: "Socratic Counter-Question",
    verbatimLabel: "Verbatim Street Dialogue Excerpt",
    watchBtn: "Watch Debate Segment",
    footerText: "Dawah Dialectics Archive & Q&A Engine • Grounded in Truth, Reason, and Wisdom.",
    noResults: "No dialectical Q&A entries found matching your query.",
    statsTitle: "Corpus Metadata & Processing Inventory",
    statsSubtitle: "Complete transparency: Tracking 2,360+ street debate transcripts with zero data loss.",
    statVideosLabel: "Subtitle Files Cataloged",
    statWordsLabel: "Spoken Words Preserved",
    statQaLabel: "Pre-Analyzed Q&A Units",
    statPillarsLabel: "Foundational Pillars Covered",
    colabTitle: "Scale Extraction on Google Colab (Free Tier)",
    colabDesc: "Ready-to-run notebook included in repo (dawah_knowledge_extractor_colab.ipynb). Run batch distillation over all 2,363 files across multi-day free GPU sessions with zero data loss.",
    chips: [
      { text: "Who created God?", query: "Who created God?" },
      { text: "Why does God allow suffering?", query: "Why does God allow innocent children to suffer?" },
      { text: "How to refute the Trinity?", query: "How to refute the Trinity?" },
      { text: "Can atheists have objective morality?", query: "Can atheists have objective morality?" },
      { text: "Women's rights in Islam", query: "Does Islam oppress women?" },
      { text: "Is scientism self-refuting?", query: "Why believe in what science cannot observe?" }
    ]
  },
  ar: {
    navTitle: "جدليات الدعوة الإسلامية",
    navSubtitle: "أرشيف المحاججة العقلية والمناظرات الحوارية في ركن المتحدثين",
    langLabel: "English",
    tabSearch: "البحث ومكتبة الإجابات",
    tabChat: "المساعد الحواري الذكي",
    tabStats: "إحصائيات الأرشيف المرئي",
    searchHeading: "إجابات عقلية رصينة ومفحمة عن أي شبهة أو استفسار حول الإسلام",
    searchSubheading: "مستخلصة ومحررة من أكثر من 2,360 حواراً ومناظرة شارع حية مع الملاحدة والنصارى واللاأدريين.",
    searchPlaceholder: "ابحث في الشبهات والأسئلة (مثال: 'من خلق الله'، 'مشكلة الشر'، 'عقيدة التثليث'، 'الأخلاق والإلحاد')...",
    filterTopicLabel: "الموضوع الفكري:",
    allTopicsLabel: "كافة الموضوعات",
    showingResults: "الوحدات الحوارية المستخلصة المعروضة:",
    assistantTitle: "المساعد الحواري الذكي الفوري",
    assistantDesc: "استدعاء فوري للإجابات والأقيسة المنطقية والأمثلة الواقعية مع توثيق الفيديو الدقيق بدون انتظار.",
    chipHint: "جرّب أن تسأل:",
    welcomeText: "السلام عليكم ورحمة الله وبركاته! اكتب أي شبهة فلسفية أو سؤال حول الإسلام، وسأستخرج لك الحجة العقلية والمثال التوضيحي العملي ورابط الفيديو بلحظته الدقيقة كما حاور بها الدعاة في الميدان.",
    chatPlaceholder: "اكتب سؤالك أو الشبهة هنا بالعربية أو الإنجليزية...",
    sendLabel: "إرسال",
    premisesLabel: "التسلسل المنطقي للحجة (المقدمات والنتيجة)",
    analogyLabel: "المثال الواقعي / حجة الإلزام والتوضيح",
    socraticLabel: "السؤال السقراطي المعاكس (إلزام الخصم بمقدماته)",
    verbatimLabel: "نص الحوار الحرفي كما قيل في الشارع",
    watchBtn: "شاهد اللقطة في الفيديو الأصلي",
    footerText: "أرشيف جدليات الدعوة الإسلامية ومحرك البحث المعرفي • بالحكمة والموعظة الحسنة والبرهان العقلي.",
    noResults: "لم يتم العثور على أي بطاقة حوارية تطابق بحثك.",
    statsTitle: "بيانات الأرشيف وجرد المعالجة الشامل",
    statsSubtitle: "شفافية تامة: تتبع وفهرسة أكثر من 2,360 تفريغاً نصياً دون فقدان أي معلومة نافعة.",
    statVideosLabel: "ملف ترجمة مفهرس ومطابق",
    statWordsLabel: "كلمة منطوقة محفوظة",
    statQaLabel: "وحدة حوارية محررة ومحللة",
    statPillarsLabel: "أبواب فلسفية كبرى مغطاة",
    colabTitle: "استكمال الاستخراج الآلي عبر جوجل كولاب (مجاناً)",
    colabDesc: "ملف كولاب جاهز للتشغيل في المستودع (dawah_knowledge_extractor_colab.ipynb). يتيح المعالجة عبر جلسات مجانية متعددة الأيام مع حفظ التقدم تلقائياً دون أي فقدان.",
    chips: [
      { text: "من خلق الله؟", query: "من خلق الله؟" },
      { text: "لماذا يسمح الله بالشر والألم؟", query: "لماذا يسمح الله بمعاناة الأطفال؟" },
      { text: "كيف نرد على عقيدة التثليث؟", query: "كيف نرد على عقيدة التثليث؟" },
      { text: "هل الأخلاق ممكنة بدون دين؟", query: "هل يستطيع الملحد تأسيس أخلاق موضوعية؟" },
      { text: "حقوق المرأة والشبهات", query: "هل يظلم الإسلام المرأة؟" },
      { text: "الرد على حصر الحقيقة في العلم", query: "لماذا نؤمن بما لا يثبته العلم التجريبي؟" }
    ]
  }
};

document.addEventListener("DOMContentLoaded", () => {
  renderLanguageUI();
  performSearch();
  loadStats();
});

function toggleLanguage() {
  currentLang = currentLang === "en" ? "ar" : "en";
  document.documentElement.setAttribute("dir", currentLang === "ar" ? "rtl" : "ltr");
  document.documentElement.setAttribute("lang", currentLang);

  renderLanguageUI();
  performSearch();
}

function renderLanguageUI() {
  const t = translations[currentLang];
  const isAr = currentLang === "ar";

  document.getElementById("nav-title").innerText = t.navTitle;
  document.getElementById("nav-subtitle").innerText = t.navSubtitle;
  document.getElementById("lang-label").innerText = t.langLabel;
  document.getElementById("tab-search-label").innerText = t.tabSearch;
  document.getElementById("tab-chat-label").innerText = t.tabChat;
  document.getElementById("tab-stats-label").innerText = t.tabStats;
  document.getElementById("search-heading").innerText = t.searchHeading;
  document.getElementById("search-subheading").innerText = t.searchSubheading;
  document.getElementById("search-input").placeholder = t.searchPlaceholder;
  document.getElementById("filter-topic-label").innerText = t.filterTopicLabel;
  document.getElementById("results-count-text").innerText = t.showingResults;
  document.getElementById("assistant-title").innerText = t.assistantTitle;
  document.getElementById("assistant-desc").innerText = t.assistantDesc;
  document.getElementById("chip-hint").innerText = t.chipHint;
  document.getElementById("welcome-text").innerText = t.welcomeText;
  document.getElementById("chat-input").placeholder = t.chatPlaceholder;
  document.getElementById("send-label").innerText = t.sendLabel;
  document.getElementById("footer-text").innerText = t.footerText;

  // Stats tab translations
  if (document.getElementById("stats-title")) document.getElementById("stats-title").innerText = t.statsTitle;
  if (document.getElementById("stats-subtitle")) document.getElementById("stats-subtitle").innerText = t.statsSubtitle;
  if (document.getElementById("stat-videos-label")) document.getElementById("stat-videos-label").innerText = t.statVideosLabel;
  if (document.getElementById("stat-words-label")) document.getElementById("stat-words-label").innerText = t.statWordsLabel;
  if (document.getElementById("stat-qa-label")) document.getElementById("stat-qa-label").innerText = t.statQaLabel;
  if (document.getElementById("stat-pillars-label")) document.getElementById("stat-pillars-label").innerText = t.statPillarsLabel;
  if (document.getElementById("colab-title")) document.getElementById("colab-title").innerText = t.colabTitle;
  if (document.getElementById("colab-desc")) document.getElementById("colab-desc").innerText = t.colabDesc;

  // Filter pills
  const pillsContainer = document.getElementById("category-pills");
  if (pillsContainer) {
    pillsContainer.innerHTML = `
      <button class="pill ${currentCategory === 'all' ? 'active' : ''}" data-category="all" onclick="setCategoryFilter('all', this)">${t.allTopicsLabel}</button>
      ${Object.keys(CATEGORY_MAP).map(catKey => `
        <button class="pill ${currentCategory === catKey ? 'active' : ''}" data-category="${catKey}" onclick="setCategoryFilter('${catKey}', this)">
          ${CATEGORY_MAP[catKey][isAr ? 'ar' : 'en']}
        </button>
      `).join("")}
    `;
  }

  // Suggestion chips
  const chipsContainer = document.getElementById("prompt-chips-container");
  if (chipsContainer) {
    chipsContainer.innerHTML = t.chips.map(chip => `
      <button class="chip" onclick="askAssistant('${escapeHtml(chip.query)}')">"${escapeHtml(chip.text)}"</button>
    `).join("");
  }
}

function switchTab(tabId) {
  document.querySelectorAll(".tab-pane").forEach(p => p.classList.remove("active"));
  document.querySelectorAll(".tab-btn").forEach(b => b.classList.remove("active"));

  document.getElementById(tabId).classList.add("active");
  const activeBtn = Array.from(document.querySelectorAll(".tab-btn")).find(b => 
    b.getAttribute("onclick").includes(tabId)
  );
  if (activeBtn) activeBtn.classList.add("active");
}

function setCategoryFilter(cat, btnElement) {
  currentCategory = cat;
  document.querySelectorAll("#category-pills .pill").forEach(p => p.classList.remove("active"));
  btnElement.classList.add("active");
  performSearch();
}

function handleSearchInput() {
  clearTimeout(searchDebounceTimeout);
  searchDebounceTimeout = setTimeout(() => {
    performSearch();
  }, 200);
}

function performSearch() {
  const query = document.getElementById("search-input").value.trim();
  const url = `/api/search?q=${encodeURIComponent(query)}&category=${encodeURIComponent(currentCategory)}`;

  fetch(url)
    .then(r => r.json())
    .then(data => {
      renderCards(data.results || []);
    })
    .catch(err => {
      console.error("Search error:", err);
    });
}

function renderCards(cards) {
  const container = document.getElementById("qa-cards-container");
  container.innerHTML = "";

  const t = translations[currentLang];
  const isAr = currentLang === "ar";

  if (!cards.length) {
    container.innerHTML = `<div style="text-align:center; padding: 3rem; color: var(--text-muted); font-size: 1.1rem;">${t.noResults}</div>`;
    return;
  }

  cards.forEach(card => {
    const questionText = isAr ? (card.question_ar || card.question_en) : (card.question_en || card.question_ar);
    const summaryText = isAr ? (card.core_answer_summary_ar || card.core_answer_summary_en) : (card.core_answer_summary_en || card.core_answer_summary_ar);
    
    // Category & interlocutor names in active language
    const categoryName = (CATEGORY_MAP[card.topic_category] && CATEGORY_MAP[card.topic_category][isAr ? "ar" : "en"]) || card.topic_category;
    const interlocutorName = (INTERLOCUTOR_MAP[card.interlocutor_type] && INTERLOCUTOR_MAP[card.interlocutor_type][isAr ? "ar" : "en"]) || card.interlocutor_type;

    // Premises list in active language
    const premises = isAr && card.logical_premises_ar && card.logical_premises_ar.length ? card.logical_premises_ar : (card.logical_premises || []);
    let premisesHtml = "";
    if (premises.length) {
      premisesHtml = `
        <div class="premises-box">
          <div class="premises-title">🧠 ${t.premisesLabel}</div>
          <ul class="premises-list">
            ${premises.map((p, idx) => `
              <li><span class="premise-num">${idx + 1}.</span> <span>${escapeHtml(p)}</span></li>
            `).join("")}
          </ul>
        </div>
      `;
    }

    // Analogy in active language
    const analogyText = isAr && card.analogy_or_metaphor_ar ? card.analogy_or_metaphor_ar : card.analogy_or_metaphor;
    let analogyHtml = "";
    if (analogyText) {
      analogyHtml = `
        <div class="analogy-callout">
          <div class="analogy-header">💡 ${t.analogyLabel}</div>
          <div class="analogy-text">${escapeHtml(analogyText)}</div>
        </div>
      `;
    }

    // Socratic question in active language
    const socraticText = isAr && card.socratic_question_ar ? card.socratic_question_ar : card.socratic_question;
    let socraticHtml = "";
    if (socraticText) {
      socraticHtml = `
        <div class="socratic-callout" style="background:rgba(59,130,246,0.08); border:1px solid rgba(59,130,246,0.25); border-radius:var(--radius-md); padding:0.85rem 1rem; margin-bottom:1.25rem;">
          <div style="font-size:0.85rem; font-weight:700; color:#60a5fa; margin-bottom:0.35rem; display:flex; align-items:center; gap:0.4rem;">❓ ${t.socraticLabel}</div>
          <div style="font-size:0.92rem; color:#f3f4f6;">"${escapeHtml(socraticText)}"</div>
        </div>
      `;
    }

    // Verbatim quote in active language
    const quoteText = isAr && card.verbatim_quote_ar ? card.verbatim_quote_ar : card.verbatim_quote;
    let quoteHtml = "";
    if (quoteText) {
      quoteHtml = `
        <div class="verbatim-box">
          <span class="quote-label">📜 ${t.verbatimLabel}:</span>
          "${escapeHtml(quoteText)}"
        </div>
      `;
    }

    const cardEl = document.createElement("div");
    cardEl.className = "qa-card";
    cardEl.innerHTML = `
      <div class="card-top">
        <div class="card-badges">
          <span class="badge badge-category">${escapeHtml(categoryName)}</span>
          <span class="badge badge-interlocutor">${escapeHtml(interlocutorName)}</span>
        </div>
      </div>
      <h3 class="card-question">${escapeHtml(questionText)}</h3>
      <div class="card-summary">${escapeHtml(summaryText)}</div>
      ${premisesHtml}
      ${analogyHtml}
      ${socraticHtml}
      ${quoteHtml}
      <div class="card-footer">
        <div class="source-info">
          <span>🎬 ${escapeHtml(card.video_title_ar || "")}</span>
          <span class="source-time">${escapeHtml(card.timestamp_formatted || "00:00")}</span>
        </div>
        <a href="${escapeHtml(card.timestamp_url || card.youtube_url)}" target="_blank" rel="noopener" class="yt-watch-btn">
          ▶ ${t.watchBtn}
        </a>
      </div>
    `;
    container.appendChild(cardEl);
  });
}

function askAssistant(promptText) {
  switchTab("chat-tab");
  document.getElementById("chat-input").value = promptText;
  sendChatMessage();
}

function sendChatMessage() {
  const input = document.getElementById("chat-input");
  const query = input.value.trim();
  if (!query) return;

  const messagesBox = document.getElementById("chat-messages");

  const userMsgEl = document.createElement("div");
  userMsgEl.className = "message user-msg";
  userMsgEl.innerHTML = `<div class="msg-content"><p>${escapeHtml(query)}</p></div>`;
  messagesBox.appendChild(userMsgEl);
  input.value = "";
  messagesBox.scrollTop = messagesBox.scrollHeight;

  fetch(`/api/chat?q=${encodeURIComponent(query)}`)
    .then(r => r.json())
    .then(data => {
      const isAr = data.language === "ar" || currentLang === "ar";
      const t = translations[isAr ? "ar" : "en"];
      const pkg = data.response_package;

      let botResponseHtml = "";
      if (pkg) {
        let noticeHtml = "";
        if (data.status === "partial_match" && data.message) {
          noticeHtml = `
            <div style="background:rgba(234, 179, 8, 0.12); border:1px solid rgba(234, 179, 8, 0.35); border-radius:var(--radius-md); padding:0.75rem 1rem; margin-bottom:0.85rem; font-size:0.9rem; color:#fef08a;">
              ${escapeHtml(data.message)}
            </div>
          `;
        }

        let premisesListHtml = "";
        if (pkg.logical_premises && pkg.logical_premises.length) {
          premisesListHtml = `
            <div class="premises-box" style="margin-top:0.75rem;">
              <div class="premises-title">🧠 ${t.premisesLabel}</div>
              <ul class="premises-list">
                ${pkg.logical_premises.map((p, idx) => `<li><span class="premise-num">${idx + 1}.</span> ${escapeHtml(p)}</li>`).join("")}
              </ul>
            </div>
          `;
        }

        let analogyHtml = "";
        if (pkg.analogy) {
          analogyHtml = `
            <div class="analogy-callout" style="margin-top:0.75rem;">
              <div class="analogy-header">💡 ${t.analogyLabel}</div>
              <div class="analogy-text">${escapeHtml(pkg.analogy)}</div>
            </div>
          `;
        }

        let socraticHtml = "";
        if (pkg.socratic_question) {
          socraticHtml = `
            <div style="background:rgba(59,130,246,0.08); border:1px solid rgba(59,130,246,0.25); border-radius:var(--radius-md); padding:0.85rem 1rem; margin-top:0.75rem;">
              <div style="font-size:0.85rem; font-weight:700; color:#60a5fa; margin-bottom:0.35rem; display:flex; align-items:center; gap:0.4rem;">❓ ${t.socraticLabel}</div>
              <div style="font-size:0.92rem; color:#f3f4f6;">"${escapeHtml(pkg.socratic_question)}"</div>
            </div>
          `;
        }

        botResponseHtml = `
          ${noticeHtml}
          <div style="margin-bottom:0.75rem;">
            <div style="display:flex; gap:0.5rem; margin-bottom:0.5rem;">
              <span class="badge badge-category">${escapeHtml(pkg.category)}</span>
              <span class="badge badge-interlocutor">${escapeHtml(pkg.interlocutor)}</span>
            </div>
            <h4 style="color:#fff; font-size:1.15rem; margin-bottom:0.5rem;">${escapeHtml(pkg.title)}</h4>
            <p style="color:#e5e7eb; font-size:0.95rem; line-height:1.6;">${escapeHtml(pkg.summary)}</p>
          </div>
          ${premisesListHtml}
          ${analogyHtml}
          ${socraticHtml}
          ${pkg.verbatim_quote ? `
            <div class="verbatim-box" style="margin-top:0.75rem;">
              <span class="quote-label">📜 ${t.verbatimLabel}:</span>
              "${escapeHtml(pkg.verbatim_quote)}"
            </div>
          ` : ""}
          <div style="margin-top:1rem; display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap; gap:0.5rem; border-top:1px solid var(--border-color); padding-top:0.75rem;">
            <span style="font-size:0.8rem; color:var(--text-muted);">🎬 ${escapeHtml(pkg.video_title)} [${escapeHtml(pkg.timestamp)}]</span>
            <a href="${escapeHtml(pkg.timestamp_url)}" target="_blank" rel="noopener" class="yt-watch-btn">
              ▶ ${t.watchBtn}
            </a>
          </div>
        `;
      } else {
        let suggestionsHtml = "";
        if (data.related_questions && data.related_questions.length) {
          suggestionsHtml = `
            <div style="margin-top:1rem; border-top:1px solid var(--border-color); padding-top:0.75rem;">
              <div style="font-size:0.85rem; color:var(--text-muted); margin-bottom:0.5rem;">${isAr ? "💡 استكشف أحد الأسئلة المتاحة حالياً في الأرشيف:" : "💡 Or explore available questions in the archive:"}</div>
              <div style="display:flex; flex-direction:column; gap:0.4rem;">
                ${data.related_questions.map(q => `
                  <button class="topic-chip" style="text-align:inherit; width:100%; border:1px solid rgba(255,255,255,0.08); background:rgba(255,255,255,0.03); padding:0.5rem 0.75rem; border-radius:var(--radius-sm); color:#e5e7eb; cursor:pointer;" onclick="askAssistant('${escapeHtml(q.question)}')">
                    📌 ${escapeHtml(q.question)}
                  </button>
                `).join("")}
              </div>
            </div>
          `;
        }
        botResponseHtml = `
          <div style="line-height:1.7; white-space:pre-line; color:#e5e7eb; padding:0.25rem 0;">
            ${escapeHtml(data.message || (isAr ? "لم نجد إجابة مطابقة." : "No matching answer found."))}
          </div>
          ${suggestionsHtml}
        `;
      }

      const botMsgEl = document.createElement("div");
      botMsgEl.className = "message assistant-msg";
      botMsgEl.innerHTML = `<div class="msg-content">${botResponseHtml}</div>`;
      messagesBox.appendChild(botMsgEl);
      messagesBox.scrollTop = messagesBox.scrollHeight;
    })
    .catch(err => {
      console.error("Chat error:", err);
    });
}

function loadStats() {
  fetch("/api/stats")
    .then(r => r.json())
    .then(data => {
      if (document.getElementById("stat-videos")) {
        document.getElementById("stat-videos").innerText = data.total_videos.toLocaleString();
      }
      if (document.getElementById("stat-qa")) {
        document.getElementById("stat-qa").innerText = data.total_qa.toLocaleString();
      }
    })
    .catch(err => console.error("Stats error:", err));
}

function escapeHtml(str) {
  if (!str) return "";
  return String(str)
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;")
    .replace(/'/g, "&#039;");
}
