using PriceTrend.Services;
using PriceTrend.Data;
using Microsoft.EntityFrameworkCore;
using Microsoft.AspNetCore.Authentication.Cookies;

var builder = WebApplication.CreateBuilder(args);

// =========================================================
// 1. 服務註冊區 (Services Configuration)
// =========================================================
builder.Services.AddControllersWithViews();
builder.Services.AddHttpClient();
builder.Services.AddAppServices();

// 註冊資料庫 (使用 AppDbContext 與 PriceTrend 連線字串，並加上連線重試機制避免啟動逾時)
builder.Services.AddDbContext<AppDbContext>(options =>
    options.UseSqlServer(
        builder.Configuration.GetConnectionString("PriceTrend"),
        sqlServerOptionsAction: sqlOptions =>
        {
            sqlOptions.EnableRetryOnFailure(
                maxRetryCount: 5,
                maxRetryDelay: TimeSpan.FromSeconds(10),
                errorNumbersToAdd: null);
        }));

builder.Services.AddScoped<IComparisonService, ComparisonService>();

// 補上 Cookie 身分驗證服務
builder.Services.AddAuthentication(CookieAuthenticationDefaults.AuthenticationScheme)
    .AddCookie(options =>
    {
        options.LoginPath = "/Account/Login"; // 若未登入，自動導向登入頁面
        options.ExpireTimeSpan = TimeSpan.FromHours(1); // 設定登入狀態保留 1 小時
    });

var app = builder.Build();

// =========================================================
// 2. HTTP 管道與中間件配置 (Middleware Pipeline)
// =========================================================
if (!app.Environment.IsDevelopment())
{
    app.UseExceptionHandler("/Home/Error");
    app.UseHsts();
}

app.UseHttpsRedirection();
app.UseRouting();

// 順序很重要：先驗證身分，再授權
app.UseAuthentication();
app.UseAuthorization();

app.MapStaticAssets();

// =========================================================
// 3. 路由配置區 (Routing Configuration)
// =========================================================
app.MapControllerRoute(
    name: "default",
    pattern: "{controller=Home}/{action=Index}/{id?}")
    .WithStaticAssets();

app.Run();