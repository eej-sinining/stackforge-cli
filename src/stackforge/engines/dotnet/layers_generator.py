from pathlib import Path


def generate_application_layer(base: Path, project: str):
    folders = [
        "Application/Common/Behaviors",
        "Application/Common/Constants",
        "Application/Common/Exceptions",
        "Application/Common/Models/Serialization",
        "Application/Helpers",
        "Application/Interfaces",
        "Application/Mappings",
        "Application/Services",
    ]
    for folder in folders:
        (base / folder).mkdir(parents=True, exist_ok=True)

    _gen_validation_behavior(base, project)
    _gen_error_messages(base, project)
    _gen_app_exceptions(base, project)
    _gen_not_found_exception(base, project)
    _gen_api_response(base, project)
    _gen_result(base, project)
    _gen_paging_params(base, project)
    _gen_paginated_result(base, project)
    _gen_paged_list(base, project)
    _gen_paged_response(base, project)
    _gen_iso_datetime(base, project)

    print("  [+] Application/ structure and files")


def generate_domain_layer(base: Path, project: str):
    folders = [
        "Domain/Common",
        "Domain/Entities/Identity",
        "Domain/Enums",
        "Domain/Utils",
    ]
    for folder in folders:
        (base / folder).mkdir(parents=True, exist_ok=True)

    _gen_base_entity(base, project)
    _gen_enum_member_extensions(base, project)
    _gen_role(base, project)
    _gen_user(base, project)
    _gen_user_role(base, project)
    _gen_global_usings(base, project)

    print("  [+] Domain/ structure and files")


def generate_infrastructure_layer(base: Path, project: str):
    folders = [
        "Infrastructure/BackgroundServices",
        "Infrastructure/Configurations",
        "Infrastructure/Options",
        "Infrastructure/Services",
    ]
    for folder in folders:
        (base / folder).mkdir(parents=True, exist_ok=True)

    print("  [+] Infrastructure/ structure and files")


def generate_persistence_layer(base: Path, project: str):
    folders = [
        "Persistence/Configurations",
        "Persistence/Extensions",
        "Persistence/Migrations",
        "Persistence/Seeders",
    ]
    for folder in folders:
        (base / folder).mkdir(parents=True, exist_ok=True)

    _gen_data_context(base, project)
    _gen_role_seeder(base, project)
    _gen_user_seeder(base, project)
    _gen_user_role_configuration(base, project)

    print("  [+] Persistence/ structure and files")


# ── Application files ──────────────────────────────────────────────────────────

def _gen_validation_behavior(base: Path, project: str):
    content = f"""using FluentValidation;
using MediatR;

namespace {project}.Application.Common.Behaviors
{{
    public class ValidationBehavior<TRequest, TResponse> : IPipelineBehavior<TRequest, TResponse>
        where TRequest : notnull
    {{
        private readonly IEnumerable<IValidator<TRequest>> _validators;

        public ValidationBehavior(IEnumerable<IValidator<TRequest>> validators)
        {{
            _validators = validators;
        }}

        public async Task<TResponse> Handle(TRequest request, RequestHandlerDelegate<TResponse> next, CancellationToken cancellationToken)
        {{
            if (_validators.Any())
            {{
                var context = new ValidationContext<TRequest>(request);
                var validationResults = await Task.WhenAll(_validators.Select(v => v.ValidateAsync(context, cancellationToken)));
                var failures = validationResults.SelectMany(r => r.Errors).Where(f => f != null).ToList();
                if (failures.Count != 0)
                    throw new ValidationException(failures);
            }}
            return await next();
        }}
    }}
}}
"""
    (base / "Application/Common/Behaviors/ValidationBehavior.cs").write_text(content)


def _gen_error_messages(base: Path, project: str):
    content = f"""namespace {project}.Application.Common.Constants
{{
    public static class ErrorMessages
    {{
        public const string NotFound = "The requested resource was not found.";
        public const string Unauthorized = "You are not authorized to perform this action.";
        public const string BadRequest = "The request is invalid.";
        public const string InternalServerError = "An unexpected error occurred.";
    }}
}}
"""
    (base / "Application/Common/Constants/ErrorMessages.cs").write_text(content)


