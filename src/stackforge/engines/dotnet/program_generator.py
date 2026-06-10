from pathlib import Path


def generate_configure_services(layer: str, base: Path, project: str):
    templates = {
        "Application": f"""using FluentValidation;
using MediatR;
using Microsoft.Extensions.DependencyInjection;
using System.Reflection;

namespace {project}.Application
{{
    public static class ConfigureServices
    {{
        public static IServiceCollection AddApplicationServices(this IServiceCollection services)
        {{
            services.AddMediatR(cfg =>
                cfg.RegisterServicesFromAssembly(Assembly.GetExecutingAssembly()));

            services.AddAutoMapper(cfg => cfg.AddMaps(Assembly.GetExecutingAssembly()));

            services.AddValidatorsFromAssembly(Assembly.GetExecutingAssembly());

            return services;
        }}
    }}
}}
""",
        "Infrastructure": f"""using Microsoft.Extensions.DependencyInjection;

namespace {project}.Infrastructure
{{
    public static class ConfigureServices
    {{
        public static IServiceCollection AddInfrastructureServices(this IServiceCollection services)
        {{
            // Register infrastructure services here

            return services;
        }}
    }}
}}
""",
        "Persistence": f"""using {project}.Persistence;
using Microsoft.EntityFrameworkCore;
using Microsoft.Extensions.Configuration;
using Microsoft.Extensions.DependencyInjection;

namespace {project}.Persistence
{{
    public static class ConfigureServices
    {{
        public static IServiceCollection AddPersistenceServices(this IServiceCollection services, IConfiguration configuration)
        {{
            services.AddDbContext<DataContext>(options =>
                options.UseNpgsql(configuration.GetConnectionString("DefaultConnection")));

            return services;
        }}
    }}
}}
""",
    }

    if layer not in templates:
        return

    file_path = base / layer / "ConfigureServices.cs"
    file_path.write_text(templates[layer])
    print(f"  [+] {layer}/ConfigureServices.cs")


def generate_program_cs(base: Path, project: str):
    content = f"""using {project}.Application;
using {project}.Infrastructure;
using {project}.Persistence;
using {project}.API.Interface;
using {project}.API.Options;
using {project}.API.Services;
using Microsoft.AspNetCore.Authentication.JwtBearer;
using Microsoft.AspNetCore.Identity;
using Microsoft.IdentityModel.Tokens;
using {project}.Domain.Entities.Identity;
using System.Text;

var builder = WebApplication.CreateBuilder(args);

// Layer services
builder.Services.AddApplicationServices();
builder.Services.AddInfrastructureServices();
builder.Services.AddPersistenceServices(builder.Configuration);

// Identity
builder.Services.AddIdentity<User, Role>(options =>
{{
    options.Password.RequireDigit = true;
    options.Password.RequireLowercase = true;
    options.Password.RequireUppercase = true;
    options.Password.RequireNonAlphanumeric = true;
    options.Password.RequiredLength = 8;
}})
.AddEntityFrameworkStores<DataContext>()
.AddDefaultTokenProviders();

// JWT
builder.Services.Configure<JwtOptions>(builder.Configuration.GetSection("Jwt"));
var jwtOptions = new {project}.API.Options.JwtOptions();
builder.Configuration.GetSection("Jwt").Bind(jwtOptions);
builder.Services.AddScoped<IJwtService, JwtService>();

builder.Services.AddAuthentication(options =>
{{
    options.DefaultAuthenticateScheme = JwtBearerDefaults.AuthenticationScheme;
    options.DefaultChallengeScheme = JwtBearerDefaults.AuthenticationScheme;
}})
.AddJwtBearer(options =>
{{
    options.TokenValidationParameters = new TokenValidationParameters
    {{
        ValidateIssuer = true,
        ValidateAudience = true,
        ValidateLifetime = true,
        ValidateIssuerSigningKey = true,
        ValidIssuer = jwtOptions.Issuer,
        ValidAudience = jwtOptions.Audience,
        IssuerSigningKey = new SymmetricSecurityKey(Encoding.UTF8.GetBytes(jwtOptions.SecretKey))
    }};
}});

// Controllers
builder.Services.AddControllers();

// Swagger
builder.Services.AddEndpointsApiExplorer();
builder.Services.AddSwaggerGen(c =>
{{
    c.AddSecurityDefinition("Bearer", new Microsoft.OpenApi.Models.OpenApiSecurityScheme
    {{
        Name = "Authorization",
        Type = Microsoft.OpenApi.Models.SecuritySchemeType.Http,
        Scheme = "bearer",
        BearerFormat = "JWT",
        In = Microsoft.OpenApi.Models.ParameterLocation.Header,
        Description = "Enter your JWT token only (no 'Bearer' prefix needed)"
    }});
    c.AddSecurityRequirement(new Microsoft.OpenApi.Models.OpenApiSecurityRequirement
    {{
        {{
            new Microsoft.OpenApi.Models.OpenApiSecurityScheme
            {{
                Reference = new Microsoft.OpenApi.Models.OpenApiReference
                {{
                    Type = Microsoft.OpenApi.Models.ReferenceType.SecurityScheme,
                    Id = "Bearer"
                }}
            }},
            Array.Empty<string>()
        }}
    }});
}});

var app = builder.Build();

if (app.Environment.IsDevelopment())
{{
    app.UseSwagger();
    app.UseSwaggerUI();
}}

if (!app.Environment.IsDevelopment())
{{
    app.UseHttpsRedirection();
}}
app.UseAuthentication();
app.UseAuthorization();
app.MapControllers();

using (var scope = app.Services.CreateScope())
{{
    var db = scope.ServiceProvider.GetRequiredService<DataContext>();
    db.Database.EnsureCreated();

    var roleManager = scope.ServiceProvider.GetRequiredService<RoleManager<Role>>();
    var userManager = scope.ServiceProvider.GetRequiredService<UserManager<User>>();
    await {project}.Persistence.Seeders.RoleSeeder.SeedAsync(roleManager);
    await {project}.Persistence.Seeders.UserSeeder.SeedAsync(userManager);
}}

app.Run();
"""

    file_path = base / "API" / "Program.cs"
    file_path.write_text(content)
    print("  [+] API/Program.cs")