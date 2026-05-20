# CLAUDE.md

This file provides guidance to Claude Code when working with code in this repository.

## Project Overview

A **Claude Code skill** for opinionated project scaffolding across Python, Go, web, and Ansible stacks. Supports 17 project types with strong defaults and minimal configuration.

### Architecture

```
project-scaffolding/
├── SKILL.md                 # Skill definition — wizard workflow and trigger patterns
├── scripts/scaffold.py      # Core scaffolding engine (~750 lines)
├── references/
│   ├── frameworks.md        # Project structures and code patterns per type
│   ├── wizard-options.md    # Detailed config options per type
│   └── best-practices.md    # Directory layout, naming, testing, Docker patterns
```

**Key principles:**
- **SKILL.md** is the contract — defines what can be created and the interactive wizard flow
- **scaffold.py** is the implementation — generates project structures via a `creators` dict
- **references/** contains deep knowledge — framework configs, best practices, tooling rationale

## Supported Project Types

| Category | Types |
|----------|-------|
| Static | HTML/CSS + Tailwind CDN |
| Python | FastAPI, Flask, CLI (Typer), Library (PyPI), Data Analysis (Polars + Jupyter) |
| Go | Gin API, Chi API, CLI (Cobra), Module (library) |
| Ansible | `ansible` (project), `ansible-role`, `ansible-docker-container` |
| Web | React + Vite, Astro, Hono, T3 Stack |

The canonical source of truth for what's supported is the `creators` dict
in `project-scaffolding/scripts/scaffold.py`. If that dict and this table
disagree, the dict wins — update the docs.

## Opinionated Defaults

| Setting | Default | Rationale |
|---------|---------|-----------|
| Python version | 3.13 | Current stable |
| Python tooling | uv + Ruff + Pyright | Astral ecosystem + Microsoft type checker |
| Python layout | `src/` via hatchling | Clean imports, catches packaging bugs early |
| Python dataframes | Polars (not pandas) | Lazy execution, memory efficient |
| Ruff rules | E4,E7,E9,F,B,I,UP,N,S,SIM,RET,PTH | Security (S) + pathlib (PTH) included |
| Go version | 1.24 | Current stable |
| Go layout | cmd/internal/pkg + Makefile | Standard Go project layout |
| Web language | TypeScript | Always, no JS option |
| CSS framework | Tailwind | Default for web projects |
| Package manager | pnpm (web), uv (Python) | Modern, fast |
| Type checker | Pyright (not mypy, not ty) | Best IDE integration |
| Every project | git init + first commit | Always |
| Every project | CLAUDE.md | References zero-check gauntlet |
| Every project | MIT license | Default, overridable |

## Working with scaffold.py

### How It Works

scaffold.py uses a flat `creators` dict mapping type names to creator
methods on the scaffold class:

```python
creators = {
    "html": self._create_html,
    "fastapi": self._create_fastapi,
    "go-gin": self._create_go_api,           # go-gin and go-chi share _create_go_api
    "ansible": self._create_ansible,
    # ... 17 total
}
```

Each creator function takes `(project_dir, name, pkg, desc, author)` and builds the full project tree. Common helpers handle cross-cutting concerns:

- `_pyproject_toml()` — generates pyproject.toml with uv/hatchling/Ruff/Pyright config
- `_go_makefile()` — Makefile with build/test/lint/run/clean targets
- `_git_init()` — git init + first commit
- `_claude_md()` — CLAUDE.md referencing zero-check
- `_license_mit()` — MIT license with author name

### Adding a New Project Type

1. Write a `_create_[type]()` function following the existing pattern
2. Add it to the `creators` dict
3. Update SKILL.md with the new type in the wizard table
4. Update references/wizard-options.md with type-specific config
5. Update references/frameworks.md with the directory structure and key patterns

### CLI Usage

```bash
python scripts/scaffold.py my-project --type fastapi --description "My API" --author "Travis"
python scripts/scaffold.py my-tool --type go-cli --description "CLI tool"
python scripts/scaffold.py my-analysis --type python-data --description "Sales analysis"
```

## Dev Workflow

```bash
# Lint the scaffolding engine
uv run ruff check scripts/scaffold.py
uv run ruff format scripts/scaffold.py
uv run pyright scripts/scaffold.py

# Test by generating a project
python scripts/scaffold.py /tmp/test-project --type fastapi --description "test"

# Repackage the .skill file after changes
cd project-scaffolding && zip -r ../project-scaffolding.skill SKILL.md scripts/ references/
```

## Packaging

After any changes to files under `project-scaffolding/`, repackage the `.skill` file:

```bash
cd project-scaffolding && zip -r ../project-scaffolding.skill SKILL.md scripts/ references/
```

Always repackage before committing.

## Important Notes

- **SKILL.md is the source of truth** for what the skill can do — always update it when adding features
- **Keep scaffold.py and SKILL.md in sync** — options in SKILL.md must be implemented in scaffold.py
- **Ruff rules are intentional** — see references/best-practices.md for the rationale behind each rule selection
- **Web types delegate to native CLIs** — React/Astro/Hono/T3 use npm create / npx, scaffold.py is the fallback
- **Polars over pandas** — this is a deliberate choice for all new data projects
- **Pyright over mypy/ty** — ty is too new, mypy lacks IDE integration depth
