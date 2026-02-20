#!/usr/bin/env python3
"""
generate_config.py

오디오 파일 구조에서 Type A / Type B config.js를 자동 생성합니다.

사용법:
  1. 아래 SETTINGS를 본인 환경에 맞게 수정하세요.
  2. python generate_config.py 실행
  3. ur-bert-eval-A/config.js 와 ur-bert-eval-B/config.js 가 자동 생성됩니다.

예상 폴더 구조:
  samples/
  ├── model_01/
  │   ├── ko_001.wav   (sample 0 → Type A)
  │   ├── en_001.wav   (sample 1 → Type A)
  │   ├── zh_001.wav   (sample 2 → Type A)
  │   ├── ja_001.wav   (sample 3 → Type A)
  │   ├── fr_001.wav   (sample 4 → Type A)
  │   ├── ko_002.wav   (sample 5 → Type B)
  │   ├── en_002.wav   (sample 6 → Type B)
  │   ├── zh_002.wav   (sample 7 → Type B)
  │   ├── ja_002.wav   (sample 8 → Type B)
  │   └── fr_002.wav   (sample 9 → Type B)
  ├── model_02/
  │   └── ...
  └── ...

분할 방식:
  모델당 10개 샘플 → 앞 5개(index 0~4) = Type A, 뒤 5개(index 5~9) = Type B
  (SPLIT_INDEX 변수로 조절 가능)
"""

import os
import json
import glob
from datetime import datetime

# ═══════════════════════════════════════════
# SETTINGS (본인 환경에 맞게 수정하세요)
# ═══════════════════════════════════════════

SAMPLES_DIR = "./samples"  # 오디오 파일이 있는 폴더
OUTPUT_DIR_A = "../ur-bert-eval-A"
OUTPUT_DIR_B = "../ur-bert-eval-B"
AUDIO_EXT = "*.wav"  # 또는 "*.mp3"

# 모델당 10개 샘플 중, 앞 SPLIT_INDEX개 → Type A, 나머지 → Type B
SPLIT_INDEX = 5

# Google Apps Script URL (결과 자동 수집용)
SHEET_URL = "https://script.google.com/macros/s/AKfycby6_3EvfoU0mcQg2IzBdmhLFlAPIn3XBzpfNbuuBigz-LWUwX3CgYMWBANXTHHSLa-umQ/exec"

# ─── 텍스트 + Roman script 매핑 ───
# key: 모델 내 샘플 인덱스 (0~9)
# 실제 실험 문장과 roman script로 교체하세요.
# 예시: 5개 언어 × 2세트 = 10개
SENTENCE_MAP = {
    # ─── Type A (index 0~4) ───
    0:  {"lang": "ko", "text": "오늘 날씨가 정말 좋습니다.",
         "roman": "o-neul nal-ssi-ga jeong-mal jo-seum-ni-da"},
    1:  {"lang": "en", "text": "The weather is really nice today.",
         "roman": "The weather is really nice today."},
    2:  {"lang": "zh", "text": "今天天气真好。",
         "roman": "jīn tiān tiān qì zhēn hǎo"},
    3:  {"lang": "ja", "text": "今日はとてもいい天気ですね。",
         "roman": "kyō wa totemo ii tenki desu ne"},
    4:  {"lang": "fr", "text": "Il fait vraiment beau aujourd'hui.",
         "roman": "il fɛ vʁɛmɑ̃ bo oʒuʁdɥi"},
    # ─── Type B (index 5~9) ───
    5:  {"lang": "ko", "text": "서울의 봄은 매우 아름답습니다.",
         "roman": "seo-u-rui bom-eun mae-u a-reum-dap-seum-ni-da"},
    6:  {"lang": "en", "text": "Spring in Seoul is very beautiful.",
         "roman": "Spring in Seoul is very beautiful."},
    7:  {"lang": "zh", "text": "首尔的春天非常美丽。",
         "roman": "shǒu ěr de chūn tiān fēi cháng měi lì"},
    8:  {"lang": "ja", "text": "ソウルの春はとても美しいです。",
         "roman": "souru no haru wa totemo utsukushii desu"},
    9:  {"lang": "fr", "text": "Le printemps à Séoul est très beau.",
         "roman": "lə pʁɛ̃tɑ̃ a seul ɛ tʁɛ bo"},
}

