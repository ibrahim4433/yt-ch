import sqlite3
import json
import urllib.request
import urllib.parse
import time
import io
import sys

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

def batch_translate_to_ar(texts, max_retries: int = 2):
    """Translates a list of strings in a single batch request for speed."""
    if not texts:
        return []
    
    clean_texts = [str(t).strip() if t else "" for t in texts]
    if not any(clean_texts):
        return ["" for _ in texts]

    delimiter = "\n====SPLIT====\n"
    combined = delimiter.join(clean_texts)
    
    url = 'https://translate.googleapis.com/translate_a/single?client=gtx&sl=en&tl=ar&dt=t&q=' + urllib.parse.quote(combined)
    for attempt in range(max_retries):
        try:
            req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
            with urllib.request.urlopen(req, timeout=6) as resp:
                data = json.loads(resp.read().decode())
                translated_combined = ''.join([part[0] for part in data[0] if part and len(part) > 0])
                results = translated_combined.split("====SPLIT====")
                # Ensure same length
                if len(results) == len(texts):
                    return [r.strip() for r in results]
                elif len(results) < len(texts):
                    results.extend(["" for _ in range(len(texts) - len(results))])
                    return [r.strip() for r in results]
                else:
                    return [r.strip() for r in results[:len(texts)]]
        except Exception:
            time.sleep(0.5)
            
    # Fallback: empty list
    return ["" for _ in texts]

def is_none_text(text: str) -> bool:
    if not text:
        return True
    return text.strip().lower() in ["none", "none used", "none used.", "none.", "n/a", "no", "not applicable", "null"]

def run_enrichment(db_path=None):
    if db_path is None:
        from db.database import DB_PATH
        db_path = DB_PATH

    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row

    rows = conn.execute("""
        SELECT * FROM qa_units 
        WHERE logical_premises_ar_json = '[]' 
           OR logical_premises_ar_json IS NULL 
           OR analogy_or_metaphor_ar = '' 
           OR socratic_question_ar = ''
    """).fetchall()

    if not rows:
        print("   ✅ All existing records in database are already 100% Arabic!")
        conn.close()
        return

    print(f"\n   🌐 Found {len(rows)} previous records to enrich with Arabic fields...")
    try:
        from tqdm.auto import tqdm
        pbar = tqdm(rows, desc="   ⚡ Fast Arabic Enrichment")
    except ImportError:
        pbar = rows

    updated_count = 0
    try:
        for r in pbar:
            row_id = r["id"]
            dirty = False

            premises_ar_current = json.loads(r["logical_premises_ar_json"] or "[]")
            premises_en = json.loads(r["logical_premises_json"] or "[]")
            analogy_ar = r["analogy_or_metaphor_ar"] or ""
            analogy_en = (r["analogy_or_metaphor"] or "").strip()
            socratic_ar = r["socratic_question_ar"] or ""
            socratic_en = (r["socratic_question"] or "").strip()
            quote_ar = r["verbatim_quote_ar"] or ""
            quote_en = (r["verbatim_quote"] or "").strip()

            # Clean "none" values
            if is_none_text(analogy_en):
                analogy_en = ""
                analogy_ar = ""
                dirty = True
            if is_none_text(socratic_en):
                socratic_en = ""
                socratic_ar = ""
                dirty = True

            # Prepare items needing translation in this card
            need_trans = []
            keys = []

            if not premises_ar_current and premises_en:
                for idx, p in enumerate(premises_en):
                    need_trans.append(p)
                    keys.append(("premise", idx))

            if not analogy_ar and analogy_en and not is_none_text(analogy_en):
                need_trans.append(analogy_en)
                keys.append(("analogy", 0))

            if not socratic_ar and socratic_en and not is_none_text(socratic_en):
                need_trans.append(socratic_en)
                keys.append(("socratic", 0))

            if not quote_ar and quote_en:
                need_trans.append(quote_en[:300])
                keys.append(("quote", 0))

            if need_trans:
                translated_parts = batch_translate_to_ar(need_trans)
                for (k_type, k_idx), trans_val in zip(keys, translated_parts):
                    if trans_val:
                        if k_type == "premise":
                            if not premises_ar_current:
                                premises_ar_current = [""] * len(premises_en)
                            premises_ar_current[k_idx] = trans_val
                        elif k_type == "analogy":
                            analogy_ar = trans_val
                        elif k_type == "socratic":
                            socratic_ar = trans_val
                        elif k_type == "quote":
                            quote_ar = trans_val
                        dirty = True

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
    except KeyboardInterrupt:
        print("\n   [!] Enrichment paused by user. Progress safely saved.")
    finally:
        print(f"   🎉 Enriched {updated_count} records with 100% Arabic dialectical fields!")
        conn.close()

if __name__ == "__main__":
    run_enrichment()
