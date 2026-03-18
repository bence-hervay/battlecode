Title: Running Matches

Source: https://docs.battlecode.cam/getting-started/running-matches

---

Run local matches with the CLI and view replays in the visualiser.

##  Run a local match

```
cambc run <bot_a> <bot_b> [map]
```

This runs the full game engine locally with **no time limits** — ideal for rapid iteration. The engine outputs a `replay.replay26` file.
Bot paths can be a directory containing `main.py`, a `.py` file, or a bot name from your `bots_dir` (set in `cambc.toml`). The optional map argument is a `.map26` file — if omitted, the first map in your `maps_dir` is used.

```
cambc run starter starter                        # bot vs itself
cambc run my_bot opponent --seed 42              # deterministic seed
cambc run my_bot opponent maps/custom.map26      # custom map
cambc run my_bot opponent --replay out.replay26  # custom replay path
```

##  View a replay

```
cambc watch replay.replay26
```

Opens the visualiser in your browser. Supports play/pause, round scrubbing, speed control, and keyboard navigation.

###  Run + watch in one command

```
cambc run --watch starter starter
```

###  View a platform match

```
cambc watch --match <match_id>
cambc watch --match <match_id> --game 3
```

##  Remote test runs

Remote commands require authentication — run `cambc login` first if you haven’t already.
Test your bots on the **same hardware** that runs ladder matches, with full time limit enforcement:

```
cambc test-run <bot_a> <bot_b> [map]
```

This uploads both bots and runs a match on AWS Graviton3 instances with the 2ms CPU time limit enforced. Use this to catch performance issues before submitting.
Bot paths for `test-run` must be a directory containing `main.py` or a `.zip` file (unlike `cambc run`, arbitrary `.py` files are not accepted).

```
cambc test-run my_bot opponent
cambc test-run my_bot opponent maps/custom.map26
```

Remote test runs are rate-limited: max 10 test/unrated matches per 5 minutes. Unrated matches also have a 5-minute cooldown per specific matchup.

You can also challenge another team to an unrated match using both teams’ latest submissions:

```
cambc unrated <opponent_team_id>
```

##  Debugging

- **stdout** via `print("msg")` is captured and saved to the replay — view it per-unit in the visualiser
- **stderr** prints to your console in real time
- Use `c.draw_indicator_line()` and `c.draw_indicator_dot()` to draw debug overlays on the map

##  Next steps

## Submit your bot

Upload your bot to compete on the ladder.

## CLI reference

Full reference for all CLI commands.

[Previous](/getting-started/first-bot)

⌘I
