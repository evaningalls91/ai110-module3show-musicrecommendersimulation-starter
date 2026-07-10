# 🎧 Model Card: Music Recommender Simulation

## 1. Model Name

BeatMaxr

---

## 2. Intended Use

Describe what your recommender is designed to do and who it is for.

What kind of recommendations does it generate
It ranks a small catalog of songs by how closely each one matches a user's stated taste and returns the top few with short reasons.

What assumptions does it make about the user
It assumes the user can describe their taste as a favorite genre and mood plus a few numeric targets, and that those numbers are on a 0 to 1 scale.

Is this for real users or classroom exploration
It is a classroom simulation for learning how recommenders work, not a production system for real listeners.

---

## 3. How the Model Works

Explain your scoring approach in simple language.

What features of each song are used
Each song has a genre, a mood, and numeric traits for energy, tempo, positivity, danceability, and how acoustic it sounds.

What user preferences are considered
The model looks at your favorite genre and mood, your target energy, positivity, danceability, and tempo, and whether you like acoustic music.

How does the model turn those into a score
It awards points when a song matches your taste, counts some features more heavily than others, and averages everything into a single score between 0 and 1.

What changes did you make from the starter logic
The scoring now uses every numeric feature with its own weight and returns ranked reasons, instead of matching on genre and mood alone.

---

## 4. Data

Describe the dataset the model uses.

How many songs are in the catalog
There are 20 songs in the catalog.

What genres or moods are represented
Genres range from pop, lofi, and rock to jazz, edm, metal, and orchestral, and moods include happy, chill, intense, melancholy, and euphoric.

Did you add or remove data
No, it uses the original 20-song starter dataset.

Are there parts of musical taste missing in the dataset
Yes, most genres appear only once, and there is nothing about artists, lyrics, era, or popularity.

---

## 5. Strengths

Where does your system seem to work well

User types for which it gives reasonable results
It works best for mainstream listeners, such as pop or lofi fans, who have several matching songs to rank.

Any patterns you think your scoring captures correctly
It correctly rewards exact genre and mood matches and songs whose energy, positivity, and danceability are close to the user's targets.

Cases where the recommendations matched your intuition
A profile copied from a real song ranked that song first at about 0.99, and an acoustic-only profile put the most acoustic songs on top.

---

## 6. Limitations and Bias

Where the system struggles or behaves unfairly.

Features it does not consider
It ignores artist, lyrics, era, popularity, and history, and it has no diversity control, so the top results can be near-duplicates.

Genres or moods that are underrepresented
Only pop and lofi have more than one song, so fans of niche genres like metal or jazz get just one real match.

Cases where the system overfits to one preference
A single heavy weight dominates everything, so weighting genre highly stacked all pop at the top, while weighting energy highly dropped every pop song.

Ways the scoring might unintentionally favor some users
It favors mainstream and average taste, and users who give fewer preferences get cleaner, more confident scores than users who describe themselves in detail.

---

## 7. Evaluation

How you checked whether the recommender behaved as expected.

Which user profiles you tested
I ran 12 edge cases, including empty, single-preference, non-existent genre, case-mismatched, exact-match, out-of-range, contradictory, all-neutral, and acoustic-only profiles.

What you looked for in the recommendations
I checked that scores stayed sensible, that the empty profile did not crash, and that the top songs actually matched the stated taste.

What surprised you
Out-of-range inputs produced negative scores, and giving the model more preferences often produced weaker, less confident scores than giving it just one.

Any simple tests or comparisons you ran
I compared the same profile under different weights and confirmed that removing the mood preference and setting the mood weight to zero give the exact same ranking.

---

## 8. Future Work

Ideas for how you would improve the model next.

Additional features or preferences
Add artist affinity, era, and popularity, and let users adjust the feature weights themselves.

Better ways to explain recommendations
Show how much each feature contributed to the score, not just which ones matched.

Improving diversity among the top results
Penalize near-duplicate songs so the top list covers more genres and artists.

Handling more complex user tastes
Support multiple favorite genres and fuzzy matching so related genres share credit.

---

## 9. Personal Reflection

A few sentences about your experience.

What you learned about recommender systems
I learned that small scoring choices, especially the feature weights, have a large effect on what gets recommended.

Something unexpected or interesting you discovered
I was surprised that giving the system more information can actually make its scores less confident.

How this changed the way you think about music recommendation apps
It made me realize how much a recommender's behavior reflects its dataset and hidden weighting choices rather than pure taste.
