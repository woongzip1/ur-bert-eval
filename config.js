/**
 * UR-BERT Multilingual TTS MOS Evaluation - Stimulus Configuration
 * 
 * 구조: 45 models × 5 samples = 225 stimuli
 * 
 * 각 stimulus 객체:
 *   id       : 고유 식별자 (CSV 결과에 기록됨)
 *   model    : 모델명 (분석용)
 *   lang     : 언어 코드 (예: "ko", "en", "zh", "ja", "fr")
 *   text     : 원문 텍스트
 *   roman    : Roman script / phonetic guide
 *   audio    : 오디오 파일 경로 (상대 경로)
 * 
 * ──────────────────────────────────────────────
 *  이 파일을 채우는 방법 (Python 스크립트 예시):
 * ──────────────────────────────────────────────
 * 
 *  import json, glob, os
 *  
 *  models = sorted(os.listdir("samples/"))
 *  stimuli = []
 *  for mi, model in enumerate(models):
 *      files = sorted(glob.glob(f"samples/{model}/*.wav"))
 *      for si, f in enumerate(files):
 *          stimuli.append({
 *              "id": f"m{mi+1:02d}_s{si+1:02d}",
 *              "model": model,
 *              "lang": "ko",           # 언어에 맞게 수정
 *              "text": "원문 텍스트",    # 실제 텍스트로 교체
 *              "roman": "romanization", # 실제 roman script로 교체
 *              "audio": f"./samples/{model}/{os.path.basename(f)}"
 *          })
 *  
 *  with open("stimuli_data.json", "w") as f:
 *      json.dump(stimuli, f, ensure_ascii=False, indent=2)
 * 
 * ──────────────────────────────────────────────
 */

const EVAL_CONFIG = {
  title: "UR-BERT Multilingual TTS Evaluation",
  itemsPerPage: 10,
  // 세션 키 (같은 브라우저에서 다른 실험과 충돌 방지)
  storageKey: "urbert_eval_v1",
};

/**
 * 아래는 placeholder 데이터입니다.
 * 실제 사용 시 본인의 모델/샘플 정보로 교체하세요.
 * 
 * 빠른 교체를 위해 Python으로 JSON을 생성한 뒤,
 * 이 배열을 통째로 교체하는 것을 추천합니다.
 */
const stimuli = [
  // ============================================================
  // Model 01 (예: baseline)
  // ============================================================
  {
    id: "m01_s01",
    model: "baseline",
    lang: "ko",
    text: "오늘 날씨가 정말 좋습니다.",
    roman: "o-neul nal-ssi-ga jeong-mal jo-seum-ni-da",
    audio: "./samples/baseline/ko_01.wav"
  },
  {
    id: "m01_s02",
    model: "baseline",
    lang: "en",
    text: "The weather is really nice today.",
    roman: "The weather is really nice today.",
    audio: "./samples/baseline/en_01.wav"
  },
  {
    id: "m01_s03",
    model: "baseline",
    lang: "zh",
    text: "今天天气真好。",
    roman: "jīn tiān tiān qì zhēn hǎo",
    audio: "./samples/baseline/zh_01.wav"
  },
  {
    id: "m01_s04",
    model: "baseline",
    lang: "ja",
    text: "今日はとてもいい天気ですね。",
    roman: "kyō wa totemo ii tenki desu ne",
    audio: "./samples/baseline/ja_01.wav"
  },
  {
    id: "m01_s05",
    model: "baseline",
    lang: "fr",
    text: "Il fait vraiment beau aujourd'hui.",
    roman: "il fɛ vʁɛmɑ̃ bo oʒuʁdɥi",
    audio: "./samples/baseline/fr_01.wav"
  },

  // ============================================================
  // Model 02 (예: proposed_v1)
  // ============================================================
  {
    id: "m02_s01",
    model: "proposed_v1",
    lang: "ko",
    text: "오늘 날씨가 정말 좋습니다.",
    roman: "o-neul nal-ssi-ga jeong-mal jo-seum-ni-da",
    audio: "./samples/proposed_v1/ko_01.wav"
  },
  {
    id: "m02_s02",
    model: "proposed_v1",
    lang: "en",
    text: "The weather is really nice today.",
    roman: "The weather is really nice today.",
    audio: "./samples/proposed_v1/en_01.wav"
  },
  // ... (나머지 모델/샘플도 같은 형식으로 추가)

  // ============================================================
  // 총 45 models × 5 samples = 225 entries
  // Python 스크립트로 생성하는 것을 강력 추천합니다.
  // ============================================================
];
