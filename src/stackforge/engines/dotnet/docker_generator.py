from pathlib import Path
from stackforge import ui


def generate_dockerfile(base: Path):
    content = """FROM mcr.microsoft.com/dotnet/sdk:10.0 AS build
WORKDIR /app

COPY . .

RUN dotnet publish API/API.csproj -c Release -o out

ENTRYPOINT ["dotnet", "out/API.dll"]
"""

    file_path = base / "Dockerfile"
    file_path.write_text(content)
    ui.file_created("Dockerfile")


def generate_docker_compose(base: Path, project: str):
    project_lower = project.lower()

    content = f"""services:
  api:
    build: .
    container_name: {project_lower}_api
    ports:
      - "5000:8080"
    environment:
      - ASPNETCORE_ENVIRONMENT=Development
      - ConnectionStrings__DefaultConnection=Host=db;Port=5432;Database={project_lower}_db;Username=postgres;Password=postgres
      - Jwt__Issuer=http://localhost:5000
      - Jwt__Audience=http://localhost:5000
      - Jwt__SecretKey=your-super-secret-key-change-this-in-production
      - Jwt__ExpiryMinutes=60
    depends_on:
      db:
        condition: service_healthy

  db:
    image: postgres:latest
    container_name: {project_lower}_db
    environment:
      POSTGRES_DB: {project_lower}_db
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: postgres
    ports:
      - "5432:5432"
    volumes:
      - {project_lower}_pgdata:/var/lib/postgresql
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U postgres"]
      interval: 5s
      timeout: 5s
      retries: 5

volumes:
  {project_lower}_pgdata:
"""

    file_path = base / "docker-compose.yml"
    file_path.write_text(content)
    ui.file_created("docker-compose.yml")