# ═══════════════════════════════════════════


def generate_stimuli(models_dir, audio_ext):
    """전체 stimuli를 생성하고 A/B로 분할합니다."""
    stimuli_a = []
    stimuli_b = []

    models = sorted([
        d for d in os.listdir(models_dir)
        if os.path.isdir(os.path.join(models_dir, d))
    ])

    print(f"Found {len(models)} models")

    for mi, model in enumerate(models):
        model_dir = os.path.join(models_dir, model)
        audio_files = sorted(glob.glob(os.path.join(model_dir, audio_ext)))

        print(f"  [{mi+1:02d}] {model}: {len(audio_files)} samples")

        for si, audio_path in enumerate(audio_files):
            filename = os.path.basename(audio_path)
            rel_path = f"./samples/{model}/{filename}"

            # 텍스트 매핑 가져오기
            info = SENTENCE_MAP.get(si, {
                "lang": "unknown",
                "text": f"[Text for sample {si}]",
                "roman": f"[Roman script for sample {si}]"
            })

            stimulus = {
                "id": f"m{mi+1:02d}_s{si+1:02d}",
                "model": model,
                "lang": info["lang"],
                "text": info["text"],
                "roman": info["roman"],
                "audio": rel_path
            }

            # 분할: 앞쪽 → A, 뒤쪽 → B
            if si < SPLIT_INDEX:
                stimuli_a.append(stimulus)
            else:
                stimuli_b.append(stimulus)

    return stimuli_a, stimuli_b, len(models)


def write_config(output_dir, experiment_type, stimuli_list, num_models):
    """config.js 파일을 생성합니다."""
    os.makedirs(output_dir, exist_ok=True)
    output_file = os.path.join(output_dir, "config.js")

    storage_key = f"urbert_eval_{experiment_type.lower()}"

    stimuli_json = json.dumps(stimuli_list, ensure_ascii=False, indent=2)

    config_content = f"""/**
 * UR-BERT Multilingual TTS MOS Evaluation - Auto-generated Config
 * Type: {experiment_type}
 * Generated: {datetime.now().isoformat()}
 * Models: {num_models}, Stimuli: {len(stimuli_list)}
 */

const EVAL_CONFIG = {{
  title: "UR-BERT Multilingual TTS Evaluation",
  experimentType: "{experiment_type}",
  itemsPerPage: 10,
  storageKey: "{storage_key}",
  sheetUrl: "{SHEET_URL}"
}};

const stimuli = {stimuli_json};
"""

    with open(output_file, "w", encoding="utf-8") as f:
        f.write(config_content)

    print(f"  → {output_file} ({len(stimuli_list)} stimuli)")


def main():
    stimuli_a, stimuli_b, num_models = generate_stimuli(SAMPLES_DIR, AUDIO_EXT)

    print(f"\n📋 Split results:")
    print(f"  Type A: {len(stimuli_a)} stimuli (sample index 0~{SPLIT_INDEX-1})")
    print(f"  Type B: {len(stimuli_b)} stimuli (sample index {SPLIT_INDEX}~9)")

    print(f"\n📝 Generating config files:")
    write_config(OUTPUT_DIR_A, "A", stimuli_a, num_models)
    write_config(OUTPUT_DIR_B, "B", stimuli_b, num_models)

    print(f"\n✅ Done! Config files generated for Type A and Type B.")
    print(f"   - {OUTPUT_DIR_A}/config.js")
    print(f"   - {OUTPUT_DIR_B}/config.js")
    print(f"   Make sure index.html is also present in both directories.")


if __name__ == "__main__":
    main()
