import subprocess
from pathlib import Path

def generate_sln(base: Path, project: str):
    layers = ["API", "Application", "Domain", "Infrastructure", "Persistence"]
    
    project_entries = ""
    for layer in layers:
        guid = str(__import__('uuid').uuid4()).upper()
        project_entries += f"""Project("{{FAE04EC0-301F-11D3-BF4B-00C04F79EFBC}}") = "{layer}", "{layer}\\{layer}.csproj", "{{{guid}}}"
EndProject
"""

    content = f"""
Microsoft Visual Studio Solution File, Format Version 12.00
# Visual Studio Version 17
{project_entries}"""

    file_path = base / f"{project}.sln"
    file_path.write_text(content)
    print(f"  [+] {project}.sln")

    
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
    print("  [+] .gitignore")


def git_init(base: Path, project: str):
    try:
        subprocess.run(["git", "init"], cwd=base, check=True, capture_output=True)
        print("  [+] git init")

        subprocess.run(["git", "add", "."], cwd=base, check=True, capture_output=True)
        print("  [+] git add .")

        subprocess.run(
            ["git", "commit", "-m", f"initial: scaffold {project} with stackforge"],
            cwd=base,
            check=True,
            capture_output=True
        )
        print("  [+] initial commit")

    except subprocess.CalledProcessError as e:
        print(f"  [!] Git error: {e}")
    except FileNotFoundError:
        print("  [!] Git not found. Make sure Git is installed and in your PATH.")

