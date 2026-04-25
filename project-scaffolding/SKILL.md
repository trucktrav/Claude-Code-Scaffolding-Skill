---
name: project-scaffolding
description: >
  Opinionated project scaffolding for Python, Go, and web stacks. Creates fully configured
  projects with 14 types: FastAPI, Flask, Python CLI (Typer), Python library, data analysis
  (Polars + Jupyter), Go Gin API, Go Chi API, Go CLI (Cobra), Go module, React + Vite,
  Astro, Hono, T3 Stack, and static HTML/CSS. Python uses uv + Ruff + Pyright with src/
  layout. Go uses standard cmd/internal/pkg layout with Makefile. Every project gets git init,
  first commit, CLAUDE.md referencing zero-check, and MIT license. Use when: creating a new
  project, initializing a codebase, scaffolding boilerplate, starting a new app or library.
---

# Project Scaffolding Wizard

Opinionated project scaffolding for Python, Go, and web stacks.

## Wizard Workflow

When a user requests a new project, follow this interactive workflow:

### Step 1: Project Type Selection

Present the project type menu:

| Category | Types |
|----------|-------|
| **Static** | HTML/CSS + Tailwind CDN |
| **Python** | FastAPI, Flask, CLI (Typer), Library (PyPI), Data Analysis (Polars + Jupyter) |
| **Go** | Gin API, Chi API, CLI (Cobra), Module (library) |
| **Web** | React + Vite, Astro, Hono, T3 Stack |

### Step 2: Basic Configuration

Gather for ALL projects:
- **Project name** (required)
- **Location/directory**
- **Description**
- **Author name**
- **License** (default: MIT)

### Step 3: Type-Specific Options

#### Python projects
- **Database** — none, SQLite, PostgreSQL, MySQL (adds SQLAlchemy + Alembic for FastAPI/Flask)
- **Docker** — include compose.yml (FastAPI only)

#### Go projects
- No additional options needed — standard layout is applied.

#### Web projects
- CLI tools handle configuration interactively (Vite, Astro, Hono, create-t3-app).

### Step 4: Generate Project

Use `scripts/scaffold.py` for Python, Go, and HTML projects.
Use native CLI tools for web projects (React/Astro/Hono/T3), with scaffold.py as fallback.

```bash
# Direct usage
python scripts/scaffold.py my-project --type fastapi --description "My API" --author "Travis"
python scripts/scaffold.py my-tool --type go-cli --description "CLI tool"
python scripts/scaffold.py my-analysis --type python-data --description "Sales analysis"
```

## Opinionated Defaults

These are non-negotiable unless the user explicitly overrides:

| Setting | Default | Rationale |
|---------|---------|-----------|
| Python version | 3.13 | Current stable, not bleeding edge 3.14 |
| Python tooling | uv + Ruff + Pyright | Astral ecosystem + Microsoft type checker |
| Python layout | `src/` via hatchling | Clean imports, catches packaging bugs early |
| Python dataframes | Polars (not pandas) | Lazy execution, memory efficient, modern API |
| Ruff rules | E4,E7,E9,F,B,I,UP,N,S,SIM,RET,PTH | Security rules included (S), pathlib enforced (PTH) |
| Go version | 1.24 | Current stable |
| Go layout | cmd/internal/pkg + Makefile | Standard Go project layout |
| Go router | Gin or Chi (user picks) | Both well-maintained, user preference |
| Go CLI | Cobra | De facto standard |
| Web language | TypeScript | Always, no JS option |
| CSS framework | Tailwind | Default for React, Astro |
| Package manager | pnpm | For web projects |
| Type checker | Pyright (not mypy, not ty) | Best IDE integration, mature |
| Every project | git init + first commit | No reason not to |
| Every project | CLAUDE.md | References zero-check gauntlet |
| Every project | MIT license | Default, overridable |

## CLI Integration

Web projects prefer native CLI tools:

| Framework | CLI Command |
|-----------|-------------|
| React (Vite) | `npm create vite@latest -- --template react-ts` |
| Astro | `npm create astro@latest` |
| Hono | `npm create hono@latest` |
| T3 Stack | `npx create-t3-app@latest` |

If a CLI tool is unavailable, scaffold.py writes a README with the manual command.

## Example Conversations

### Python data analysis
```
User: Create a data analysis project for recipe analytics

Claude: I'll scaffold a Polars + Jupyter data analysis project:
- src/ layout with polars, plotly, pyarrow
- notebooks/ directory for Jupyter work
- data/raw/ and data/processed/ for data pipeline
- uv for dependency management, Ruff + Pyright for quality
- CLAUDE.md referencing zero-check

Name: recipe-analytics
Type: python-data
```

### Go API
```
User: New Go API with Chi

Claude: I'll create a Go Chi API project:
- Standard cmd/internal/pkg layout
- Chi router with middleware (Logger, Recoverer)
- Health check endpoint
- Makefile with build/test/lint/run targets
- golangci-lint for linting

Name: my-api
Type: go-chi
```

### FastAPI with database
```
User: FastAPI project with PostgreSQL

Claude: I'll scaffold a FastAPI project with PostgreSQL:
- src/ layout with uv + hatchling
- SQLAlchemy 2.0 + Alembic for migrations
- asyncpg driver
- Pydantic settings for config
- Health check endpoint with test

Name: my-api
Type: fastapi, Database: postgresql
```

## Available Resources

| Resource | When to Load | Purpose |
|----------|--------------|---------|
| `references/wizard-options.md` | Step 3 (gathering preferences) | Detailed config choices per type |
| `references/frameworks.md` | When generating code | Project structures and code patterns |
| `references/best-practices.md` | Architecture decisions | Directory organization, naming, patterns |
| `scripts/scaffold.py` | For project generation | Python engine for all 14 types |
