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

Real-world music recommenders (like Spotify's Discover Weekly) combine two strategies: **collaborative filtering**, which surfaces songs liked by users with similar taste, and **content-based filtering**, which matches songs to a listener's preferred attributes like genre, tempo, and energy. Production systems layer both, plus contextual signals (time of day, device, recent skips). This simulation focuses on **content-based filtering only** — it scores each song by how closely its attributes match a user's declared taste profile, prioritizing genre and mood as the strongest intent signals, then using energy and acousticness as continuous refinements to separate, for example, a focused study playlist from a high-energy workout set.

### Algorithm Recipe

For every song in the catalog, the system computes a **total score** by summing four weighted components:

| Rule | Weight | How it works |
|------|--------|--------------|
| Genre match | `2.0` | `+2.0` if `song.genre == user.favorite_genre`, else `0` |
| Mood match | `1.5` | `+1.5` if `song.mood == user.favorite_mood`, else `0` |
| Energy proximity | `1.0` | `1.0 − |song.energy − user.target_energy|` (ranges 0.0–1.0) |
| Acousticness fit | `0.5` | If `likes_acoustic`: `song.acousticness × 0.5`; else `(1 − song.acousticness) × 0.5` |

**Maximum possible score: 5.0** (perfect match on all four dimensions)

All songs are then sorted by total score (descending) and the top `k` are returned, each paired with a plain-language explanation of why it ranked where it did.

**Why these weights?** Genre carries the most weight (2.0) because it is the strongest intent signal — a pop fan almost never wants metal. Mood (1.5) comes second because it separates study-chill from workout-hype within the same genre. Energy (1.0) is a continuous refinement inside a genre/mood cluster. Acousticness (0.5) is the softest preference — a nice-to-have, not a dealbreaker.

### Potential Biases

- **Genre over-weighting:** Because genre holds a 2.0 weight — nearly half the maximum score — the system can bury a song that perfectly matches a user's mood, energy, and acoustic taste simply because it lives in the wrong genre category. A great jazz track might score lower than a mediocre pop track for a pop fan, even if the jazz song is a closer experiential fit.
- **Mood label sparsity:** With only one or two songs per mood in the catalog, a user whose favorite mood has no exact match will receive recommendations driven almost entirely by genre, making mood feel like a tiebreaker rather than a real signal.
- **Binary acoustic penalty:** The `likes_acoustic` flag treats preference as fully on or off. Users who enjoy a mix of acoustic and electronic songs have no way to express that nuance, and the scoring will always push them toward one extreme.
- **No personalization over time:** The system treats every session as a fresh start. It has no memory of what the user skipped or replayed, so it cannot learn or adapt.

### `Song` features used in scoring

- `genre` — categorical; matched directly against the user's preferred genre
- `mood` — categorical; matched directly against the user's preferred mood
- `energy` — continuous (0.0–1.0); compared against the user's target energy level
- `acousticness` — continuous (0.0–1.0); separa![alt text](<Screenshot 2026-04-05 183630.png>)tes acoustic/ambient songs from electronic/synthetic ones
- `tempo_bpm` — continuous (60–152 BPM); secondary refinement within a genre for pacing
- `danceability`, `valence` — present in the data but lower priority given their narrower variance across this catalog

### `UserProfile` fields driving recommendations

- `favorite_genre` — primary filter signal (e.g. `"lofi"`, `"pop"`)
- `favorite_mood` — secondary filter signal (e.g. `"chill"`, `"intense"`)
- `target_energy` — continuous preference; songs whose energy is closest to this value score higher
- `likes_acoustic` — boolean; boosts high-acousticness songs when `True`, penalizes them when `False`

---

## Getting Started

### Setup

1. Create a virtual environment (optional but recommended):

   ```bash
   python -m venv .venv
   source .venv/bin/activate      # Mac or Linux
   .venv\Scripts\activate         # Windows

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

The most important thing this project taught me is that a recommender can be mathematically correct and still feel wrong. When I set `energy=0.99` for a classical profile, the system returned a quiet, peaceful song with energy=0.18 — and the math was perfectly valid. That gap between "correct by the rules" and "correct for the user" is where most of the hard work in real AI systems lives. Writing the scoring function took an hour; figuring out *why* it behaved unexpectedly took much longer.

The second thing I learned is how much the explanation shapes the experience. The same ranked list with a one-line reason ("genre=pop, mood=happy, energy 0.82 close to your target") felt curated and trustworthy, while a bare list of song titles would have felt arbitrary. Simple algorithms can feel surprisingly intelligent when their reasoning is visible — which also means they can mislead users just as easily if that reasoning is wrong but still sounds confident.


---

## 7. `model_card_template.md`

Combines reflection and model card framing from the Module 3 guidance. :contentReference[oaicite:2]{index=2}  

```markdown
# 🎧 Model Card - Music Recommender Simulation

## 1. Model Name

Give your recommender a name, for example:

> VibeFinder 1.0

---

## 2. Intended Use

- What is this system trying to do
- Who is it for

Example:

> This model suggests 3 to 5 songs from a small catalog based on a user's preferred genre, mood, and energy level. It is for classroom exploration only, not for real users.

---

## 3. How It Works (Short Explanation)

Describe your scoring logic in plain language.

- What features of each song does it consider
- What information about the user does it use
- How does it turn those into a number

Try to avoid code in this section, treat it like an explanation to a non programmer.

---

## 4. Data

Describe your dataset.

- How many songs are in `data/songs.csv`
- Did you add or remove any songs
- What kinds of genres or moods are represented
- Whose taste does this data mostly reflect

---

## 5. Strengths

Where does your recommender work well

You can think about:
- Situations where the top results "felt right"
- Particular user profiles it served well
- Simplicity or transparency benefits

---

## 6. Limitations and Bias

Where does your recommender struggle

Some prompts:
- Does it ignore some genres or moods
- Does it treat all users as if they have the same taste shape
- Is it biased toward high energy or one genre by default
- How could this be unfair if used in a real product

---

## 7. Evaluation

How did you check your system

Examples:
- You tried multiple user profiles and wrote down whether the results matched your expectations
- You compared your simulation to what a real app like Spotify or YouTube tends to recommend
- You wrote tests for your scoring logic

You do not need a numeric metric, but if you used one, explain what it measures.

---

## 8. Future Work

If you had more time, how would you improve this recommender

Examples:

- Add support for multiple users and "group vibe" recommendations
- Balance diversity of songs instead of always picking the closest match
- Use more features, like tempo ranges or lyric themes

---

## 9. Personal Reflection

A few sentences about what you learned:

- What surprised you about how your system behaved
- How did building this change how you think about real music recommenders
- Where do you think human judgment still matters, even if the model seems "smart"
<Screenshot 2026-04-05 185256.png>
<Screenshot 2026-04-05 183630.png>
