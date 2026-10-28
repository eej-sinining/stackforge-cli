import uuid
import subprocess
from pathlib import Path
from stackforge import ui

def generate_sln(base: Path, project: str):
    layers = ["API", "Application", "Domain", "Infrastructure", "Persistence"]
    configurations = ["Debug|Any CPU", "Release|Any CPU"]

    project_entries = ""
    project_configs = ""
    for layer in layers:
        guid = "{" + str(uuid.uuid4()).upper() + "}"
        project_entries += f"""Project("{{FAE04EC0-301F-11D3-BF4B-00C04F79EFBC}}") = "{layer}", "{layer}\\{layer}.csproj", "{guid}"
EndProject
"""
        for config in configurations:
            project_configs += f"\t\t{guid}.{config}.ActiveCfg = {config}\n"
            project_configs += f"\t\t{guid}.{config}.Build.0 = {config}\n"

    solution_configs = "".join(f"\t\t{config} = {config}\n" for config in configurations)

    # Without the Global section, dotnet build/restore on the .sln finds no projects to build.
    content = f"""
Microsoft Visual Studio Solution File, Format Version 12.00
# Visual Studio Version 17
{project_entries}Global
\tGlobalSection(SolutionConfigurationPlatforms) = preSolution
{solution_configs}\tEndGlobalSection
\tGlobalSection(ProjectConfigurationPlatforms) = postSolution
{project_configs}\tEndGlobalSection
EndGlobal
"""

    file_path = base / f"{project}.sln"
    file_path.write_text(content)
    ui.file_created(f"{project}.sln")

    
def generate_gitignore(base: Path):
    content = """# Build results
bin/
obj/
out/

# Environment
.env

# VS / Rider
.vs/
.idea/
*.user

# Logs
*.log
"""

    file_path = base / ".gitignore"
    file_path.write_text(content)
    ui.file_created(".gitignore")


def generate_github_workflow(base: Path):
    workflow_dir = base / ".github" / "workflows"
    workflow_dir.mkdir(parents=True, exist_ok=True)

    content = """name: Sync Environment Branches

on:
  push:
    branches:
      - main

permissions:
  contents: write

jobs:
  sync-branches:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
        with:
          fetch-depth: 0

      - name: Create staging branch if missing
        run: |
          if ! git ls-remote --exit-code origin refs/heads/staging; then
            git push origin HEAD:refs/heads/staging
          fi

      - name: Create development branch if missing
        run: |
          if ! git ls-remote --exit-code origin refs/heads/development; then
            git push origin HEAD:refs/heads/development
          fi
"""
    file_path = workflow_dir / "sync-branches.yml"
    file_path.write_text(content.lstrip())
    ui.file_created(".github/workflows/sync-branches.yml")


def git_init(base: Path, project: str):
    try:
        subprocess.run(["git", "init", "-b", "main"], cwd=base, check=True, capture_output=True)
        ui.file_created("git init (main)")

        subprocess.run(["git", "add", "."], cwd=base, check=True, capture_output=True)
        ui.file_created("git add .")

        subprocess.run(
            ["git", "commit", "-m", f"initial: scaffold {project} with stackforge"],
            cwd=base,
            check=True,
            capture_output=True
        )
        ui.file_created("initial commit")

        subprocess.run(["git", "branch", "staging"], cwd=base, check=True, capture_output=True)
        subprocess.run(["git", "branch", "development"], cwd=base, check=True, capture_output=True)
        ui.file_created("branches: main, staging, development")

    except subprocess.CalledProcessError as e:
        ui.error(f"Git error: {e}")
    except FileNotFoundError:
        ui.error("Git not found. Make sure Git is installed and in your PATH.")

