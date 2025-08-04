Below is the **single, canonical “Close-to-Shore Bible”** for *Broken Divinity – Python / ASCII edition*.
It merges everything discussed so far, re-orders the sections for a smoother read, and folds in:

* your **preferred file header** (Section 11)
* the **version-number flow + GitHub rule** (Section 15)

---

# Broken Divinity — Close-to-Shore Bible

*Short hops, loud logs, data-driven JSON, always-green pytest*

---

## 0) Core Principles (“Stay Close to Shore”)

|                       | Rule                                                               | Rationale                      |
| --------------------- | ------------------------------------------------------------------ | ------------------------------ |
| **Short hops**        | Each hop is a tiny, runnable vertical slice.                       | Always know where land is.     |
| **Always green**      | End every hop with green tests **and** a bootable ASCII game.      | No lingering debt.             |
| **Data-driven first** | Content lives in JSON/YAML; systems **discover** via folder scans. | Easy modding, no brittle glue. |
| **Avoid hard-coding** | Prefer tables & registries over `if/elif` ladders.                 | Fewer bugs, easier refactor.   |
| **Auto-populated UI** | Containers read data and spawn controls automatically.             | No hand-placed buttons.        |
| **Traceable logs**    | Verbose, tagged logs; never silently fail.                         | Debug in seconds, not hours.   |

**Definition of Done (per hop)**

1. `pytest` green (unit + integration + smoke)
2. `Game.run()` boots without error
3. Logs clean (no warnings/errors unless expected)
4. New data discovered, not hard-wired
5. Commit + tag (see §15)
6. `TODO(tag):` notes for deferred work

---

## 1) Project Layout

```
broken_divinity/
│
├─ src/                     # importable package
│   ├─ engine/              # loop, renderer, input, event bus
│   ├─ systems/             # registries + managers
│   ├─ components/          # lightweight ECS bits
│   └─ ui/                  # ASCII panels
│
├─ data/                    # JSON / YAML assets
│   ├─ abilities/
│   ├─ buffs/
│   ├─ statuses/
│   └─ entities/
│
├─ tests/                   # permanent pytest suites
│   ├─ unit/
│   ├─ integration/
│   └─ smoke/
│
└─ scratch_tests/           # temporary debug tests (git-ignored)
```

---

## 2) Dependencies

| Purpose         | Library                                |
| --------------- | -------------------------------------- |
| ASCII rendering | **rich** (fallback to `curses`)        |
| Input           | `blessed` or `readchar`                |
| Data parsing    | `json` + `pyyaml`                      |
| Tests           | `pytest`, `pytest-subtests`            |
| Logging         | `logging` + `rich.logging.RichHandler` |
| CLI helpers     | `typer` (optional)                     |

---

## 3) Logging & Observability

```python
# src/engine/logging_setup.py
import logging
from rich.logging import RichHandler

def configure(verbose: bool = True) -> None:
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format="%(message)s",
        datefmt="[%X]",
        handlers=[RichHandler(markup=True)]
    )
```

* **Tag prefix** = logger name (`log = logging.getLogger("TurnMgr")`).
* `log.debug|info|warning|error(…)` as severity ladder.
* Never silently fail.

---

## 4) Data-Driven Conventions

* **Assets:** JSON/YAML; keys match `name`.
* **Registries:** scan `data/**` once, cache by `name`.
* **Tables over branches:** map types → effects in dicts, not control flow.

---

## 5) Architecture (Engine Loop Snapshot)

```python
class Game:
    def __init__(self):
        configure(verbose=True)
        self.renderer   = ASCIIRenderer()
        self.turn_mgr   = TurnManager(event_bus=EventBus.global_bus())

    def run(self) -> None:
        while not self.turn_mgr.game_over:
            self.turn_mgr.process_turn()
            self.renderer.render(self.turn_mgr)
            cmd = self.renderer.get_input()
            self.turn_mgr.handle_input(cmd)
```

* Managers live in `src/systems`.
* Global events via `EventBus`.
* IDs via `id(entity)` if needed.

---

## 6) UI Principles (ASCII Panels)

| Panel             | Public API               | Data Source                     |
| ----------------- | ------------------------ | ------------------------------- |
| **InitiativeBar** | `populate(units)`        | `TurnManager.order`             |
| **ActionBar**     | `show(actor)`            | `actor.ability_container.all()` |
| **EntityPanel**   | `bind(entity)`           | Signals: `hp_changed`, `died`   |
| **CombatLog**     | Subscribes to `EventBus` | Emits formatted lines           |

Zero hard-wired paths; icons loaded via registry meta.

---

## 7) Game Rules (Initial)

