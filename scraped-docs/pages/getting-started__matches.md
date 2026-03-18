Title: How Matches Work

Source: https://docs.battlecode.cam/getting-started/matches

---

## Match format

Every match consists of **5 games**. Each game is played on a different map with a different random seed. The team that wins more games wins the match.

## Win conditions per game

A game ends when:| Condition | Description |
|---|---|
Core destroyed | One team’s core reaches 0 HP |
Resources | After 2000 rounds, the tiebreaker sequence determines the winner |
Timeout | After 2000 rounds with equal tiebreakers — decided by coinflip |

## Ladder

The ladder ranks all teams by **Glicko-2** rating. New teams start unrated and are seeded to 1500 when they upload their first ready submission.

## Scheduling

Every **10 minutes**, the scheduler:

- Pairs each team with one similarly-rated opponent (greedy nearest-rating matching with small random jitter to avoid repetitive matchups)
- Avoids rematches from the last hour
- Submits matches to the runner infrastructure 
## Rating updates

Ratings are updated using **Glicko-2** after each scheduler cycle. Match outcomes use fractional scoring based on the game score (e.g., a 5-0 win counts more than a 3-2 win). Each team has three rating components: **Rating **— skill estimate (starts at 1500)** Uncertainty (RD) **— confidence in the rating (starts high, decreases with more matches)** Volatility**— expected rating fluctuation
