# project-scaffolding skill for Claude Code

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Python](https://img.shields.io/badge/python-3.10%2B-3776ab.svg)](project-scaffolding/scripts/scaffold.py)
[![Claude Code](https://img.shields.io/badge/Claude%20Code-skill-blueviolet.svg)](project-scaffolding/SKILL.md)

Opinionated project scaffolding for Python, Go, web, and Ansible stacks
— Claude Code skill plus a standalone CLI engine. **17 project types**
with strong defaults; no kitchen-sink, no menu of every framework on
earth.

This skill replaced an earlier 70+ type scaffolder. The narrower set is
deliberate: every type ships with a curated toolchain (uv + Ruff +
Pyright for Python; `cmd/internal/pkg` + Makefile for Go; pnpm + Vite
for web) that's known to work end-to-end with `zero-check`.

## Supported project types

| Category | Types | Stack |
|----------|-------|-------|
| **Static** | HTML/CSS + Tailwind CDN | one-file or multi-page, no build step |
| **Python** | FastAPI, Flask, Python CLI, Python lib, Python data analysis | uv + Ruff + Pyright, `src/` layout via hatchling; Polars for data |
| **Go** | Gin API, Chi API, CLI (Cobra), Module (library) | Go 1.24, `cmd/internal/pkg` + Makefile, golangci-lint |
| **Ansible** | Project, role, docker-container role | ansible-lint preconfigured |
| **Web** | React + Vite, Astro, Hono, T3 Stack | TypeScript always, Tailwind default; delegates to native CLIs (`npm create vite`, `create-t3-app`, etc.) |

The full list lives in the `creators` dict at
`project-scaffolding/scripts/scaffold.py`. If a docs table disagrees
with that dict, the dict wins.

## Install

The skill ships as a packaged zip: `project-scaffolding.skill`.

**From the packaged `.skill`** (recommended):

```bash
unzip project-scaffolding.skill -d ~/.claude/skills/project-scaffolding
```

**From the source tree** (development):

```bash
ln -s "$(pwd)/project-scaffolding" ~/.claude/skills/project-scaffolding
```

Once installed, Claude Code triggers the skill on prompts like:

- "Create a new project"
- "Scaffold a FastAPI backend"
- "Start a Go CLI"
- "Initialize a Python library"

Or invoke the wizard directly via `/project-scaffolding`.

## CLI usage

The same scaffolder runs as a standalone CLI:

```bash
python project-scaffolding/scripts/scaffold.py my-api \
    --type fastapi \
    --description "My API" \
    --author "Travis"

python project-scaffolding/scripts/scaffold.py my-tool \
    --type go-cli \
    --description "CLI tool"

python project-scaffolding/scripts/scaffold.py my-role \
    --type ansible-role \
    --description "Custom geerlingguy-style role"
```

`--type` must match a key in the `creators` dict.

## Opinionated defaults

| Setting | Default | Rationale |
|---------|---------|-----------|
| Python version | 3.13 | Current stable |
| Python tooling | uv + Ruff + Pyright | Astral ecosystem + MS type checker |
| Python layout | `src/` via hatchling | Catches packaging bugs early |
| Python dataframes | Polars (not pandas) | Lazy execution, memory efficient |
| Ruff rules | `E4,E7,E9,F,B,I,UP,N,S,SIM,RET,PTH` | Security (S) + pathlib (PTH) included |
| Go version | 1.24 | Current stable |
| Go layout | `cmd/internal/pkg` + Makefile | Standard Go project layout |
| Web language | TypeScript | Always, no JS option |
| CSS framework | Tailwind | Default for web projects |
| Package manager | pnpm (web), uv (Python) | Modern, fast |
| Type checker | Pyright | Best IDE integration |
| Every project | `git init` + first commit | Always |
| Every project | CLAUDE.md referencing zero-check | Always |
| Every project | MIT license | Default, overridable |

## What gets generated

The scaffolder generates a full project tree, not just a skeleton. Each
type includes:

- Source layout (`src/`, `cmd/`, etc.)
- Dependency manifest (`pyproject.toml`, `go.mod`, `package.json`)
- Linting + type-check config (`ruff.toml` inline in pyproject, `golangci.yml`)
- Test scaffold (`tests/` for Python, Go's built-in testing)
- `Dockerfile` + `compose.yml` for FastAPI (when `--docker` is selected)
- `Makefile` (Go projects)
- `CLAUDE.md` referencing the [zero-check](../zero-check-pipeline) gauntlet
- `README.md` stub
- `.gitignore` matched to the toolchain
- `git init` + initial commit

## Wizard flow

When triggered via Claude Code, the skill walks the user through a four-step wizard:

1. **Project type** — pick from the table above
2. **Basic config** — name, location, description, author, license
3. **Type-specific options** — e.g. Python projects can request a DB (SQLite / PostgreSQL / MySQL, adds SQLAlchemy + Alembic on FastAPI/Flask); FastAPI can request Docker
4. **Generate** — runs `scaffold.py` for Python / Go / HTML / Ansible; delegates to native CLIs for web

See `project-scaffolding/SKILL.md` for the canonical wizard contract.

## Repo layout

```
Claude-Code-Scaffolding-Skill/
  project-scaffolding/
    SKILL.md                       # Wizard workflow + trigger description
    scripts/
      scaffold.py                  # Core engine (~750 lines, 17 creators)
    references/
      frameworks.md                # Per-type structure + code patterns
      wizard-options.md            # Detailed config options
      best-practices.md            # Directory layout, naming, testing, Docker
  project-scaffolding.skill        # Packaged zip (regenerate after edits)
  CLAUDE.md                        # Agent notes
  README.md                        # This file
```

## Repackaging

After any edit under `project-scaffolding/`, rebuild the `.skill` zip:

```bash
cd project-scaffolding && zip -r ../project-scaffolding.skill SKILL.md scripts/ references/
```

Always repackage before committing — the `.skill` is what users install.

## License

MIT.
