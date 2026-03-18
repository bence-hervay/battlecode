Title: Road, Barrier & Marker

Source: https://docs.battlecode.cam/spec/other-buildings

---

## Road

Walkable tiles for builder bots to move on. The cheapest building.| Property | Value |
|---|---|
| HP | 10 |
| Base cost | 1 Ti |
| Scaling | 0.5% |

## Barrier

Cheap, takes up space, and has high HP. Useful for blocking enemy paths or protecting key buildings.| Property | Value |
|---|---|
| HP | 30 |
| Base cost | 3 Ti |
| Scaling | 1% |

## Marker

A tile containing a single **unsigned 32-bit integer** that can be read by any allied unit. Building a marker is completely free and does **not** cost action cooldown — you may place at most one marker per round. Any team may build over markers, destroying them.

| Property | Value |
|---|---|
| HP | 1 |
| Cost | Free |

Markers are the **only form of communication** between allied units. Global variables are not shared between `Player` instances — each unit has its own isolated Python environment.

### Communication patterns

Since each unit’s `Player` instance is isolated, markers are essential for coordination: **Scouting reports **: Write enemy positions to markers near your core** Build orders **: Use marker values as state machine flags** Territory claims**: Mark tiles to avoid duplicate work
