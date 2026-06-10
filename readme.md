# StackForge

A CLI scaffolder for .NET Clean Architecture (CQRS) projects.

## Installation

```bash
pip install stackforge
```

## Usage

```bash
stackforge
```

Then follow the prompts to scaffold a new project.

## What it generates

- .NET 10 Clean Architecture structure (API, Application, Domain, Infrastructure, Persistence)
- JWT authentication with ASP.NET Identity
- Swagger UI with Bearer token support
- PostgreSQL with EF Core
- Docker + docker-compose with healthchecks
- Role and user seeders (SuperAdmin out of the box)
- Git initialization with initial commit

## Quickstart after scaffolding

1. Open the project in VS Code or Visual Studio
2. Run: `docker-compose up --build`
3. Visit: `http://localhost:5000/swagger`