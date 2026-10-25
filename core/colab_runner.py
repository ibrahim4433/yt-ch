#!/usr/bin/env python3
"""
core/colab_runner.py
Batch extraction runner optimized for Google Colab Free Tier (Local T4 GPU).
Runs open-weight models (Qwen-2.5 / Llama-3) directly on the Colab GPU without any API keys!
Features auto-checkpointing, error recovery, and zero data-loss batching.
"""

import os
import re
import sys
import json
import time
from pathlib import Path
from typing import List, Dict, Any, Optional

try:
    from core.srt_parser import parse_srt_file, chunk_transcript_for_extraction
    from core.extractor_prompt import EXTRACTION_SYSTEM_PROMPT, USER_EXTRACTION_PROMPT_TEMPLATE
except (ImportError, ValueError):
    from .srt_parser import parse_srt_file, chunk_transcript_for_extraction
    from .extractor_prompt import EXTRACTION_SYSTEM_PROMPT, USER_EXTRACTION_PROMPT_TEMPLATE

BASE_DIR = Path(__file__).resolve().parent.parent

# Persistent Google Drive support for Colab environment
DRIVE_BASE = Path("/content/drive/MyDrive/yt-ch")
if os.path.exists("/content/drive/MyDrive"):
    DATA_DIR = DRIVE_BASE / "data"
    DOWNLOADS_DIR = DRIVE_BASE / "Downloads"
else:
    DATA_DIR = BASE_DIR / "data"
    DOWNLOADS_DIR = BASE_DIR / "Downloads"

DATA_DIR.mkdir(parents=True, exist_ok=True)
OUTPUT_JSONL = DATA_DIR / "extracted_qa.jsonl"
CHECKPOINT_FILE = DATA_DIR / "extraction_checkpoint.json"


