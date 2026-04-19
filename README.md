# ABFM ITE Question Bank

A Streamlit app for browsing and self-quizzing on ABFM In-Training Examination questions from **2015–2024** (1,960 questions total).

## Features

| Mode | Description |
|------|-------------|
| 📖 Browse | Page through questions with filtering by year, keyword search, and answer reveal |
| 🧠 Quiz | Self-assessment with interactive answer selection and immediate feedback |
| 📊 Stats | Visual breakdown of the question bank by year, answer distribution, and more |

## Sidebar Controls

- **Year filter** — select one or more exam years (2015–2024, note: 2022 not included in source data)
- **Keyword search** — filter by text appearing in the question stem
- **Question count** shown live

## Setup

### 1. Parse the raw text file

Place `ABFM_ITE_2015_2024_Grouped.txt` in the project directory, then run:

```bash
python parse_abfm.py
```

This generates `abfm_questions.json` (required by the app).

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Run locally

```bash
streamlit run app.py
```

## Deployment (Streamlit Community Cloud)

1. Push this repo to GitHub (include `abfm_questions.json` — it is pre-generated)
2. Go to [share.streamlit.io](https://share.streamlit.io)
3. Connect your repo, set **Main file path** to `app.py`
4. Deploy — no secrets needed

## File Structure

```
├── app.py                          # Streamlit app
├── parse_abfm.py                   # One-time parser (text → JSON)
├── abfm_questions.json             # Pre-parsed question data
├── ABFM_ITE_2015_2024_Grouped.txt  # Source data (do not commit if large)
├── requirements.txt
└── README.md
```

## Data Format (`abfm_questions.json`)

Each question object:

```json
{
  "year": 2019,
  "number": 42,
  "stem": "A 55-year-old male presents with...",
  "choices": {
    "A": "Option text",
    "B": "Option text",
    "C": "Option text",
    "D": "Option text"
  },
  "correct_letter": "C",
  "correct_label": "Full answer text",
  "explanation": [
    {
      "heading": "Diagnosis",
      "bullets": [
        {
          "text": "Top-level bullet text",
          "sub": ["Sub-bullet 1", "Sub-bullet 2"]
        }
      ]
    }
  ],
  "explanation_raw": "Raw explanation text..."
}
```

## Notes

- 2022 exam is not present in the source dataset
- Years 2015–2018 have 240 questions each; 2019–2024 have 200 each
- This app is intended for **educational self-study only**
