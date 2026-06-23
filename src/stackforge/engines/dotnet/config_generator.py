from pathlib import Path
from stackforge import ui


def generate_env(base: Path, project: str):
    project_lower = project.lower()

    content = f"""ASPNETCORE_ENVIRONMENT=Development
DB_HOST=db
DB_PORT=5432
DB_NAME={project_lower}_db
DB_USER=postgres
DB_PASSWORD=postgres
JWT_ISSUER=https://localhost:5000
JWT_AUDIENCE=https://localhost:5000
JWT_SECRET_KEY=your-super-secret-key-change-this-in-production
JWT_EXPIRY_MINUTES=60
"""

    file_path = base / ".env"
    file_path.write_text(content)
    ui.file_created(".env")


def generate_appsettings(base: Path, project: str):
    project_lower = project.lower()

    content = f"""{{
  "ConnectionStrings": {{
    "DefaultConnection": "Host=db;Port=5432;Database={project_lower}_db;Username=postgres;Password=postgres"
  }},
  "Jwt": {{
    "Issuer": "https://localhost:5000",
    "Audience": "https://localhost:5000",
    "SecretKey": "your-super-secret-key-change-this-in-production",
    "ExpiryMinutes": 60
  }},
  "Logging": {{
    "LogLevel": {{
      "Default": "Information",
      "Microsoft.AspNetCore": "Warning"
    }}
  }},
  "AllowedHosts": "*"
}}
"""

    file_path = base / "API" / "appsettings.json"
    file_path.write_text(content)
    ui.file_created("API/appsettings.json")


def generate_appsettings_development(base: Path, project: str):
    project_lower = project.lower()

    content = f"""{{
  "ConnectionStrings": {{
    "DefaultConnection": "Host=localhost;Port=5432;Database={project_lower}_db;Username=postgres;Password=postgres"
  }},
  "Jwt": {{
    "Issuer": "https://localhost:5000",
    "Audience": "https://localhost:5000",
    "SecretKey": "your-super-secret-key-change-this-in-production",
    "ExpiryMinutes": 60
  }},
  "Logging": {{
    "LogLevel": {{
      "Default": "Information",
      "Microsoft.AspNetCore": "Warning"
    }}
  }}
}}
"""

    file_path = base / "API" / "appsettings.Development.json"
    file_path.write_text(content)
    ui.file_created("API/appsettings.Development.json")