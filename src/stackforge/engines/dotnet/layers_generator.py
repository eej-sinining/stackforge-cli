from pathlib import Path
from stackforge import ui
from stackforge.templating import render_file

ENGINE = "dotnet"


def _generate_layer(base: Path, project: str, layer: str, folders: list[str], templates: list[str]):
    for folder in folders:
        (base / folder).mkdir(parents=True, exist_ok=True)

    for template in templates:
        render_file(ENGINE, base, template, project)

    ui.file_created(f"{layer}/ structure and files")


def generate_application_layer(base: Path, project: str):
    _generate_layer(
        base,
        project,
        "Application",
        folders=[
            "Application/Common/Behaviors",
            "Application/Common/Constants",
            "Application/Common/Exceptions",
            "Application/Common/Models/Serialization",
            "Application/Helpers",
            "Application/Interfaces",
            "Application/Mappings",
            "Application/Services",
        ],
        templates=[
            "Application/Common/Behaviors/ValidationBehavior.cs",
            "Application/Common/Constants/ErrorMessages.cs",
            "Application/Common/Exceptions/AppExceptions.cs",
            "Application/Common/Exceptions/NotFoundException.cs",
            "Application/Common/Models/ApiResponse.cs",
            "Application/Common/Models/Result.cs",
            "Application/Common/Models/PagingParams.cs",
            "Application/Common/Models/PaginatedResult.cs",
            "Application/Common/Models/PagedList.cs",
            "Application/Common/Models/PagedResponse.cs",
            "Application/Common/Models/Serialization/IsoDateTime.cs",
        ],
    )


def generate_domain_layer(base: Path, project: str):
    _generate_layer(
        base,
        project,
        "Domain",
        folders=[
            "Domain/Common",
            "Domain/Entities/Identity",
            "Domain/Enums",
            "Domain/Utils",
        ],
        templates=[
            "Domain/Common/BaseEntity.cs",
            "Domain/Common/EnumMemberExtensions.cs",
            "Domain/Entities/Identity/Role.cs",
            "Domain/Entities/Identity/User.cs",
            "Domain/Entities/Identity/UserRole.cs",
            "Domain/GlobalUsings.cs",
        ],
    )


def generate_infrastructure_layer(base: Path, project: str):
    _generate_layer(
        base,
        project,
        "Infrastructure",
        folders=[
            "Infrastructure/BackgroundServices",
            "Infrastructure/Configurations",
            "Infrastructure/Options",
            "Infrastructure/Services",
        ],
        templates=[],
    )


def generate_persistence_layer(base: Path, project: str):
    _generate_layer(
        base,
        project,
        "Persistence",
        folders=[
            "Persistence/Configurations",
            "Persistence/Extensions",
            "Persistence/Migrations",
            "Persistence/Seeders",
        ],
        templates=[
            "Persistence/DataContext.cs",
            "Persistence/Seeders/RoleSeeder.cs",
            "Persistence/Seeders/UserSeeder.cs",
            "Persistence/Configurations/UserRoleConfiguration.cs",
        ],
    )