* **Damage types:** `Physical`, `Infernal`, `Holy` (mod table).
* **Rounds vs Turns:** buffs expire at **round end**.
* **Stacks:** magnitude + duration stack (exceptions noted in resource).

---

## 8) Testing Strategy (pytest)

### Permanent suites (`tests/`)

* **Unit**, **Integration**, **Smoke** folders.
* Leak hygiene: rely on fixtures; call `gc.collect()` in suspect cases.

### Scratch tests (`scratch_tests/`)

* Files start `dbg_*.py`, print-heavy, poke privates if needed.
* Git-ignored. Run with `pytest scratch_tests -q`.

### CLI snippets

```bash
# all permanent
python -m pytest -q tests
# only smoke
python -m pytest -q tests/smoke
# scratch only
python -m pytest -q scratch_tests
```

---

## 9) CLI & Tasks

**Makefile**

```make
test-all:      ; python -m pytest -q tests
test-smoke:    ; python -m pytest -q tests/smoke
test-scratch:  ; python -m pytest -q scratch_tests
run:           ; python -m broken_divinity.cli run
```

VS Code `tasks.json` mirrors these.

---

## 10) Code-Style Quick List

* **Black** + **PEP 8**.
* Guard clauses; ≤ 40 lines/function.
* Explicit `dataclass`es for data carriers.
* Severity: `assert` → `log.warning` → `log.error`.
* End every file with `#EOF`.

---

## 11) Preferred File Header

```python
"""
╔══════════════════════════════════════════════════════════════════════════════╗
║  Ability Registry                                                            ║
╟──────────────────────────────────────────────────────────────────────────────╢
║  Author        : Eric Acosta ┃ https://github.com/EricA1019                 ║
║  Purpose       : Discovers JSON ability definitions and serves them by name ║
║  Last-Updated  : 2025-08-03                                                 ║
║  Version       : v0.11.19                                                   ║
╚══════════════════════════════════════════════════════════════════════════════╝
"""
# imports…
#EOF
```

* 80-char box, symmetrical.
* Lives *inside* the top docstring.
* Update **Last-Updated** and **Version** each hop.

---

## 12) ASCII Artistry

* Icons in `icons/*.txt` (multi-line).
* Render via Rich panels; strip ANSI on fallback.
* Example `imp.txt`:

```
/\_/\
(ಠ_ಠ)
/ >🔥
```

---

## 13) Prompting LLMs

```
I'm building a terminal ASCII roguelike in Python 3.11.

Constraints:
- Data-driven JSON in data/*
- Registries discover content recursively
- Rich renderer, curses fallback
- Pytest tests first (test_*.py), no private pokes
- Provide a bootstrap script that writes files, skipping existing
- Verbose logging via logging.getLogger("[Tag]")
```

Checklist: deterministic tests, recursive scans, tagged logs, etc.

---

## 14) Glossary

| Term             | Meaning                                        |
| ---------------- | ---------------------------------------------- |
| **Hop**          | One merge-ready vertical slice (`PATCH` bump). |
| **Phase**        | A cohesive feature block (`MINOR` bump).       |
| **Epoch**        | Breaking redesign (`MAJOR` bump).              |
| **Panel**        | Rectangular ASCII region.                      |
| **Scratch test** | Disposable debug file in `scratch_tests/`.     |

---

## 15) Version-Number Flow & GitHub Policy

| SemVer field | Represents      | Starts at       | Example    | Remote push?                              |
| ------------ | --------------- | --------------- | ---------- | ----------------------------------------- |
| **MAJOR**    | Epoch / rewrite | `0` → `1` later | `v1.00.00` | Yes                                       |
| **MINOR**    | **Phase**       | `0`             | `v0.11.00` | **Must** push at every phase close        |
| **PATCH**    | **Hop**         | `1`             | `v0.11.19` | Push optional (push if others/CI need it) |

> Hop 19 inside Phase 11 ⇒ **`v0.11.19`**

### Tag Recipes

```bash
# ----- Hop (PATCH) -----
git commit -m "feat(ui): initiative bar renders"
git tag -a v0.11.19 -m "Hop 19: initiative bar"
git push --tags origin main        # optional

# ----- Phase close (MINOR) -----
git commit -m "chore(phase): close phase 12 – action bar complete"
git tag -a v0.12.00 -m "Phase 12 complete: action bar"
git push --tags origin main        # **mandatory**
```

**Pre-tag checklist**

1. `pytest` green.
2. `Game.run --quick` boots.
3. Update headers’ `Last-Updated` + `Version`.
4. Append CHANGELOG entry.
5. If **phase tag**, push `main` & tags to GitHub immediately.

---

*Living document — refine as habits evolve. Keep hops short, logs loud, tests green, scenes bootable.*
