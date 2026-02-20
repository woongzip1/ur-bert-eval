#!/usr/bin/env python3
"""
build_demo.py

실제 데이터(data_urbert)를 기반으로 Type A / Type B 데모 실험을 자동 구성합니다.

수행하는 작업:
  1. output_samples/ 에서 모델 목록 스캔
  2. tts_metadata/ 에서 텍스트 매핑 로드
  3. 언어별로 공통 샘플 ID 10개 선택 (5→A, 5→B)
  4. 오디오 파일 심볼릭 링크 생성
  5. config.js 자동 생성

사용법:
  cd /home/woongzip/homepage/ur-bert-eval
  python build_demo.py
"""

import os
import csv
import json
import random
import glob
from pathlib import Path
from datetime import datetime
from collections import defaultdict

# ═══════════════════════════════════════════
# SETTINGS
# ═══════════════════════════════════════════

DATA_ROOT = "/home/woongzip/data_urbert"
SAMPLES_DIR = os.path.join(DATA_ROOT, "output_samples")
METADATA_DIR = os.path.join(DATA_ROOT, "tts_metadata")

OUTPUT_DIR_A = "/home/woongzip/homepage/ur-bert-eval/A"
OUTPUT_DIR_B = "/home/woongzip/homepage/ur-bert-eval/B"

SAMPLES_PER_LANG = 10   # 언어당 샘플 수 (5→A, 5→B)
SPLIT_INDEX = 5          # 앞 5개→A, 뒤 5개→B
RANDOM_SEED = 42

SHEET_URL = "https://script.google.com/macros/s/AKfycby6_3EvfoU0mcQg2IzBdmhLFlAPIn3XBzpfNbuuBigz-LWUwX3CgYMWBANXTHHSLa-umQ/exec"

# 모델명 suffix → metadata CSV의 lang code
LANG_MAP = {
    "AF": "af",
    "DE": "de",
    "EN": "en",
    "NP": "np",
    "SI": "si",
    "TN": "tn",
    "ZH": "zh",
    "KM": "km",
    "JV": "jv",
    "SU": "su",
    "XH": "xh",
}

# 언어 코드 → 표시용 이름
LANG_DISPLAY = {
    "af": "Afrikaans",
    "de": "German",
    "en": "English",
    "np": "Nepali",
    "si": "Sinhala",
    "tn": "Tswana",
    "zh": "Chinese",
    "km": "Khmer",
    "jv": "Javanese",
    "su": "Sundanese",
    "xh": "Xhosa",
}

# ═══════════════════════════════════════════


def get_model_lang(model_name):
    """모델명에서 언어 코드 추출 (예: URBERT-TN → tn)"""
    suffix = model_name.split("-")[-1]
    return LANG_MAP.get(suffix, None)


def get_checkpoint_dir(model_path):
    """모델 폴더 내 체크포인트 디렉토리 찾기"""
    dirs = [d for d in os.listdir(model_path)
            if os.path.isdir(os.path.join(model_path, d))]
    if not dirs:
        return None
    return dirs[0]  # G_100000 or G_300000 등


def load_metadata(lang_code):
    """metadata CSV에서 {id: text} 딕셔너리 반환"""
    csv_path = os.path.join(METADATA_DIR, f"{lang_code}_test.csv")
    if not os.path.exists(csv_path):
        print(f"  ⚠ Metadata not found: {csv_path}")
        return {}

    id_to_text = {}
    with open(csv_path, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f, delimiter="|")
        for row in reader:
            id_to_text[row["id"]] = row["text"]
    return id_to_text


def get_wav_ids(model_path, ckpt_dir):
    """모델의 generated_wav 폴더에서 wav 파일 ID 목록 반환"""
    wav_dir = os.path.join(model_path, ckpt_dir, "generated_wav")
    if not os.path.exists(wav_dir):
        return set()
    return {os.path.splitext(f)[0] for f in os.listdir(wav_dir) if f.endswith(".wav")}


