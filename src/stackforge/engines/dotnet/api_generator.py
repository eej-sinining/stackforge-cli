from pathlib import Path
from stackforge import ui
from stackforge.templating import render_file

ENGINE = "dotnet"

API_FOLDERS = [
    "API/Configurations/Swagger",
    "API/Controllers/Main",
    "API/Helpers",
    "API/Interface",
    "API/Options",
    "API/Properties",
    "API/Services",
    "API/Swagger",
    "API/DTOs",
]

API_TEMPLATES = [
    "API/Controllers/BaseApiController.cs",
    "API/Options/JwtOptions.cs",
    "API/Interface/IJwtService.cs",
    "API/Services/JwtService.cs",
    "API/Swagger/EnumMemberSchemaFilter.cs",
    "API/Configurations/Swagger/ApiRoles.cs",
    "API/Properties/launchSettings.json",
    "API/DTOs/AccountDTOs.cs",
    "API/Controllers/Main/AccountController.cs",
]


def generate_api_structure(base: Path, project: str):
    for folder in API_FOLDERS:
        (base / folder).mkdir(parents=True, exist_ok=True)

    for template in API_TEMPLATES:
        render_file(ENGINE, base, template, project)

    ui.file_created("API/ structure and files")
