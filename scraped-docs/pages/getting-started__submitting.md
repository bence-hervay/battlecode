Title: Submitting

Source: https://docs.battlecode.cam/getting-started/submitting

---

## Log in

Before submitting, authenticate the CLI with your platform account: `cambc logout`.
## Via CLI

## Via the platform

- Go to game.battlecode.cam
- Navigate to **Submissions** in the sidebar - Upload your bot zip 
## Bot requirements

Your submission must contain a `main.py` file with a `Player` class. The file can be at the root of the zip or inside a single top-level directory.
| Constraint | Limit |
|---|---|
| Zip size | 5 MB max |
| Decompressed size | 50 MB max |
| File count | 500 files max |
| Native extensions | Not allowed (`.so `, `.pyd `, `.dylib `, `.dll`) |
| Imports | Must be top-level (file I/O is blocked during `run()`) |

## What happens after upload

- Your zip is validated (structure, size, no native extensions)
- Status is set to **ready** - Your latest ready submission becomes your active bot on the ladder
- The scheduler pairs you against other teams every 10 minutes 
## Ladder

The ladder ranks all teams by Glicko-2 rating. Every 10 minutes, the scheduler creates one match per team, pairing you with a similarly-rated opponent. Each match consists of **5 games**— the team that wins more games wins the match. Ratings update after each scheduler cycle. See How matches work for details.
