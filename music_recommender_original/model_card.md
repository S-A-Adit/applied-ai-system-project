# 🎧 Model Card: Music Recommender Simulation

## 1. Model Name

**VibeMatch 1.0**

A content-based music recommender that scores songs against a user's declared taste profile and returns the top matches with plain-language explanations.

---

## 2. Goal / Task

VibeMatch tries to answer one question: given what a user tells us about their taste, which songs from the catalog are most likely to feel right to them right now?

It does this by comparing each song's attributes — genre, mood, and energy level — against the user's preferences, assigning a score, and returning the highest-scoring songs. It is built for classroom exploration, not real users. It assumes the user can describe their taste accurately upfront and that a small hand-labeled catalog is sufficient to test the idea.

---

## 3. Algorithm Summary

For every song in the catalog, the system adds up points across four rules:

- **Genre match:** If the song's genre matches your favorite genre, it earns 1.0 point. This is the biggest single signal — it says "you probably want music that sounds like what you already like."
- **Mood match:** If the song's mood label matches yours, it earns 1.5 points. Mood separates a "chill study session" playlist from a "pump-up workout" one.
- **Energy proximity:** Songs closer to your target energy level score higher, up to 2.0 points. The further the song's energy is from your target, the more points it loses. This is the most continuous signal — it rewards songs that feel right in intensity.
- **Acousticness fit:** If you said you like acoustic music, songs with higher acousticness get a small bonus (up to 0.5 points). If you prefer electronic sounds, the bonus flips to favor low-acousticness songs. This field is optional.

The maximum possible score is **5.0**. Songs are ranked from highest to lowest and the top five are returned with a brief reason explaining what matched.

---

## 4. Data Used

- **Catalog size:** 18 songs stored in `data/songs.csv`
- **Features per song:** id, title, artist, genre, mood, energy (0.0–1.0), tempo BPM, valence, danceability, acousticness (0.0–1.0)
- **Genres represented:** pop, lofi, rock, ambient, jazz, synthwave, indie pop, hip-hop, R&B, classical, EDM, country, folk, metal, reggae (15 genres)
- **Moods represented:** happy, chill, intense, relaxed, focused, moody, energetic, romantic, peaceful, euphoric, nostalgic, melancholic, angry, breezy (14 moods)
- **Key limits:** Most genres have only one song. The catalog skews toward high-energy tracks — 8 of 18 songs have energy above 0.75. Low-energy genres like ambient, classical, and folk are underrepresented. No data was added or removed from the starter set.
- **Whose taste does this reflect?** The catalog appears to reflect a broadly Western, English-language popular music listener. Genres like K-pop, Afrobeats, Latin pop, and classical non-Western traditions are absent entirely.

---

## 5. Strengths

- Works well for **mainstream profiles** like pop/happy or lofi/chill, where the catalog has multiple songs per genre and the labels are consistent with the energy levels.
- The **energy proximity formula** is effective within a genre — when two pop songs compete, the one whose energy is closer to the user's target correctly wins.
- **Explanations are transparent.** Every recommendation says exactly which factors matched and what the energy gap was. There are no black-box scores.
- The scoring logic is **easy to audit and adjust.** Changing a weight is one number change in one function, making it straightforward to test how sensitive the system is.

---

## 6. Limitations and Bias

The most significant weakness is the **label-over-vibe problem**: genre and mood are fixed point bonuses that dominate the score even when the continuous features tell a different story. In testing, a user asking for `genre=classical, mood=peaceful, energy=0.99` got Moonlit Sonata (energy=0.18) ranked first — a song that sounds the opposite of intense — because its genre+mood label bonus (+2.5) outweighed the 0.81 energy gap even after doubling the energy weight.

A second bias affects **rare-genre users.** Pop and lofi fans have two or three songs competing for the genre bonus. Metal, classical, and jazz fans have exactly one — so after that one song, their remaining four recommendations are driven by energy alone, producing a structurally weaker playlist.

The **catalog skews high-energy**, meaning users who prefer calm or ambient music face larger energy penalties across most of the catalog. A user targeting energy=0.1 will almost always receive recommendations with mediocre energy scores, while a user targeting energy=0.8 finds natural matches in nearly every genre.

Finally, the system has **no fallback or warning** when a user's preferred genre or mood doesn't exist in the catalog. It silently returns the next-best songs, which can look confident and relevant when they are actually just the least-bad options available.

---

## 7. Evaluation Process

I tested six user profiles manually, running each through the CLI and inspecting the top-5 results.

