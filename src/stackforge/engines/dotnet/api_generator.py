from pathlib import Path
from stackforge import ui


def generate_api_structure(base: Path, project: str):
    # Folders
    folders = [
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

    for folder in folders:
        (base / folder).mkdir(parents=True, exist_ok=True)

    _generate_base_controller(base, project)
    _generate_jwt_options(base, project)
    _generate_ijwt_service(base, project)
    _generate_jwt_service(base, project)
    _generate_enum_schema_filter(base, project)
    _generate_api_roles(base, project)
    _generate_launch_settings(base)
    _generate_login_dto(base, project)
    _generate_account_controller(base, project)

    ui.file_created("API/ structure and files")


def _generate_base_controller(base: Path, project: str):
    content = f"""using Microsoft.AspNetCore.Mvc;
using System.Security.Claims;

namespace {project}.API.Controllers
{{
    [Route("api/[controller]")]
    [ApiController]
    public class BaseApiController : ControllerBase
    {{
        protected Guid GetUserId() => Guid.Parse(User?.FindFirst(ClaimTypes.NameIdentifier)?.Value!);

        protected string GetCurrentEmail() => User?.FindFirstValue(ClaimTypes.Email)!;

        protected Guid? GetOrganizationId()
        {{
            var claim = User?.FindFirst("OrganizationId");

            if (claim == null || !Guid.TryParse(claim.Value, out var orgId))
                return null;

            return orgId;
        }}
    }}
}}
"""
    (base / "API/Controllers/BaseApiController.cs").write_text(content)


def _generate_jwt_options(base: Path, project: str):
    content = f"""namespace {project}.API.Options
{{
    public class JwtOptions
    {{
        public string Issuer {{ get; set; }} = string.Empty;
        public string Audience {{ get; set; }} = string.Empty;
        public string SecretKey {{ get; set; }} = string.Empty;
        public int ExpiryMinutes {{ get; set; }}
    }}
}}
"""
    (base / "API/Options/JwtOptions.cs").write_text(content)


def _generate_ijwt_service(base: Path, project: str):
    content = f"""namespace {project}.API.Interface
{{
    public interface IJwtService
    {{
        string GenerateToken(Guid userId, string email);
    }}
}}
"""
    (base / "API/Interface/IJwtService.cs").write_text(content)


def _generate_jwt_service(base: Path, project: str):
    content = f"""using {project}.API.Interface;
using {project}.API.Options;
using Microsoft.Extensions.Options;
using Microsoft.IdentityModel.Tokens;
using System.IdentityModel.Tokens.Jwt;
using System.Security.Claims;
using System.Text;

namespace {project}.API.Services
{{
    public class JwtService : IJwtService
    {{
        private readonly JwtOptions _options;

        public JwtService(IOptions<JwtOptions> options)
        {{
            _options = options.Value;
        }}

        public string GenerateToken(Guid userId, string email)
        {{
            var claims = new[]
            {{
                new Claim(ClaimTypes.NameIdentifier, userId.ToString()),
                new Claim(ClaimTypes.Email, email),
            }};

            var key = new SymmetricSecurityKey(Encoding.UTF8.GetBytes(_options.SecretKey));
            var creds = new SigningCredentials(key, SecurityAlgorithms.HmacSha256);

            var token = new JwtSecurityToken(
                issuer: _options.Issuer,
                audience: _options.Audience,
                claims: claims,
                expires: DateTime.UtcNow.AddMinutes(_options.ExpiryMinutes),
                signingCredentials: creds);

            return new JwtSecurityTokenHandler().WriteToken(token);
        }}
    }}
}}
"""
    (base / "API/Services/JwtService.cs").write_text(content)


def _generate_enum_schema_filter(base: Path, project: str):
    content = f"""using Microsoft.OpenApi.Any;
using Microsoft.OpenApi.Models;
using Swashbuckle.AspNetCore.SwaggerGen;
using System.Runtime.Serialization;

namespace {project}.API.Swagger
{{
    public class EnumMemberSchemaFilter : ISchemaFilter
    {{
        public void Apply(OpenApiSchema schema, SchemaFilterContext context)
        {{
            if (!context.Type.IsEnum) return;

            schema.Enum.Clear();
            foreach (var member in Enum.GetNames(context.Type))
            {{
                var field = context.Type.GetField(member);
                var attr = field?.GetCustomAttributes(typeof(EnumMemberAttribute), false)
                                 .OfType<EnumMemberAttribute>()
                                 .FirstOrDefault();
                schema.Enum.Add(new OpenApiString(attr?.Value ?? member));
            }}
        }}
    }}
}}
"""
    (base / "API/Swagger/EnumMemberSchemaFilter.cs").write_text(content)


def _generate_api_roles(base: Path, project: str):
    content = f"""namespace {project}.API.Configurations.Swagger
{{
    public static class ApiRoles
    {{
        public const string SuperAdmin = "SuperAdmin";
        public const string Admin = "Admin";
        public const string User = "User";
    }}
}}
"""
    (base / "API/Configurations/Swagger/ApiRoles.cs").write_text(content)


def _generate_launch_settings(base: Path):
    content = """{
  "$schema": "https://json.schemastore.org/launchsettings.json",
  "profiles": {
    "http": {
      "commandName": "Project",
      "environmentVariables": {
        "ASPNETCORE_ENVIRONMENT": "Development"
      },
      "dotnetRunMessages": true,
      "applicationUrl": "http://localhost:5000"
    },
    "https": {
      "commandName": "Project",
      "environmentVariables": {
        "ASPNETCORE_ENVIRONMENT": "Development"
      },
      "dotnetRunMessages": true,
      "applicationUrl": "https://localhost:7013;http://localhost:5282"
    },
    "Container (Dockerfile)": {
      "commandName": "Docker",
      "launchUrl": "{Scheme}://{ServiceHost}:{ServicePort}",
      "environmentVariables": {
        "ASPNETCORE_HTTPS_PORTS": "8081",
        "ASPNETCORE_HTTP_PORTS": "8080"
      },
      "publishAllPorts": true,
      "useSSL": true
    }
  }
}
"""
    (base / "API/Properties/launchSettings.json").write_text(content)

def _generate_login_dto(base: Path, project: str):
    content = f"""namespace {project}.API.DTOs
{{
    public class LoginRequest
    {{
        public string Email {{ get; set; }} = string.Empty;
        public string Password {{ get; set; }} = string.Empty;
    }}

    public class LoginResponse
    {{
        public string Token {{ get; set; }} = string.Empty;
        public string Email {{ get; set; }} = string.Empty;
        public string FullName {{ get; set; }} = string.Empty;
    }}

    public class CurrentUserResponse
    {{
        public Guid Id {{ get; set; }}
        public string Email {{ get; set; }} = string.Empty;
        public string FullName {{ get; set; }} = string.Empty;
        public IList<string> Roles {{ get; set; }} = new List<string>();
    }}
}}
"""
    (base / "API/DTOs/AccountDTOs.cs").write_text(content)


def _generate_account_controller(base: Path, project: str):
    content = f"""using {project}.API.Controllers;
using {project}.API.DTOs;
using {project}.API.Interface;
using {project}.Domain.Entities.Identity;
using Microsoft.AspNetCore.Authorization;
using Microsoft.AspNetCore.Identity;
using Microsoft.AspNetCore.Mvc;

namespace {project}.API.Controllers.Main
{{
    public class AccountController : BaseApiController
    {{
        private readonly UserManager<User> _userManager;
        private readonly SignInManager<User> _signInManager;
        private readonly IJwtService _jwtService;

        public AccountController(
            UserManager<User> userManager,
            SignInManager<User> signInManager,
            IJwtService jwtService)
        {{
            _userManager = userManager;
            _signInManager = signInManager;
            _jwtService = jwtService;
        }}

        [HttpPost("login")]
        public async Task<IActionResult> Login([FromBody] LoginRequest request)
        {{
            var user = await _userManager.FindByEmailAsync(request.Email);
            if (user == null)
                return Unauthorized("Invalid credentials.");

            var result = await _signInManager.CheckPasswordSignInAsync(user, request.Password, false);
            if (!result.Succeeded)
                return Unauthorized("Invalid credentials.");

            var token = _jwtService.GenerateToken(user.Id, user.Email!);

            return Ok(new LoginResponse
            {{
                Token = token,
                Email = user.Email!,
                FullName = $"{{user.FirstName}} {{user.LastName}}"
            }});
        }}

        [Authorize]
        [HttpGet("me")]
        public async Task<IActionResult> Me()
        {{
            var user = await _userManager.FindByIdAsync(GetUserId().ToString());
            if (user == null)
                return NotFound("User not found.");

            var roles = await _userManager.GetRolesAsync(user);

            return Ok(new CurrentUserResponse
            {{
                Id = user.Id,
                Email = user.Email!,
                FullName = $"{{user.FirstName}} {{user.LastName}}",
                Roles = roles
            }});
        }}
    }}
}}
"""
    (base / "API/Controllers/Main/AccountController.cs").write_text(content)