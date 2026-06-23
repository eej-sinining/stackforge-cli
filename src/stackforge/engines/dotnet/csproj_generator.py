from pathlib import Path
from stackforge import ui


LAYER_CONFIGS = {
    "Domain": {
        "sdk": "Microsoft.NET.Sdk",
        "references": [],
        "packages": [
            ("Microsoft.AspNetCore.Identity.EntityFrameworkCore", "10.0.4"),
        ],
    },
    "Application": {
        "sdk": "Microsoft.NET.Sdk",
        "references": ["Domain"],
        "packages": [
            ("MediatR", "14.1.0"),
            ("FluentValidation", "11.9.0"),
            ("FluentValidation.DependencyInjectionExtensions", "11.9.0"),
            ("AutoMapper", "16.1.1"),
            ("Microsoft.Extensions.DependencyInjection.Abstractions", "10.0.4"),
        ]
    },
    "Infrastructure": {
        "sdk": "Microsoft.NET.Sdk",
        "references": ["Application"],
        "packages": [],
    },
    "Persistence": {
        "sdk": "Microsoft.NET.Sdk",
        "references": ["Application"],
        "packages": [
            ("Microsoft.EntityFrameworkCore", "10.0.4"),
            ("Npgsql.EntityFrameworkCore.PostgreSQL", "10.0.2"),
            ("Microsoft.EntityFrameworkCore.Tools", "10.0.4"),
        ],
    },
    "API": {
        "sdk": "Microsoft.NET.Sdk.Web",
        "references": ["Application", "Infrastructure", "Persistence"],
        "packages": [
            ("Swashbuckle.AspNetCore", "6.5.0"),
            ("Microsoft.AspNetCore.Authentication.JwtBearer", "10.0.4"),
        ],
    },
}


def generate_csproj(layer: str, base: Path):
    config = LAYER_CONFIGS[layer]
    sdk = config["sdk"]

    project_refs = ""
    for ref in config["references"]:
        project_refs += f'\n        <ProjectReference Include="..\\{ref}\\{ref}.csproj" />'

    package_refs = ""
    for name, version in config["packages"]:
        package_refs += f'\n        <PackageReference Include="{name}" Version="{version}" />'

    item_group = ""
    if project_refs:
        item_group += f"""
    <ItemGroup>{project_refs}
    </ItemGroup>"""
    if package_refs:
        item_group += f"""
    <ItemGroup>{package_refs}
    </ItemGroup>"""

    content = f"""<Project Sdk="{sdk}">

    <PropertyGroup>
        <TargetFramework>net10.0</TargetFramework>
        <Nullable>enable</Nullable>
        <ImplicitUsings>enable</ImplicitUsings>
    </PropertyGroup>
{item_group}
</Project>"""

    csproj_path = base / layer / f"{layer}.csproj"
    csproj_path.write_text(content.strip())
    ui.file_created(f"{layer}/{layer}.csproj")