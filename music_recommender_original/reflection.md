# Reflection: Profile Comparisons

## Pair 1 — Default pop/happy (energy=0.8) vs Classical high-energy (energy=0.99)

**Pop/happy top results:** Sunrise City, Gym Hero, Rooftop Lights
**Classical/peaceful top results:** Moonlit Sonata, Iron Curtain, Signal Drop

The pop profile behaves exactly as the algorithm intends: Sunrise City wins cleanly on all
three dimensions (genre + mood + energy proximity). The results feel right — a bright,
upbeat pop playlist.

The classical profile is where things get interesting. The user asked for `energy=0.99` —
as intense as possible — but got Moonlit Sonata (energy=0.18) at #1. That is the opposite
of what they described. The reason is that genre+mood labels (+2.5 combined) outweigh the
huge energy gap. Iron Curtain at energy=0.97 is a far closer experiential match but loses
because it carries no genre or mood bonus.

**Why this matters:** The pop profile shows the system working as designed. The classical
profile exposes the core flaw — label bonuses can override what the user actually wants to
hear. Two profiles, same scoring logic, completely different levels of trustworthiness.

---

## Pair 2 — Non-existent genre (bluegrass/chill/0.4) vs Genre-vs-mood conflict (pop/angry/0.5)

**Bluegrass top results:** Lofi/chill songs ranked by energy proximity
**Pop/angry top results:** Pop songs with wrong mood beating the only angry song (Iron Curtain)

Both profiles surface a silent failure mode. The bluegrass user gets lofi songs with no
warning that their requested genre doesn't exist — the system returns results that look
plausible but are fundamentally a fallback. The pop/angry user gets cheerful pop tracks
because genre weight (1.0) beats mood weight (1.5)... wait, actually mood (1.5) > genre
(1.0) under energy-first weights. Let me reconsider: under original weights (genre=2.0),
a pop/wrong-mood song beats an angry/wrong-genre song. Under energy-first (genre=1.0),
the mood match wins instead — a pop/angry user would get Iron Curtain ranked higher.

**Why this matters:** These profiles test whether the system handles "no good match"
gracefully. It doesn't — it returns the least-bad option with no signal to the user that
the request was unanswerable. Real recommenders surface a "no results" message or broaden
the search explicitly; this system quietly degrades.

---

## Pair 3 — Original weights (pop/happy/0.8) vs Energy-first weights (pop/happy/0.8)

**Original weights top 5:** Sunrise City (4.48), Gym Hero (2.87), Rooftop Lights (2.46), ...
**Energy-first weights top 5:** Sunrise City (~4.46), Gym Hero (~3.74), Rooftop Lights (~3.42), ...

Same profile, same top-3 order, different scores and tighter gaps. Under energy-first,
Rooftop Lights (indie pop, happy, energy=0.76) moves much closer to Gym Hero because its
energy proximity score doubled. Musically, Rooftop Lights is probably a better match for
a pop/happy/0.8 listener than Gym Hero (which skews more intense at 0.93), yet it still
ranks third under both weight schemes because Gym Hero's genre bonus keeps it ahead.

**Why this matters:** Doubling energy's importance made the rankings more nuanced — the
gap between #2 and #3 shrank from 0.41 to 0.32 — but didn't flip the order. This suggests
the original weights were not wildly miscalibrated for the pop/happy profile, just slightly
less sensitive to energy differences within the same genre cluster. The experiment confirmed
the system is more robust for "mainstream" profiles than adversarial ones.

---

## Pair 4 — Pop/happy (energy=0.8) vs Classical/peaceful (energy=0.99) under energy-first weights

**Pop/happy energy-first:** Sunrise City first, same story as original
**Classical/peaceful energy-first:** Moonlit Sonata still first (score dropped 3.69 → 2.88),
Iron Curtain climbed from 0.98 → 1.96

Doubling energy's weight hurt Moonlit Sonata (its 0.81 energy gap was penalized harder)
and helped Iron Curtain (its 0.02 gap was rewarded more). The gap between them shrank from
2.71 to 0.92 — a meaningful shift. If energy weight were tripled or quadrupled, Iron Curtain
would eventually overtake Moonlit Sonata. That would be the more experientially honest result
for a user explicitly asking for energy=0.99.

**Why this matters:** This pair shows that weight tuning is not just cosmetic — it directly
controls which bias wins. The original weights favored label fidelity (giving classical fans
their classical song regardless of energy). Energy-first weights push toward experiential
fidelity (giving high-energy seekers the highest-energy song). Neither is objectively correct;
they reflect a design choice about what "a good recommendation" means.
