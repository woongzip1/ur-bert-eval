#!/usr/bin/env python3
"""
generate_config.py

오디오 파일 구조에서 config.js의 stimuli 배열을 자동 생성합니다.

사용법:
  1. 아래 SETTINGS를 본인 환경에 맞게 수정하세요.
  2. python generate_config.py 실행
  3. 생성된 config.js를 ur-bert-eval/ 폴더에 복사하세요.

예상 폴더 구조:
  samples/
  ├── model_01/
  │   ├── ko_001.wav
  │   ├── en_001.wav
  │   └── ...
  ├── model_02/
  │   └── ...
  └── ...
"""

import os
import json
import glob
from pathlib import Path

# ═══════════════════════════════════════════
# SETTINGS (본인 환경에 맞게 수정하세요)
# ═══════════════════════════════════════════

SAMPLES_DIR = "./samples"  # 오디오 파일이 있는 폴더
OUTPUT_FILE = "./config.js"
AUDIO_EXT = "*.wav"  # 또는 "*.mp3"

# 텍스트 + Roman script 매핑
# key: 파일명 패턴 또는 샘플 인덱스로 매핑
# 아래는 예시이며, 본인의 실제 텍스트로 교체하세요.
SENTENCE_MAP = {
    # sample_index: { lang, text, roman }
    0: {
        "lang": "ko",
        "text": "오늘 날씨가 정말 좋습니다.",
        "roman": "o-neul nal-ssi-ga jeong-mal jo-seum-ni-da"
    },
    1: {
        "lang": "en",
        "text": "The weather is really nice today.",
        "roman": "The weather is really nice today."
    },
    2: {
        "lang": "zh",
        "text": "今天天气真好。",
        "roman": "jīn tiān tiān qì zhēn hǎo"
    },
    3: {
        "lang": "ja",
        "text": "今日はとてもいい天気ですね。",
        "roman": "kyō wa totemo ii tenki desu ne"
    },
    4: {
        "lang": "fr",
        "text": "Il fait vraiment beau aujourd'hui.",
        "roman": "il fɛ vʁɛmɑ̃ bo oʒuʁdɥi"
    },
}

# ═══════════════════════════════════════════


def main():
    stimuli = []
    models = sorted([
        d for d in os.listdir(SAMPLES_DIR)
        if os.path.isdir(os.path.join(SAMPLES_DIR, d))
    ])

    print(f"Found {len(models)} models")

    for mi, model in enumerate(models):
        model_dir = os.path.join(SAMPLES_DIR, model)
        audio_files = sorted(glob.glob(os.path.join(model_dir, AUDIO_EXT)))

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

            stimuli.append({
                "id": f"m{mi+1:02d}_s{si+1:02d}",
                "model": model,
                "lang": info["lang"],
                "text": info["text"],
                "roman": info["roman"],
                "audio": rel_path
            })

    # Generate config.js
    config_content = f"""/**
 * UR-BERT Multilingual TTS MOS Evaluation - Auto-generated Config
 * Generated: {__import__('datetime').datetime.now().isoformat()}
 * Models: {len(models)}, Total stimuli: {len(stimuli)}
 */

const EVAL_CONFIG = {{
  title: "UR-BERT Multilingual TTS Evaluation",
  itemsPerPage: 10,
  storageKey: "urbert_eval_v1",
}};

const stimuli = {json.dumps(stimuli, ensure_ascii=False, indent=2)};
"""

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write(config_content)

    print(f"\n✅ Generated {OUTPUT_FILE}")
    print(f"   Total stimuli: {len(stimuli)}")
    print(f"   Models: {len(models)}")
    print(f"   Samples per model: {len(stimuli) // max(len(models), 1)}")


if __name__ == "__main__":
    main()
