from pathlib import Path
from stackforge import ui


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
        "API": f"""using {project}.API.Interface;
using {project}.API.Options;
using {project}.API.Services;
using {project}.Domain.Entities.Identity;
using {project}.Persistence;
using Microsoft.AspNetCore.Authentication.JwtBearer;
using Microsoft.AspNetCore.Authorization;
using Microsoft.AspNetCore.Identity;
using Microsoft.IdentityModel.Tokens;
using Microsoft.OpenApi.Models;
using System.Text;
using System.Text.Json.Serialization;

namespace {project}.API
{{
    public static class ConfigureServices
    {{
        public const string CorsPolicy = "Cors";

        public static IServiceCollection AddApiServices(this IServiceCollection services, IConfiguration configuration)
        {{
            services.Configure<JwtOptions>(configuration.GetSection("Jwt"));
            var jwtOptions = new JwtOptions();
            configuration.GetSection("Jwt").Bind(jwtOptions);

            services.AddControllers()
                .AddJsonOptions(options => options.JsonSerializerOptions.Converters.Add(new JsonStringEnumConverter()));

            services.AddEndpointsApiExplorer();

            services.AddSwaggerGen(config =>
            {{
                config.AddSecurityDefinition("Bearer", new OpenApiSecurityScheme
                {{
                    Name = "Authorization",
                    Type = SecuritySchemeType.Http,
                    Scheme = "bearer",
                    BearerFormat = "JWT",
                    In = ParameterLocation.Header,
                    Description = "Enter your JWT token only (no 'Bearer' prefix needed)"
                }});

                config.AddSecurityRequirement(new OpenApiSecurityRequirement
                {{
                    {{
                        new OpenApiSecurityScheme
                        {{
                            Reference = new OpenApiReference
                            {{
                                Type = ReferenceType.SecurityScheme,
                                Id = "Bearer"
                            }}
                        }},
                        Array.Empty<string>()
                    }}
                }});
            }});

            // Browser origins allowed to call the API. Format: scheme + host (+ port if non-default), no trailing slash.
            // Only add frontends you own: an allowed origin's scripts can call this API from a visitor's browser.
            // Bearer tokens travel in the Authorization header, so credentials (cookies) are not allowed.
            services.AddCors(options =>
            {{
                options.AddPolicy(CorsPolicy, policy =>
                {{
                    policy.AllowAnyMethod()
                        .AllowAnyHeader()
                        .WithExposedHeaders("WWW-Authenticate", "Retry-After")
                        .WithOrigins(
                            "http://localhost:3000"
                            );
                }});
            }});

            services.AddIdentity<User, Role>(options =>
            {{
                options.Password.RequireDigit = true;
                options.Password.RequireLowercase = true;
                options.Password.RequireUppercase = true;
                options.Password.RequireNonAlphanumeric = true;
                options.Password.RequiredLength = 8;
            }})
            .AddEntityFrameworkStores<DataContext>()
            .AddDefaultTokenProviders();

            services.AddAuthentication(options =>
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

            // Deny by default: endpoints without an explicit policy require an authenticated user.
            // Public endpoints must opt out with [AllowAnonymous].
            services.AddAuthorization(options =>
            {{
                options.FallbackPolicy = new AuthorizationPolicyBuilder()
                    .RequireAuthenticatedUser()
                    .Build();
            }});

            //Scopes
            services.AddScoped<IJwtService, JwtService>();

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
    ui.file_created(f"{layer}/ConfigureServices.cs")


def generate_program_cs(base: Path, project: str):
    content = f"""using {project}.API;
using {project}.Application;
using {project}.Domain.Entities.Identity;
using {project}.Infrastructure;
using {project}.Persistence;
using Microsoft.AspNetCore.Identity;

var builder = WebApplication.CreateBuilder(args);

// Layer services
builder.Services.AddApplicationServices();
builder.Services.AddInfrastructureServices();
builder.Services.AddPersistenceServices(builder.Configuration);
builder.Services.AddApiServices(builder.Configuration);

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
app.UseRouting();
app.UseCors({project}.API.ConfigureServices.CorsPolicy);
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
    ui.file_created("API/Program.cs")
