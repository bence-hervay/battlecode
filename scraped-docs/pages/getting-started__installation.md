Title: Installation

Source: https://docs.battlecode.cam/getting-started/installation

---

Install the Cambridge Battlecode CLI and run your first local match.

##  Requirements

- **Python 3.12 or 3.13** (3.14 is not supported)
- **pip** (comes with Python)

##  Install

```
pip install cambc
```

This gives you both the CLI tool and the compiled Rust game engine as a native Python module. No Docker, Rust toolchain, or Node.js required.

The `cambc` package includes the full game engine compiled for your platform. Supported: macOS (Apple Silicon + Intel), Linux (x86\_64 + ARM64), Windows (x86\_64).

##  Verify

```
cambc --version
```

##  Set up your project

```
cambc starter
```

This scaffolds a project with a `cambc.toml` config, `bots/` and `maps/` directories, a `.gitignore`, and optionally a starter bot. See the [CLI reference](/getting-started/cli#cambc-starter) for details.

##  What’s included

| Component | Description |
| --- | --- |
| `cambc` CLI | Run local matches, open the visualiser, submit bots, trigger test runs |
| `cambc` Python module | Game types (`Team`, `EntityType`, `Direction`, `Position`, etc.) for use in your bot code |
| `titan_runner` | The compiled Rust game engine (embedded, runs locally with no time limits) |

##  Next steps

## Write your first bot

Create a simple bot that spawns builders and starts harvesting.

## CLI reference

Full reference for all CLI commands.

[Previous](/)

⌘I