def _gen_app_exceptions(base: Path, project: str):
    content = f"""namespace {project}.Application.Common.Exceptions
{{
    public class AppException : Exception
    {{
        public int StatusCode {{ get; }}

        public AppException(string message, int statusCode = 400) : base(message)
        {{
            StatusCode = statusCode;
        }}
    }}
}}
"""
    (base / "Application/Common/Exceptions/AppExceptions.cs").write_text(content)


def _gen_not_found_exception(base: Path, project: str):
    content = f"""namespace {project}.Application.Common.Exceptions
{{
    public class NotFoundException : Exception
    {{
        public NotFoundException(string name, object key)
            : base($"{{name}} ({{key}}) was not found.")
        {{
        }}
    }}
}}
"""
    (base / "Application/Common/Exceptions/NotFoundException.cs").write_text(content)


def _gen_api_response(base: Path, project: str):
    content = f"""namespace {project}.Application.Common.Models
{{
    public class ApiResponse<T>
    {{
        public bool Success {{ get; set; }}
        public string? Message {{ get; set; }}
        public T? Data {{ get; set; }}

        public static ApiResponse<T> Ok(T data, string message = "Success") =>
            new() {{ Success = true, Message = message, Data = data }};

        public static ApiResponse<T> Fail(string message) =>
            new() {{ Success = false, Message = message }};
    }}
}}
"""
    (base / "Application/Common/Models/ApiResponse.cs").write_text(content)


def _gen_result(base: Path, project: str):
    content = f"""namespace {project}.Application.Common.Models
{{
    public class Result
    {{
        public bool IsSuccess {{ get; }}
        public string? Error {{ get; }}

        protected Result(bool isSuccess, string? error)
        {{
            IsSuccess = isSuccess;
            Error = error;
        }}

        public static Result Success() => new(true, null);
        public static Result Failure(string error) => new(false, error);
    }}

    public class Result<T> : Result
    {{
        public T? Value {{ get; }}

        protected Result(bool isSuccess, T? value, string? error) : base(isSuccess, error)
        {{
            Value = value;
        }}

        public static Result<T> Success(T value) => new(true, value, null);
        public static new Result<T> Failure(string error) => new(false, default, error);
    }}
}}
"""
    (base / "Application/Common/Models/Result.cs").write_text(content)


def _gen_paging_params(base: Path, project: str):
    content = f"""namespace {project}.Application.Common.Models
{{
    public class PagingParams
    {{
        public int PageNumber {{ get; set; }} = 1;
        public int PageSize {{ get; set; }} = 10;
    }}
}}
"""
    (base / "Application/Common/Models/PagingParams.cs").write_text(content)


def _gen_paginated_result(base: Path, project: str):
    content = f"""namespace {project}.Application.Common.Models
{{
    public class PaginatedResult<T>
    {{
        public List<T> Items {{ get; set; }} = new();
        public int TotalCount {{ get; set; }}
        public int PageNumber {{ get; set; }}
        public int PageSize {{ get; set; }}
        public int TotalPages => (int)Math.Ceiling(TotalCount / (double)PageSize);
        public bool HasPreviousPage => PageNumber > 1;
        public bool HasNextPage => PageNumber < TotalPages;
    }}
}}
"""
    (base / "Application/Common/Models/PaginatedResult.cs").write_text(content)


def _gen_paged_list(base: Path, project: str):
    content = f"""using Microsoft.EntityFrameworkCore;

namespace {project}.Application.Common.Models
{{
    public class PagedList<T>
    {{
        public List<T> Items {{ get; }}
        public int TotalCount {{ get; }}
        public int PageNumber {{ get; }}
        public int PageSize {{ get; }}
        public int TotalPages => (int)Math.Ceiling(TotalCount / (double)PageSize);
        public bool HasPreviousPage => PageNumber > 1;
        public bool HasNextPage => PageNumber < TotalPages;

        private PagedList(List<T> items, int totalCount, int pageNumber, int pageSize)
        {{
            Items = items;
            TotalCount = totalCount;
            PageNumber = pageNumber;
            PageSize = pageSize;
        }}

        public static async Task<PagedList<T>> CreateAsync(IQueryable<T> source, int pageNumber, int pageSize)
        {{
            var totalCount = await source.CountAsync();
            var items = await source.Skip((pageNumber - 1) * pageSize).Take(pageSize).ToListAsync();
            return new PagedList<T>(items, totalCount, pageNumber, pageSize);
        }}
    }}
}}
"""
    (base / "Application/Common/Models/PagedList.cs").write_text(content)


