Title: Your First Bot

Source: https://docs.battlecode.cam/getting-started/first-bot

---

## Get started with `cambc starter`

If you haven’t already, run `cambc starter` to scaffold your project. When prompted, choose to create the starter bot — it gives you a working bot to build on.
## Bot structure

Every bot is a Python file containing a `Player` class with a `run` method. The engine creates one `Player` instance per unit and calls `run(controller)` once per round. main.py

## Key concepts

One Player instance per unit

One Player instance per unit

The Controller object

The Controller object

Imports from cambc

Imports from cambc `from cambc import *` gives you all game types: `Team`, `EntityType`, `Direction`, `Position`, `ResourceType`, `Environment`, `GameConstants`, `GameError`, and `Controller`. Time limit

Time limit

Each unit gets **2ms of CPU time** per round, plus a 5% buffer that refills when you use less. Locally there are no time limits — use remote test runs to check performance on the actual hardware. No external packages

No external packages

Only Python standard library modules are available. External packages like `numpy` or `scipy` cannot be imported — bots run in a sandboxed environment with no `pip install`.

## Next steps

## Run a local match

Test your bot against itself or an example opponent.

## Game rules

Understand the full game mechanics before optimising.

## API reference

Every method available via the Controller object.

## Types and enums

All game types: Team, EntityType, Direction, Position, and more.