def load_checkpoints() -> Dict[str, Any]:
    """Loads already processed video IDs to avoid re-processing."""
    if CHECKPOINT_FILE.exists():
        try:
            with open(CHECKPOINT_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return {"processed_video_ids": [], "total_qa_extracted": 0}
    return {"processed_video_ids": [], "total_qa_extracted": 0}


def save_checkpoints_dict(state: Dict[str, Any]):
    """Saves the complete checkpoints dictionary directly."""
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    with open(CHECKPOINT_FILE, "w", encoding="utf-8") as f:
        json.dump(state, f, ensure_ascii=False, indent=2)


def save_checkpoint(video_id: str, count_extracted: int):
    """Saves progress after each video is processed."""
    state = load_checkpoints()
    if video_id not in state["processed_video_ids"]:
        state["processed_video_ids"].append(video_id)
        state["total_qa_extracted"] = state.get("total_qa_extracted", 0) + count_extracted
    save_checkpoints_dict(state)


def append_extracted_units(units: List[Dict[str, Any]]):
    """Appends extracted Q&A units to the JSONL dataset."""
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    with open(OUTPUT_JSONL, "a", encoding="utf-8") as f:
        for unit in units:
            f.write(json.dumps(unit, ensure_ascii=False) + "\n")


def clean_llm_json_response(raw_text: str) -> List[Dict[str, Any]]:
    """Strips markdown code fences and parses JSON safely."""
    text = raw_text.strip()
    if text.startswith("```"):
        text = re.sub(r"^```(?:json)?\s*", "", text)
        text = re.sub(r"\s*```$", "", text)
    try:
        data = json.loads(text)
        if isinstance(data, list):
            return data
        elif isinstance(data, dict):
            for v in data.values():
                if isinstance(v, list):
                    return v
            return [data]
        return []
    except json.JSONDecodeError:
        # Regex fallback to find JSON array
        match = re.search(r"\[\s*\{.*\}\s*\]", text, re.DOTALL)
        if match:
            try:
                return json.loads(match.group(0))
            except Exception:
                pass
        return []


class LocalGPUClient:
    """
    Runs an open-weight model directly on the Google Colab GPU (T4 / A100 / V5e).
    Zero API keys, zero external internet dependencies, zero rate limits.
    """
    def __init__(self, model_name: str = "Qwen/Qwen2.5-7B-Instruct", load_in_4bit: bool = True):
        import torch
        from transformers import AutoModelForCausalLM, AutoTokenizer

        print(f"[+] Initializing Local GPU Model: {model_name}")
        print(f"[+] CUDA Available: {torch.cuda.is_available()}")
        if torch.cuda.is_available():
            print(f"[+] GPU Device: {torch.cuda.get_device_name(0)}")

        self.tokenizer = AutoTokenizer.from_pretrained(model_name)
        
        quant_config = None
        if load_in_4bit:
            try:
                from transformers import BitsAndBytesConfig
                quant_config = BitsAndBytesConfig(
                    load_in_4bit=True,
                    bnb_4bit_compute_dtype=torch.float16,
                    bnb_4bit_quant_type="nf4",
                    bnb_4bit_use_double_quant=True
                )
            except ImportError:
                print("[-] bitsandbytes not found, continuing without 4-bit quant.")

        self.model = AutoModelForCausalLM.from_pretrained(
            model_name,
            device_map="auto",
            quantization_config=quant_config,
            torch_dtype=torch.float16
        )
        print("[+] Model loaded into GPU VRAM successfully!")

    def extract(self, prompt: str) -> str:
        messages = [
            {"role": "system", "content": EXTRACTION_SYSTEM_PROMPT},
            {"role": "user", "content": prompt}
        ]
        text_input = self.tokenizer.apply_chat_template(
            messages,
            tokenize=False,
            add_generation_prompt=True
        )
        inputs = self.tokenizer([text_input], return_tensors="pt").to(self.model.device)

        import torch
        with torch.no_grad():
            generated_ids = self.model.generate(
                **inputs,
                max_new_tokens=1500,
                temperature=0.2,
                top_p=0.9,
                do_sample=True,
                pad_token_id=self.tokenizer.eos_token_id
            )
            
        generated_ids = [
            output_ids[len(input_ids):] for input_ids, output_ids in zip(inputs.input_ids, generated_ids)
        ]
        response = self.tokenizer.batch_decode(generated_ids, skip_special_tokens=True)[0]
        return response


class ExtractionClient:
    """Universal client supporting Local Colab GPU or API fallback."""
    def __init__(self, provider: str = "local_gpu", model_name: str = "Qwen/Qwen2.5-7B-Instruct"):
        self.provider = provider.lower()
        if self.provider == "local_gpu":
            self.client = LocalGPUClient(model_name=model_name, load_in_4bit=True)
        elif self.provider == "gemini":
            import google.generativeai as genai
            genai.configure(api_key=os.environ.get("GEMINI_API_KEY"))
            self.model = genai.GenerativeModel(
                model_name="gemini-1.5-flash",
                system_instruction=EXTRACTION_SYSTEM_PROMPT
            )
        else:
            raise ValueError(f"Unknown provider: {provider}")

    def extract(self, prompt: str) -> str:
        if self.provider == "local_gpu":
            return self.client.extract(prompt)
        elif self.provider == "gemini":
            res = self.model.generate_content(
                prompt,
                generation_config={"temperature": 0.2, "response_mime_type": "application/json"}
            )
            return res.text
        return "[]"


def process_video(
    video_record: Dict[str, Any],
    client: Any,
    chunk_duration_sec: float = 360.0,
    overlap_duration_sec: float = 60.0
) -> List[Dict[str, Any]]:
    """Processes a single video by chunking its transcript and extracting all Q&As."""
    raw_srt_rel = video_record.get("srt_file", "").replace("\\", "/")
    filename = video_record.get("srt_filename") or Path(raw_srt_rel).name

    candidate_paths = [
        BASE_DIR / raw_srt_rel,
        BASE_DIR / "Downloads" / filename,
        DOWNLOADS_DIR / filename,
        DRIVE_BASE / raw_srt_rel,
        DRIVE_BASE / "Downloads" / filename,
        Path("/content/drive/MyDrive/yt-ch/Downloads") / filename,
        Path("/content/drive/MyDrive/yt-ch") / raw_srt_rel,
    ]

    srt_path = None
    for p in candidate_paths:
        if p.exists():
            srt_path = p
            break

    if not srt_path:
        return None

    cues = parse_srt_file(srt_path)
    if not cues:
        return None

    chunks = chunk_transcript_for_extraction(
        cues,
        chunk_duration_sec=chunk_duration_sec,
        overlap_duration_sec=overlap_duration_sec
    )

    all_units = []
    video_id = video_record["video_id"]
    youtube_base = video_record.get("youtube_url", f"https://www.youtube.com/watch?v=YC86BQwvHyk")

    for i, chunk in enumerate(chunks):
        prompt = USER_EXTRACTION_PROMPT_TEMPLATE.format(
            title_ar=video_record.get("title_ar", ""),
            youtube_url=youtube_base,
            start_fmt=chunk["start_fmt"],
            end_fmt=chunk["end_fmt"],
            transcript_text=chunk["text"]
        )

        try:
            raw_output = client.extract(prompt)
            extracted = clean_llm_json_response(raw_output)
            
            for item in extracted:
                ts_sec = item.get("timestamp_seconds", int(chunk["start_sec"]))
                if ts_sec < chunk["start_sec"]:
                    ts_sec = int(chunk["start_sec"])
                    
                item["id"] = f"{video_id}_{len(all_units) + 1:03d}"
                item["video_id"] = video_id
                item["channel"] = video_record.get("channel", "SCDawah Arabic")
                item["video_title_ar"] = video_record.get("title_ar", "")
                item["youtube_url"] = youtube_base
                item["timestamp_url"] = f"{youtube_base}&t={int(ts_sec)}s"
                item["timestamp_seconds"] = int(ts_sec)
                
                all_units.append(item)
                
        except Exception as e:
            print(f"[-] Error processing chunk {i} of {video_id}: {e}")
            time.sleep(2)

    return all_units