| Profile | Genre | Mood | Energy | Purpose |
|---------|-------|------|--------|---------|
| Default | pop | happy | 0.8 | Baseline — expected a clean match |
| Adversarial | classical | peaceful | 0.99 | Genre+mood contradict energy request |
| Missing genre | bluegrass | chill | 0.4 | No catalog match for genre |
| Conflict | pop | angry | 0.5 | Only angry song is in a different genre |
| Energy-first (pop) | pop | happy | 0.8 | Same as default, weights shifted |
| Energy-first (classical) | classical | peaceful | 0.99 | Same adversarial, weights shifted |

**What surprised me most:** Moonlit Sonata held the #1 spot for the classical/0.99 profile even after doubling the energy weight. I expected energy to have enough pull to surface Iron Curtain (energy=0.97) at the top, but the label bonus was too strong. The weight-shift experiment also showed that halving the genre weight for the pop/happy profile barely changed the top-3 order — which means genre was somewhat redundant for that profile because mood and energy already agreed.

---

## 8. Intended Use and Non-Intended Use

**Intended use:**
- Classroom exploration of how content-based filtering works
- Learning how scoring weights affect recommendations
- Practicing Python data structures, CSV handling, and ranking logic

**Not intended for:**
- Real users making real listening decisions — the catalog is too small and the scoring too simple
- Any situation where personalization accuracy matters — there is no learning, no history, and no feedback loop
- Users who expect the system to understand lyrics, cultural context, or subjective "feel" — it only sees numbers and labels

---

## 9. Ideas for Improvement

1. **Add a "no good match" signal.** If the top score falls below a threshold (e.g., 2.0 out of 5.0), tell the user that no close match was found rather than silently returning mediocre results.

2. **Balance the catalog.** Add at least two or three songs per genre so rare-genre users get a meaningful filtered pool instead of a single match followed by pure energy ranking.

3. **Replace fixed genre/mood bonuses with proximity scores.** Instead of "match or nothing," build a similarity map where adjacent genres (e.g., indie pop ↔ pop, ambient ↔ lofi) earn partial credit. This would soften the label-over-vibe problem without removing genre as a signal.

---

## 10. Personal Reflection

**Biggest learning moment**

The clearest moment came during the classical/high-energy adversarial test. I set `energy=0.99` expecting the system to surface an intense, driving song — and it returned Moonlit Sonata, a quiet classical piece with energy=0.18. At first I thought I had a bug. I didn't. The math was exactly correct: genre+mood labels contributed +2.5 fixed points, which the 0.81 energy gap couldn't overcome. That moment taught me something I didn't fully believe before building it: a scoring function can be logically correct and still produce results that feel completely wrong. "Correct by the rules" and "correct for the user" are different problems, and confusing them is probably the most common mistake in building simple AI systems.

**How AI tools helped — and when I had to double-check**

AI tools helped most during the design phase: drafting the algorithm recipe, choosing weights, and structuring the scoring function. The suggestions were fast and generally sound. Where I had to slow down and verify was whenever a tool described *what the output would be* — for example, claiming a weight change would "shift the rankings significantly." Running the actual code showed that halving the genre weight barely changed the top-3 order for the pop/happy profile. The prediction sounded reasonable but was wrong in practice. That reinforced a habit I want to keep: treat AI-generated analysis as a hypothesis, not a conclusion, and always run the code to check.

**What surprised me about simple algorithms feeling like recommendations**

I expected a four-rule scoring function to feel mechanical — like the system was obviously just matching keywords. What surprised me was how convincing the output looked for well-matched profiles. When Sunrise City came back at #1 for a pop/happy/0.8 listener with a score of 4.48 and a reason that said "genre=pop, mood=happy, energy 0.82 close to target," it genuinely felt like a thoughtful suggestion. The explanation did most of the work. A bare ranked list would have felt arbitrary; the same list with a one-line reason felt curated. That's worth remembering: the *presentation* of a recommendation carries almost as much weight as the recommendation itself, even when the underlying logic is simple.

**What I'd try next**

If I extended this project, the first thing I'd change is replacing fixed genre/mood bonuses with a continuous similarity score — so adjacent genres like indie pop and pop share partial credit instead of being treated as completely different. Second, I'd add a minimum-score threshold with a "no strong match found" message so the system stops returning confident-looking results when it has nothing good to offer. Third, I'd collect a feedback signal — even just a thumbs up or skip — and use it to re-weight the scoring function over time. That would turn a static rule set into something that actually learns, which is the gap between this simulation and a real recommender.