def main():
    random.seed(RANDOM_SEED)

    # ─── Step 1: 모델 스캔 & 언어별 그룹핑 ───
    print("📂 Scanning models...")
    all_models = sorted([
        d for d in os.listdir(SAMPLES_DIR)
        if os.path.isdir(os.path.join(SAMPLES_DIR, d))
    ])

    # 모델별 정보 수집
    model_info = {}  # {model_name: {lang, ckpt_dir, wav_ids, wav_dir}}
    lang_to_models = defaultdict(list)

    for model_name in all_models:
        lang = get_model_lang(model_name)
        if lang is None:
            print(f"  ⚠ Unknown language for model: {model_name}, skipping")
            continue

        model_path = os.path.join(SAMPLES_DIR, model_name)
        ckpt_dir = get_checkpoint_dir(model_path)
        if ckpt_dir is None:
            print(f"  ⚠ No checkpoint dir for model: {model_name}, skipping")
            continue

        wav_ids = get_wav_ids(model_path, ckpt_dir)
        wav_dir = os.path.join(model_path, ckpt_dir, "generated_wav")

        model_info[model_name] = {
            "lang": lang,
            "ckpt_dir": ckpt_dir,
            "wav_ids": wav_ids,
            "wav_dir": wav_dir,
        }
        lang_to_models[lang].append(model_name)
        print(f"  ✓ {model_name} ({lang}) - {len(wav_ids)} wavs")

    print(f"\n  Total: {len(model_info)} models, {len(lang_to_models)} languages")

    # ─── Step 2: 언어별로 공통 샘플 선택 ───
    print("\n🎯 Selecting samples per language...")
    lang_selected = {}  # {lang: [list of 10 sample IDs]}

    for lang, models in sorted(lang_to_models.items()):
        # 해당 언어의 모든 모델에 공통으로 존재하는 sample ID 찾기
        common_ids = None
        for model_name in models:
            ids = model_info[model_name]["wav_ids"]
            if common_ids is None:
                common_ids = ids.copy()
            else:
                common_ids &= ids

        # metadata에도 존재하는 ID만 필터
        metadata = load_metadata(lang)
        common_ids = {sid for sid in common_ids if sid in metadata}

        if len(common_ids) < SAMPLES_PER_LANG:
            print(f"  ⚠ {lang}: only {len(common_ids)} common samples (need {SAMPLES_PER_LANG})")
            selected = sorted(common_ids)[:SAMPLES_PER_LANG]
        else:
            selected = sorted(random.sample(sorted(common_ids), SAMPLES_PER_LANG))

        lang_selected[lang] = selected
        display_name = LANG_DISPLAY.get(lang, lang)
        print(f"  ✓ {lang} ({display_name}): {len(selected)} samples from {len(models)} models")

    # ─── Step 3: Stimuli 생성 & A/B 분할 ───
    print("\n📋 Building stimuli...")
    stimuli_a = []
    stimuli_b = []

    for model_name in sorted(model_info.keys()):
        info = model_info[model_name]
        lang = info["lang"]
        metadata = load_metadata(lang)
        selected_ids = lang_selected.get(lang, [])

        for si, sample_id in enumerate(selected_ids):
            text = metadata.get(sample_id, f"[{sample_id}]")
            wav_filename = f"{sample_id}.wav"

            stimulus = {
                "id": f"{model_name}_{si+1:02d}",
                "model": model_name,
                "lang": lang,
                "text": text,
                "roman": "(Roman transcription TBD)",  # 추후 추가
                "audio": f"./samples/{model_name}/{wav_filename}",
                "_wav_src": os.path.join(info["wav_dir"], wav_filename),  # symlink용 (config에는 안 들어감)
            }

            if si < SPLIT_INDEX:
                stimuli_a.append(stimulus)
            else:
                stimuli_b.append(stimulus)

    print(f"  Type A: {len(stimuli_a)} stimuli")
    print(f"  Type B: {len(stimuli_b)} stimuli")

    # ─── Step 4: 심볼릭 링크 생성 ───
    print("\n🔗 Creating audio symlinks...")
    for label, output_dir, stimuli_list in [("A", OUTPUT_DIR_A, stimuli_a),
                                             ("B", OUTPUT_DIR_B, stimuli_b)]:
        link_count = 0
        for stim in stimuli_list:
            wav_src = stim["_wav_src"]
            # samples/{MODEL_NAME}/filename.wav
            model_name = stim["model"]
            wav_filename = os.path.basename(wav_src)
            dest_dir = os.path.join(output_dir, "samples", model_name)
            os.makedirs(dest_dir, exist_ok=True)

            dest_path = os.path.join(dest_dir, wav_filename)
            if os.path.exists(dest_path) or os.path.islink(dest_path):
                os.remove(dest_path)
            os.symlink(wav_src, dest_path)
            link_count += 1

        print(f"  Type {label}: {link_count} symlinks in {output_dir}/samples/")

    # ─── Step 5: config.js 생성 ───
    print("\n📝 Generating config.js files...")

    for label, output_dir, stimuli_list, storage_key in [
        ("A", OUTPUT_DIR_A, stimuli_a, "urbert_eval_A"),
        ("B", OUTPUT_DIR_B, stimuli_b, "urbert_eval_B"),
    ]:
        # _wav_src 필드 제거 (config.js에 불필요)
        clean_stimuli = []
        for s in stimuli_list:
            clean = {k: v for k, v in s.items() if not k.startswith("_")}
            clean_stimuli.append(clean)

        stimuli_json = json.dumps(clean_stimuli, ensure_ascii=False, indent=2)

        config_content = f"""/**
 * UR-BERT Multilingual TTS MOS Evaluation - Auto-generated Config
 * Type: {label}
 * Generated: {datetime.now().isoformat()}
 * Models: {len(model_info)}, Stimuli: {len(clean_stimuli)}
 */

const EVAL_CONFIG = {{
  title: "UR-BERT Multilingual TTS Evaluation",
  experimentType: "{label}",
  itemsPerPage: 10,
  storageKey: "{storage_key}",
  sheetUrl: "{SHEET_URL}"
}};

const stimuli = {stimuli_json};
"""

        output_file = os.path.join(output_dir, "config.js")
        with open(output_file, "w", encoding="utf-8") as f:
            f.write(config_content)
        print(f"  ✓ {output_file} ({len(clean_stimuli)} stimuli)")

    # ─── Summary ───
    print("\n" + "=" * 60)
    print("✅ Demo experiment built successfully!")
    print(f"   Models: {len(model_info)}")
    print(f"   Languages: {len(lang_to_models)}")
    print(f"   Type A: {len(stimuli_a)} stimuli → {OUTPUT_DIR_A}/")
    print(f"   Type B: {len(stimuli_b)} stimuli → {OUTPUT_DIR_B}/")
    print()
    print("🚀 로컬 테스트 방법:")
    print(f"   cd {OUTPUT_DIR_A}")
    print(f"   python3 -m http.server 8080")
    print(f"   → 브라우저에서 http://localhost:8080 접속")
    print()
    print(f"   cd {OUTPUT_DIR_B}")
    print(f"   python3 -m http.server 8081")
    print(f"   → 브라우저에서 http://localhost:8081 접속")
    print("=" * 60)


if __name__ == "__main__":
    main()
