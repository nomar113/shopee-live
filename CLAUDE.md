# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Shopee automation bot that interacts with the Shopee app on an Android device via ADB (Android Debug Bridge). It automates collecting coins from Shopee Lives and playing the Shopee Candy mini-game using screen capture and OpenCV template matching.

## Prerequisites

- Android device connected via USB with ADB debugging enabled
- `adb` command available in PATH
- Tesseract OCR installed (used by pytesseract)
- Python 3.x

## Commands

```bash
# Install dependencies
pip install -r requirements.txt

# Run the main lives coin collector
python main.py

# Run the Shopee Candy game bot (standalone, run from shopee-candy/)
cd shopee-candy && python main.py

# Crop a template image from a screenshot (interactive GUI)
python cut.py
```

## Architecture

The project has two independent automation flows:

### Lives Coin Collector (main entry point)
- **`main.py`** — Async main loop that cycles through Shopee lives, claims coins, waits for timers, and scrolls to find new lives.
- **`lives/core.py`** (`Live` class) — All live-stream coin logic: template matching to detect coin/claim buttons, OCR to read countdown timers, scroll to next live on failed claims.
- **`ADB/core.py`** (`ADB` class) — Wrapper around `adb` CLI for screenshots (`capture_screenshot`), swipe scrolling (`scrool`), and taps (`tap` is a static method).

### Shopee Candy Bot (`shopee-candy/`)
- **`shopee-candy/main.py`** — Standalone loop that detects the candy game UI, auto-taps hammer coordinates, and sends push notifications via ntfy.sh on errors.
- **`shopee-candy/opencv.py`** — Standalone tap sequence script for candy game levels.

### Image Recognition Pattern
Both flows use the same pattern: capture screenshot via ADB → load with OpenCV → grayscale conversion → `cv2.matchTemplate` with normalized cross-correlation → threshold filtering. Template images are stored in `img/lives/` for the lives flow.

## Key Details

- The project language is Portuguese (Brazilian) — variable names, logs, and comments are often in PT-BR.
- `ADB.tap()` is a **static method** (no `self`), while `scrool()` and `capture_screenshot()` are instance methods.
- Screenshots are saved to `./img/screenshot.png` — the bot reads from this path for all template matching.
- Template matching thresholds: 0.95 for coin detection, 0.80 for claim button detection.
- `waitToReceiveCoins` uses OCR (pytesseract) to read countdown timers from a specific screen region, then sleeps for that duration.
- The `.gitignore` uses a whitelist approach — it ignores everything then explicitly allows `.py` files, `requirements.txt`, and specific template images.
