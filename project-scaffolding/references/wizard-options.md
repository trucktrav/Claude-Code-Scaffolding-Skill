# Wizard Configuration Options

Detailed configuration options for each of the 14 supported project types.

---

## Language & SDK Options

### Python
| Option | Choices | Default |
|--------|---------|---------|
| Version | 3.12, 3.13 | 3.13 |
| Package manager | uv (only) | uv |
| Linter/formatter | Ruff (only) | Ruff |
| Type checker | Pyright (only) | Pyright |
| Build system | hatchling | hatchling |
| Layout | src/ | src/ |

### Go
| Option | Choices | Default |
|--------|---------|---------|
| Version | 1.23, 1.24 | 1.24 |
| Layout | cmd/internal/pkg | standard |
| Linter | golangci-lint | golangci-lint |
| Build tool | Makefile | Makefile |

### TypeScript/Web
| Option | Choices | Default |
|--------|---------|---------|
| Language | TypeScript (only) | TypeScript |
| Strict mode | Yes (only) | Yes |
| Package Manager | pnpm | pnpm |
| CSS | Tailwind | Tailwind |

---

## HTML/CSS Projects

**Type: `html`**

Minimal configuration — always creates Tailwind CDN site.

| Option | Choices | Default |
|--------|---------|---------|
| CSS approach | Tailwind CDN | Tailwind CDN |
| Pages | Single, Multi-page | Single |

---

## Python: FastAPI

**Type: `fastapi`**

| Option | Choices | Default |
|--------|---------|---------|
| Database | None, SQLite, PostgreSQL, MySQL | None |
| ORM | SQLAlchemy 2.0 (auto when DB selected) | SQLAlchemy |
| Migrations | Alembic (auto when DB selected) | Alembic |
| Docker | Yes, No | No |
| Structure | src/ with core/api/models/schemas | Always |

When database is selected:
- PostgreSQL → asyncpg driver
- MySQL → aiomysql driver
- SQLite → aiosqlite driver

---

## Python: Flask

**Type: `flask`**

| Option | Choices | Default |
|--------|---------|---------|
| Database | None, SQLite, PostgreSQL, MySQL | None |
| ORM | Flask-SQLAlchemy + Flask-Migrate (auto) | Flask-SQLAlchemy |
| Structure | src/ with api/models/services | Always |

---

## Python: CLI

**Type: `python-cli`**

| Option | Choices | Default |
|--------|---------|---------|
| Framework | Typer (only) | Typer |
| Output | Rich (always included) | Rich |
| Structure | src/ with commands/ | Always |
| Entry point | `[project.scripts]` in pyproject.toml | Always |

---

## Python: Library

**Type: `python-lib`**

| Option | Choices | Default |
|--------|---------|---------|
| Structure | src/ layout | Always |
| Build | hatchling | hatchling |
| Publishing | PyPI-ready pyproject.toml | Always |

Minimal — just `__init__.py`, `main.py`, and a test. Add dependencies as needed.

---

## Python: Data Analysis

**Type: `python-data`**

| Option | Choices | Default |
|--------|---------|---------|
| DataFrame library | Polars (only) | Polars |
| Visualization | Plotly | Plotly |
| Notebooks | Jupyter (separate dep group) | Yes |
| Data format | Parquet (pyarrow) | Parquet |
| Directory structure | data/raw/ + data/processed/ | Always |

Includes a `load.py` utility module with `load_raw()` and `save_processed()` helpers.
Notebooks are in a separate `[dependency-groups] notebook` section to keep the base install lean.

---

## Go: Gin API

**Type: `go-gin`**

| Option | Choices | Default |
|--------|---------|---------|
| Layout | cmd/internal/pkg | Standard |
| Router | Gin | Gin |
| Includes | Health endpoint, Makefile | Always |

---

## Go: Chi API

**Type: `go-chi`**

| Option | Choices | Default |
|--------|---------|---------|
| Layout | cmd/internal/pkg | Standard |
| Router | Chi v5 with middleware | Chi |
| Middleware | Logger, Recoverer | Always |
| Includes | Health endpoint, Makefile | Always |

---

## Go: CLI

**Type: `go-cli`**

| Option | Choices | Default |
|--------|---------|---------|
| Framework | Cobra | Cobra |
| Layout | cmd/ + internal/ | Standard |
| Includes | root + version subcommand, Makefile | Always |

---

## Go: Module

**Type: `go-module`**

| Option | Choices | Default |
|--------|---------|---------|
| Layout | Flat (single package) | Flat |
| Includes | Example function + test, Makefile | Always |

Minimal library structure. No cmd/ — just the package and tests.

---

## Web: React + Vite

**Type: `react`**

Delegated to `npm create vite@latest -- --template react-ts`.
Scaffold.py adds CLAUDE.md, LICENSE, and .gitignore on top of the Vite output.

---

## Web: Astro

**Type: `astro`**

Delegated to `npm create astro@latest` with the `basics` template.
Scaffold.py adds CLAUDE.md, LICENSE, and .gitignore on top.

---

## Web: Hono

**Type: `hono`**

Delegated to `npm create hono@latest`.
Scaffold.py adds CLAUDE.md, LICENSE, and .gitignore on top.

---

## Web: T3 Stack

**Type: `t3`**

Delegated to `npx create-t3-app@latest`.
Full-stack: Next.js + tRPC + Prisma + Tailwind + NextAuth.
Scaffold.py adds CLAUDE.md, LICENSE, and .gitignore on top.

---

## Code Quality (all Python projects)

Every Python project includes in pyproject.toml:

```toml
[tool.ruff]
line-length = 100

[tool.ruff.lint]
select = ["E4", "E7", "E9", "F", "B", "I", "UP", "N", "S", "SIM", "RET", "PTH"]

[tool.ruff.lint.per-file-ignores]
"tests/**" = ["S101", "INP001"]

[tool.pyright]
pythonVersion = "3.13"
typeCheckingMode = "standard"
```

Ruff rules rationale:
- `S` (security) — catches hardcoded passwords, SQL injection, eval() usage
- `PTH` — enforces pathlib over os.path (modern Python)
- `SIM` — simplifies conditionals and loops
- `RET` — catches implicit returns and unnecessary else after return
- `N` — PEP 8 naming conventions
- `B` — bugbear catches common bugs
- `I` — isort keeps imports clean
- `UP` — pyupgrade modernizes syntax

## Testing (all projects)

| Stack | Framework | Config |
|-------|-----------|--------|
| Python | pytest | `[tool.pytest.ini_options] testpaths = ["tests"]` |
| Go | go test | `make test` with race detector + coverage |
| Web | Vitest (via Vite) | Configured by CLI tool |