def _gen_paged_response(base: Path, project: str):
    content = f"""namespace {project}.Application.Common.Models
{{
    public class PagedResponse<T>
    {{
        public List<T> Items {{ get; set; }} = new();
        public int TotalCount {{ get; set; }}
        public int PageNumber {{ get; set; }}
        public int PageSize {{ get; set; }}
        public int TotalPages {{ get; set; }}
        public bool HasPreviousPage {{ get; set; }}
        public bool HasNextPage {{ get; set; }}
    }}
}}
"""
    (base / "Application/Common/Models/PagedResponse.cs").write_text(content)


def _gen_iso_datetime(base: Path, project: str):
    content = f"""using System.Text.Json;
using System.Text.Json.Serialization;

namespace {project}.Application.Common.Models.Serialization
{{
    public class IsoDateTimeConverter : JsonConverter<DateTime>
    {{
        public override DateTime Read(ref Utf8JsonReader reader, Type typeToConvert, JsonSerializerOptions options)
            => DateTime.Parse(reader.GetString()!);

        public override void Write(Utf8JsonWriter writer, DateTime value, JsonSerializerOptions options)
            => writer.WriteStringValue(value.ToUniversalTime().ToString("yyyy-MM-ddTHH:mm:ssZ"));
    }}
}}
"""
    (base / "Application/Common/Models/Serialization/IsoDateTime.cs").write_text(content)


# ── Domain files ───────────────────────────────────────────────────────────────

def _gen_base_entity(base: Path, project: str):
    content = f"""namespace {project}.Domain.Common
{{
    public abstract class BaseEntity
    {{
        public Guid Id {{ get; set; }} = Guid.NewGuid();
        public DateTime CreatedAt {{ get; set; }} = DateTime.UtcNow;
        public DateTime UpdatedAt {{ get; set; }} = DateTime.UtcNow;
    }}
}}
"""
    (base / "Domain/Common/BaseEntity.cs").write_text(content)


def _gen_enum_member_extensions(base: Path, project: str):
    content = f"""using System.Runtime.Serialization;
using System.Reflection;

namespace {project}.Domain.Common
{{
    public static class EnumMemberExtensions
    {{
        public static string ToEnumMemberValue<T>(this T value) where T : Enum
        {{
            return typeof(T)
                .GetField(value.ToString())
                ?.GetCustomAttribute<EnumMemberAttribute>()
                ?.Value ?? value.ToString();
        }}
    }}
}}
"""
    (base / "Domain/Common/EnumMemberExtensions.cs").write_text(content)


def _gen_role(base: Path, project: str):
    content = f"""using Microsoft.AspNetCore.Identity;

namespace {project}.Domain.Entities.Identity
{{
    public class Role : IdentityRole<Guid>
    {{
        public ICollection<UserRole> UserRoles {{ get; set; }} = new List<UserRole>();
    }}
}}
"""
    (base / "Domain/Entities/Identity/Role.cs").write_text(content)


def _gen_user(base: Path, project: str):
    content = f"""using Microsoft.AspNetCore.Identity;

namespace {project}.Domain.Entities.Identity
{{
    public class User : IdentityUser<Guid>
    {{
        public string FirstName {{ get; set; }} = string.Empty;
        public string LastName {{ get; set; }} = string.Empty;
        public DateTime CreatedAt {{ get; set; }} = DateTime.UtcNow;
        public DateTime UpdatedAt {{ get; set; }} = DateTime.UtcNow;
        public ICollection<UserRole> UserRoles {{ get; set; }} = new List<UserRole>();
    }}
}}
"""
    (base / "Domain/Entities/Identity/User.cs").write_text(content)


def _gen_user_role(base: Path, project: str):
    content = f"""using Microsoft.AspNetCore.Identity;

namespace {project}.Domain.Entities.Identity
{{
    public class UserRole : IdentityUserRole<Guid>
    {{
        public virtual User User {{ get; set; }} = null!;
        public virtual Role Role {{ get; set; }} = null!;
    }}
}}
"""
    (base / "Domain/Entities/Identity/UserRole.cs").write_text(content)


