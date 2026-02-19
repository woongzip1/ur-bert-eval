# UR-BERT Multilingual TTS Evaluation

Interspeech 2025 listening test for multilingual TTS MOS evaluation.

**Live page**: [woongzip1.github.io/ur-bert-eval](https://woongzip1.github.io/ur-bert-eval)

## Setup

### 1. Prepare audio samples

```
samples/
├── model_01/
│   ├── ko_001.wav
│   ├── en_001.wav
│   ├── zh_001.wav
│   ├── ja_001.wav
│   └── fr_001.wav
├── model_02/
│   └── ...
└── model_45/
    └── ...
```

### 2. Generate config.js

Edit `generate_config.py` with your actual text/roman script, then:

```bash
python generate_config.py
```

This auto-generates `config.js` from the folder structure.

### 3. Deploy to GitHub Pages

```bash
git init
git remote add origin git@github.com:woongzip1/ur-bert-eval.git
git add .
git commit -m "Initial evaluation page"
git push -u origin main
```

Then go to **Settings → Pages → Source: main branch** in the GitHub repo.

## Features

- Per-evaluator randomized stimulus order (seeded shuffle, reproducible)
- Progress auto-saved to localStorage (can resume across sessions)
- Keyboard shortcuts: press 1-5 to rate the next unanswered item
- CSV export with evaluator ID, model, language, MOS score, and timestamp
- Mobile-responsive

## Audio format note

GitHub Pages repos have a soft limit of ~1GB. For 225 WAV files (10s each at 16kHz mono), that's roughly:

| Format | Per file | Total (225) |
|--------|----------|-------------|
| WAV 16kHz mono 16bit | ~320KB | ~70MB |
| WAV 22kHz mono 16bit | ~440KB | ~97MB |
| WAV 48kHz stereo 16bit | ~1.9MB | ~430MB |
| MP3 128kbps | ~160KB | ~35MB |

If your WAVs are large (high sample rate / stereo), consider converting to mono 22kHz WAV or high-bitrate MP3.

## CSV Output

```
evaluator,stimulus,model,lang,mos,timestamp
listener_01,m03_s02,model_03,en,4,2025-02-19T14:30:00.000Z
...
```
