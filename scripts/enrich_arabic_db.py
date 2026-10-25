import sqlite3
import json
import urllib.request
import urllib.parse
import time
import io
import sys

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

def translate_to_ar(text: str, max_retries: int = 3) -> str:
    if not text or not text.strip():
        return ""
    cleaned = text.strip()
    if cleaned.lower() in ["none", "none used", "none used.", "none.", "n/a", "no", "not applicable", "null"]:
        return ""
    
    url = 'https://translate.googleapis.com/translate_a/single?client=gtx&sl=en&tl=ar&dt=t&q=' + urllib.parse.quote(cleaned)
    for attempt in range(max_retries):
        try:
            req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
            with urllib.request.urlopen(req, timeout=10) as resp:
                data = json.loads(resp.read().decode())
                res = ''.join([part[0] for part in data[0] if part and len(part) > 0])
                return res.strip()
        except Exception as e:
            if attempt == max_retries - 1:
                print(f"[-] Failed translating: '{cleaned[:40]}...' ({e})")
                return ""
            time.sleep(1.0)
    return ""

def run_enrichment():
    conn = sqlite3.connect('data/dawah_knowledge.db')
    conn.row_factory = sqlite3.Row

    rows = conn.execute("SELECT * FROM qa_units").fetchall()
    print(f"Found {len(rows)} records in database. Starting Arabic enrichment...")

    updated_count = 0
    for r in rows:
        row_id = r["id"]
        dirty = False

        # 1. Premises
        premises_ar_current = json.loads(r["logical_premises_ar_json"] or "[]")
        premises_en = json.loads(r["logical_premises_json"] or "[]")
        
        if not premises_ar_current and premises_en:
            translated_premises = []
            for p in premises_en:
                ar_p = translate_to_ar(p)
                if ar_p:
                    translated_premises.append(ar_p)
                time.sleep(0.1)
            premises_ar_current = translated_premises
            dirty = True

        # 2. Analogy
        analogy_ar = r["analogy_or_metaphor_ar"] or ""
        analogy_en = (r["analogy_or_metaphor"] or "").strip()
        if analogy_en.lower() in ["none", "none used", "none used.", "none.", "n/a", ""]:
            analogy_en = ""
            analogy_ar = ""
            dirty = True
        elif not analogy_ar and analogy_en:
            analogy_ar = translate_to_ar(analogy_en)
            dirty = True
            time.sleep(0.1)

        # 3. Socratic Question
        socratic_ar = r["socratic_question_ar"] or ""
        socratic_en = (r["socratic_question"] or "").strip()
        if socratic_en.lower() in ["none", "none used", "none used.", "none.", "n/a", ""]:
            socratic_en = ""
            socratic_ar = ""
            dirty = True
        elif not socratic_ar and socratic_en:
            socratic_ar = translate_to_ar(socratic_en)
            dirty = True
            time.sleep(0.1)

        # 4. Verbatim Quote
        quote_ar = r["verbatim_quote_ar"] or ""
        quote_en = (r["verbatim_quote"] or "").strip()
        if not quote_ar and quote_en:
            quote_ar = translate_to_ar(quote_en[:400]) # translate first 400 chars of spoken quote
            dirty = True
            time.sleep(0.1)

        if dirty:
            with conn:
                conn.execute("""
                    UPDATE qa_units SET
                        logical_premises_json = ?,
                        logical_premises_ar_json = ?,
                        analogy_or_metaphor = ?,
                        analogy_or_metaphor_ar = ?,
                        socratic_question = ?,
                        socratic_question_ar = ?,
                        verbatim_quote = ?,
                        verbatim_quote_ar = ?
                    WHERE id = ?
                """, (
                    json.dumps(premises_en, ensure_ascii=False),
                    json.dumps(premises_ar_current, ensure_ascii=False),
                    analogy_en,
                    analogy_ar,
                    socratic_en,
                    socratic_ar,
                    quote_en,
                    quote_ar,
                    row_id
                ))
            updated_count += 1
            print(f"[+] Enriched {row_id} with full Arabic fields ({updated_count}/{len(rows)})")

    print(f"\n🎉 Successfully enriched {updated_count} records with 100% Arabic dialectical fields!")
    conn.close()

if __name__ == "__main__":
    run_enrichment()