def _gen_global_usings(base: Path, project: str):
    content = f"""global using {project}.Domain.Common;
global using {project}.Domain.Entities;
"""
    (base / "Domain/GlobalUsings.cs").write_text(content)


# ── Persistence files ──────────────────────────────────────────────────────────

def _gen_data_context(base: Path, project: str):
    identity_db_context = "IdentityDbContext<"
    content = f"""using {project}.Domain.Entities.Identity;
using Humanizer;
using Microsoft.AspNetCore.Identity;
using Microsoft.AspNetCore.Identity.EntityFrameworkCore;
using Microsoft.EntityFrameworkCore;
using System.Reflection;

namespace {project}.Persistence
{{
    public class DataContext : {identity_db_context}
        User,
        Role,
        Guid,
        IdentityUserClaim<Guid>,
        UserRole,
        IdentityUserLogin<Guid>,
        IdentityRoleClaim<Guid>,
        IdentityUserToken<Guid>>
    {{
        public DataContext(DbContextOptions<DataContext> options) : base(options)
        {{
        }}

        protected override void OnModelCreating(ModelBuilder builder)
        {{
            base.OnModelCreating(builder);
            builder.ApplyConfigurationsFromAssembly(Assembly.GetExecutingAssembly());
            foreach (var entityType in builder.Model.GetEntityTypes())
            {{
                var table = entityType.GetTableName();
                if (table!.StartsWith("AspNet"))
                    entityType.SetTableName(table.Substring(6).Underscore());
            }}
        }}
    }}
}}
"""
    (base / "Persistence/DataContext.cs").write_text(content)


def _gen_role_seeder(base: Path, project: str):
    content = f"""using {project}.Domain.Entities.Identity;
using Microsoft.AspNetCore.Identity;

namespace {project}.Persistence.Seeders
{{
    public static class RoleSeeder
    {{
        public static async Task SeedAsync(RoleManager<Role> roleManager)
        {{
            string[] roles = {{ "SuperAdmin", "Admin", "User" }};

            foreach (var role in roles)
            {{
                if (!await roleManager.RoleExistsAsync(role))
                    await roleManager.CreateAsync(new Role {{ Name = role }});
            }}
        }}
    }}
}}
"""
    (base / "Persistence/Seeders/RoleSeeder.cs").write_text(content)


def _gen_user_seeder(base: Path, project: str):
    content = f"""using {project}.Domain.Entities.Identity;
using Microsoft.AspNetCore.Identity;

namespace {project}.Persistence.Seeders
{{
    public static class UserSeeder
    {{
        public static async Task SeedAsync(UserManager<User> userManager)
        {{
            var superAdmin = await userManager.FindByEmailAsync("super_admin@{project.lower()}.com");

            if (superAdmin == null)
            {{
                var user = new User
                {{
                    UserName = "super_admin@{project.lower()}.com",
                    Email = "super_admin@{project.lower()}.com",
                    FirstName = "Super",
                    LastName = "Admin",
                    EmailConfirmed = true,
                }};

                await userManager.CreateAsync(user, "Pa$$w0rd");
                await userManager.AddToRoleAsync(user, "SuperAdmin");
            }}
        }}
    }}
}}
"""
    (base / "Persistence/Seeders/UserSeeder.cs").write_text(content)


def _gen_user_role_configuration(base: Path, project: str):
    content = f"""using {project}.Domain.Entities.Identity;
using Microsoft.EntityFrameworkCore;
using Microsoft.EntityFrameworkCore.Metadata.Builders;

namespace {project}.Persistence.Configurations
{{
    public class UserRoleConfiguration : IEntityTypeConfiguration<UserRole>
    {{
        public void Configure(EntityTypeBuilder<UserRole> builder)
        {{
            builder.HasKey(ur => new {{ ur.UserId, ur.RoleId }});

            builder.HasOne(ur => ur.User)
                .WithMany(u => u.UserRoles)
                .HasForeignKey(ur => ur.UserId)
                .IsRequired();

            builder.HasOne(ur => ur.Role)
                .WithMany(r => r.UserRoles)
                .HasForeignKey(ur => ur.RoleId)
                .IsRequired();
        }}
    }}
}}
"""
    (base / "Persistence/Configurations/UserRoleConfiguration.cs").write_text(content)