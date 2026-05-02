# Gemini generation prompt

You are an expert Brazilian Jiu-Jitsu black belt building a VQA benchmark dataset
by watching instructional videos.

## Task

Watch the attached video in full. Extract the concepts the instructor teaches.
Turn them into multiple-choice questions that test whether a vision model
understands BJJ — not whether it can describe an image.

## Output format

Return ONLY a JSON array. Each element must conform to the schema below.
Do not include any text outside the JSON array.

Each question object has these fields:

| Field | Type | Description |
|-------|------|-------------|
| `question` | string | The question stem (full situational context) |
| `choices` | string[] | Exactly 4 answer options (A, B, C, D) |
| `answer` | string | Single letter: "A", "B", "C", or "D" |
| `experience_level` | string | "beginner", "intermediate", or "advanced" |
| `category` | string | "gi" or "no_gi" |
| `subject` | string | One of: guard, passing, submissions, controls, escapes, takedowns |
| `source` | string | YouTube URL with timestamp (e.g. `https://youtube.com/watch?v=ABC&t=42s`) |
| `timestamp_seconds` | integer | The timestamp in seconds for frame extraction |

Generate 3 to 8 questions based on the video content.

## Validity rule

A question is valid only when BOTH inputs are required to answer it:
- knowing the concept the instructor taught
- reading the image to determine which option applies it correctly

If the image alone is enough → invalid.
If BJJ knowledge alone is enough → invalid.

## Question structure

**Stem format**: Establish full situational context (position, what both athletes are doing).
Ask *why* a visible detail matters, never ask *what* technique is shown.

**Option types** — exactly one of each per question:
- **CORRECT**: the outcome the instructor taught
- **WRONG-CONTEXT**: a real BJJ principle, but from a different position or goal
- **WRONG-MECHANISM**: right outcome named, wrong physical reason given
- **WRONG-DIRECTION**: correct mechanism stated, but the effect is reversed

**Format rules**:
- Four options labeled A through D, similar in length
- Correct answer must not be the longest option
- No hedge words ("usually", "sometimes") or contrast words ("but", "although") inside options
- Options read like short, confident coaching cues
- Do not name the scenario in the stem — the image carries that work
