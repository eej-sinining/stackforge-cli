# StackForge

A CLI scaffolder for .NET Clean Architecture (CQRS) projects.

## Installation

```bash
pip install stackforge-cli
```

## Usage

```bash
stackforge
```

Then follow the prompts to scaffold a new project.

## Version and updates

Check the version you have installed:

```bash
stackforge --version
```

Update to the latest release:

```bash
pip install --upgrade stackforge-cli
```

When you run `stackforge`, it checks PyPI for a newer version and prints an upgrade notice if one is available (network required; fails silently if offline).

## What it generates

- .NET 10 Clean Architecture structure (API, Application, Domain, Infrastructure, Persistence)
- JWT authentication with ASP.NET Identity
- Swagger UI with Bearer token support
- PostgreSQL with EF Core
- Docker + docker-compose with healthchecks
- Role and user seeders (SuperAdmin out of the box)
- Git initialization on `main` with `staging` and `development` branches
- GitHub Actions workflow to create `staging` and `development` on first push to `main`

## Quickstart after scaffolding

1. Open the project in VS Code or Visual Studio
2. Run: `docker-compose up --build`
3. Visit: `http://localhost:5000/swagger`

## Git workflow

Each scaffolded project is initialized with three local branches:

| Branch        | Purpose                          |
|---------------|----------------------------------|
| `main`        | Production / default branch      |
| `staging`     | Pre-production environment       |
| `development` | Active development environment   |

A GitHub Actions workflow (`.github/workflows/sync-branches.yml`) is also included as a fallback: if you only push `main` first, it creates remote `staging` and `development` on GitHub automatically.

### Example: push to GitHub

From your scaffolded project directory (e.g. `~/stackforge/MyApi`):

```bash
# 1. Create a new repo on GitHub (empty, no README), then add the remote
git remote add origin https://github.com/<your-user>/MyApi.git

# 2. Push all branches in one go
git push -u origin --all
```

That publishes `main`, `staging`, and `development` in a single command and sets upstream tracking for each.

### Day-to-day branching

```bash
# Work on a feature
git checkout development
git checkout -b feature/my-feature
# ... commit changes ...
git push -u origin feature/my-feature

# Merge into development when ready (via PR or locally)
git checkout development
git merge feature/my-feature
git push origin development
```

Promote changes up the chain (`development` → `staging` → `main`) using pull requests or merges as your team prefers.