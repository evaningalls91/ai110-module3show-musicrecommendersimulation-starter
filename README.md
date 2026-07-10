# 🎵 Music Recommender Simulation

## Project Summary

In this project you will build and explain a small music recommender system.

Your goal is to:

- Represent songs and a user "taste profile" as data
- Design a scoring rule that turns that data into recommendations
- Evaluate what your system gets right and wrong
- Reflect on how this mirrors real world AI recommenders

Replace this paragraph with your own summary of what your version does.

---

## How The System Works

This is a content-based recommender: it matches songs to a user by comparing
their measurable attributes, with no ratings or listening history involved. The `Song` stores two text tags, `genre` and `mood`, plus five numeric audio features: `energy`, `tempo_bpm`, `valence`, `danceability`, and `acousticness`. The UserProfile stores the user's taste as targets: a `favorite_genre` and `favorite_mood`, a `target_energy`, and a `likes_acoustic` flag, plus optional `target_valence`, `target_danceability`, and `target_tempo`.

The algorithm is hybrid and scores both numerica and categorical features.

- Numeric features: similarity = `1 - |target - value|`, so an exact match
  scores 1 and a far-off value scores near 0. Tempo is on a different scale
  (BPM), so its distance is normalized first. `acousticness` uses the
  `likes_acoustic` flag as its target (1.0 if they like acoustic, else 0.0).
- Categorical features: an exact `genre` or `mood` match earns a bonus.

Each feature has a weight (genre and energy matter most; tempo least), and
the weighted results are averaged into a single 0–1 score. Only the
preferences the user actually provides count toward that average, so a sparse
profile still works.

---

## Getting Started

### Setup

1. Create a virtual environment (optional but recommended):

   ```bash
   python -m venv .venv
   source .venv/bin/activate      # Mac or Linux
   .venv\Scripts\activate         # Windows

   ```

2. Install dependencies

```bash
pip install -r requirements.txt
```

3. Run the app:

```bash
python -m src.main
```

### Running Tests

Run the starter tests with:

```bash
pytest
```

You can add more tests in `tests/test_recommender.py`.

---

## Sample Recommendation Output

============================================================
🎵 MUSIC RECOMMENDER  
============================================================

## Your taste profile

Genre pop
Mood happy
Energy 0.8
Valence 0.8
Danceability 0.8
Likes Acoustic False
Tempo 120

## Top 5 recommendations

1. Sunrise City — Neon Echo
   pop / happy
   Score 0.97 ███████████████████░
   Why:
   • matches your favorite genre (pop)
   • matches your mood (happy)
   • energy close to target (0.82 vs 0.80)
   • danceability fits your taste (0.79)
   • positivity fits your taste (0.84)
   • tempo near your target (118 BPM)

2. Gym Hero — Max Pulse
   pop / intense
   Score 0.77 ███████████████░░░░░
   Why:
   • matches your favorite genre (pop)
   • energy close to target (0.93 vs 0.80)
   • positivity fits your taste (0.77)
   • produced/electronic sound you like (0.05)
   • danceability fits your taste (0.88)
   • tempo near your target (132 BPM)

3. First Light Ahead — Horizon Line
   pop / hopeful
   Score 0.75 ███████████████░░░░░
   Why:
   • matches your favorite genre (pop)
   • energy close to target (0.68 vs 0.80)
   • positivity fits your taste (0.83)
   • danceability fits your taste (0.71)
   • tempo near your target (116 BPM)

4. Rooftop Lights — Indigo Parade
   indie pop / happy
   Score 0.71 ██████████████░░░░░░
   Why:
   • matches your mood (happy)
   • energy close to target (0.76 vs 0.80)
   • positivity fits your taste (0.81)
   • danceability fits your taste (0.82)
   • tempo near your target (124 BPM)

5. Bubblegum Circuit — Sticker Club
   electropop / playful
   Score 0.56 ███████████░░░░░░░░░
   Why:
   • energy close to target (0.80 vs 0.80)
   • danceability fits your taste (0.85)
   • positivity fits your taste (0.88)
   • produced/electronic sound you like (0.12)
   • tempo near your target (122 BPM)

---

## Experiments You Tried

Use this section to document the experiments you ran. For example:

- What happened when you changed the weight on genre from 2.0 to 0.5
- What happened when you added tempo or valence to the score
- How did your system behave for different types of users

---

## Limitations and Risks

Summarize some limitations of your recommender.

Examples:

- It only works on a tiny catalog
- It does not understand lyrics or language
- It might over favor one genre or mood

You will go deeper on this in your model card.

---

## Reflection

Read and complete `model_card.md`:

[**Model Card**](model_card.md)

Write 1 to 2 paragraphs here about what you learned:

- about how recommenders turn data into predictions
- about where bias or unfairness could show up in systems like this
