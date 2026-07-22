# OCR Vocab Bot — Japanese Book Vocabulary Extractor & Spaced Repetition Trainer

A Discord bot that turns photos of Japanese book pages into study-ready vocabulary —
extracting highlighted words via an LLM vision model, storing them in a personal
database, exporting them to Anki/CSV/Google Sheets, and (in progress) using a
spaced-repetition model to decide what's actually due for review.

Built as a personal tool for my own Japanese reading practice, and as a project
demonstrating an end-to-end applied AI pipeline: ingestion → extraction → persistence
→ evaluation → modeling.

<img width="400" height="269" alt="Screen Recording 2026-07-22 at 12 13 25 AM" src="https://github.com/user-attachments/assets/269debbd-c198-4ee2-b420-7e3c87c6cfee" />

---

## What it does

1. **`/scan`** — attach a photo (or a `.zip` of multiple photos) of a book page with
   highlighted vocabulary. The bot:
   - Unzips/reads the image(s) in memory
   - Sends them to Gemini in throttled batches for OCR + vocabulary extraction
     (word, reading, meaning), using a structured output schema (Pydantic) to keep
     responses reliably parseable
   - Saves new words to a personal SQLite database, deduplicated per user
   - Exports the newly scanned words as an Anki deck (`.apkg`), a CSV, or pushes
     them directly to a Google Sheet

2. **`/quiz`** — quizzes on saved vocabulary using a modal-based, all-at-once answer
   format. Every answer (correct/incorrect) is logged with a timestamp, building a
   review history per word.

3. **`/all_words`** — view everything saved so far.

4. **Daily scheduled quiz** — posts an automatic review session at a set time each day.

5. **(In progress) Review prioritization model** — using the accumulated review
   history to predict which words are most at risk of being forgotten, based on
   Duolingo's published half-life regression approach, rather than a naive
   "longest since reviewed" heuristic.

---

## Architecture

```
Discord (/scan, /quiz, /all_words)
        │
        ▼
  bot.py (command routing, orchestration)
        │
        ├──► util_functions.py   (zip extraction, batching/throttling)
        ├──► gemini_ocr.py       (Gemini API calls, structured JSON output)
        ├──► export_functions.py (Anki / CSV / Google Sheets export)
        ├──► quiz_commands.py    (quiz UI: embeds, buttons, modals)
        └──► database.py         (SQLite: vocab + review_log tables)
```

Each module has a single responsibility — `bot.py` never touches SQL directly,
`database.py` never knows about Discord, `gemini_ocr.py` never knows about export
formats. This kept the project maintainable while iterating on each piece
independently.

---

## Design decisions worth noting

- **SQLite over a hosted DB**: this is a personal-scale tool (single user / small
  server), so a single-file database is simpler to reason about and deploy than
  provisioning a separate database service.
- **Deduplication on `(client_id, word, reading)`, not `(client_id, word, reading, meaning)`**:
  early testing showed Gemini's `meaning` field can vary in phrasing between
  identical scans of the same word (e.g. "to be singled out for criticism" vs.
  "to be targeted, to be singled out for criticism"), since it's LLM-generated
  free text, not a fixed dictionary lookup. Word + reading are stable identifiers;
  meaning is not.
- **`review_log` as a separate table, not a counter on `vocab`**: a running
  correct/incorrect tally can't answer "how long since this was last reviewed"
  or "in what order did reviews happen" — both are required inputs for a
  half-life decay model. A per-event log preserves the information a running
  count would throw away.
- **Batched Gemini calls with throttling**: sending multiple images per API call
  reduces request count (helpful against free-tier rate limits), but accuracy was
  observed to degrade at higher batch sizes — worth quantifying properly in the
  evaluation notebook (see below).

---

## Setup

```bash
git clone <this repo>
cd ocr-discord-bot
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

Create a `.env` file with:
```
DISCORD_TOKEN=
GUILD_ID=
GEMINI_API_KEY=
QUIZ_CHANNEL_ID=
YOUR_USER_ID=
```

If using Google Sheets export, add a `service_account.json` (Google Cloud service
account credentials with Sheets + Drive API access), and share the target sheet
with that service account's email.

Run:
```bash
python3 bot.py
```

---

## Deployment

Currently hosted on a Google Cloud `e2-micro` instance (Always Free tier),
managed via `systemd` for automatic restarts and persistence across reboots.

---

## Evaluation & Modeling — *(in progress)*

> TODO: OCR accuracy evaluation notebook — comparing extracted vocab against a
> hand-labeled ground truth set across different batch sizes, measuring
> precision/recall and the accuracy/latency tradeoff observed empirically during
> development.

> TODO: Half-life regression model — trained on accumulated `review_log` data,
> predicting per-word forgetting curves to prioritize `/quiz` selection, evaluated
> against the naive "longest since reviewed" heuristic baseline currently in use.

---

## Stack

Python · discord.py · Google Gemini API (`google-genai`) · Pydantic · SQLite ·
genanki · gspread · Google Cloud Compute Engine

---

## Status

Actively used for personal study. Core pipeline (scan → store → export → quiz) is
complete and deployed. Modeling component is pending sufficient accumulated review
data (collection ongoing).
