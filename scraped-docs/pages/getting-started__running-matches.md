Title: Running Matches

Source: https://docs.battlecode.cam/getting-started/running-matches

---

## Run a local match

**no time limits**— ideal for rapid iteration. The engine outputs a `replay.replay26` file. Bot paths can be a directory containing `main.py`, a `.py` file, or a bot name from your `bots_dir` (set in `cambc.toml`). The optional map argument is a `.map26` file — if omitted, the first map in your `maps_dir` is used.
## View a replay

## Run + watch in one command

## View a platform match

## Remote test runs

Remote commands require authentication — run `cambc login` first if you haven’t already. Test your bots on the **same hardware** that runs ladder matches, with full time limit enforcement: `test-run` must be a directory containing `main.py` or a `.zip` file (unlike `cambc run`, arbitrary `.py` files are not accepted).
## Debugging

**stdout** via `print("msg")` is captured and saved to the replay — view it per-unit in the visualiser **stderr** prints to your console in real time- Use `c.draw_indicator_line()` and `c.draw_indicator_dot()` to draw debug overlays on the map

## Next steps

## Submit your bot

Upload your bot to compete on the ladder.

## CLI reference

Full reference for all CLI commands.
