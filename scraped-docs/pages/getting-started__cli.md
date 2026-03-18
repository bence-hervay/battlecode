Title: CLI reference

Source: https://docs.battlecode.cam/getting-started/cli

---

`cambc`

CLI is your main tool for local development, testing, and interacting with the platform. Install it with `pip install cambc`.
## Project setup

`cambc starter`

Scaffold a new Cambridge Battlecode project. Run this first after installing. `cambc.toml`

The config file created by `cambc starter`. All fields have defaults and all CLI options override config values. `cambc run` are resolved by first checking the raw path, then checking inside `bots_dir`. So `cambc run starter opponent` resolves to `bots/starter` and `bots/opponent`.
## Local development

`cambc run`

Run a local match between two bots. No time limits are enforced locally. **Arguments:**

| Argument | Description |
|---|---|
`bot_a ` | First bot — a directory containing ` main.py `, a `.py ` file, or a name in ` bots_dir` |
`bot_b ` | Second bot — same formats as ` bot_a` |
`map ` | Optional `.map26 ` map file. If omitted, uses the first map in ` maps_dir` |

**Options:**

| Option | Description |
|---|---|
`--replay PATH ` | Output replay file path (overrides ` cambc.toml` default) |
`--seed N ` | Map seed (overrides ` cambc.toml` default) |
`--watch` | Open the visualiser automatically after the match |

`cambc watch`

View a replay in the browser-based visualiser. **Local replay:** Serves the visualiser on `localhost` and opens your browser. Press `Ctrl+C` to stop the server. **Platform match:** Opens the platform visualiser in your browser for a specific match. `cambc map-editor`

Open the map editor to create custom `.map26` files.
## Platform commands

These commands interact with the online platform at game.battlecode.cam. Most require authentication via `cambc login`. `cambc login`

Authenticate with the platform. Opens a browser window for OAuth login and stores your session locally. `cambc logout`. `cambc logout`

Clear stored credentials. `cambc submit`

Upload a bot to compete on the ladder. `main.py`, a single `.py` file, or a `.zip`. Directories are auto-zipped before upload. See submission requirements for constraints. `cambc status`

Show your current team, rating, rank, and member list. `cambc unrated`

Challenge another team to an unrated match using both teams’ latest submissions.
| Option | Description |
|---|---|
`--match ID` | Use the opponent’s submission version from a specific past match instead of their latest |

`cambc test-run`

Upload two local bots and run a remote match with full time limit enforcement on AWS Graviton3 hardware. `cambc run`, this enforces the 2ms CPU time limit per round — use this to check your bot’s performance before submitting. `cambc matches`

View recent match history.
| Option | Description |
|---|---|
`--type {ladder|unrated}` | Filter by match type |
`--team NAME` | Filter by team name (substring match) |
`--limit N` | Number of matches to show (default 20, max 100) |
`--cursor CURSOR` | Pagination cursor from previous results |
