using PriceTrend.Services;

var builder = WebApplication.CreateBuilder(args);

// =========================================================
// 1. 服務註冊區 (Services Configuration)
// =========================================================
builder.Services.AddControllersWithViews();
builder.Services.AddHttpClient();
builder.Services.AddAppServices();

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
app.UseAuthentication();
app.UseAuthorization();
app.MapStaticAssets();

// =========================================================
// 3. 路由配置區 (Routing Configuration)
// =========================================================
// 後臺路由
app.MapControllerRoute(
    name: "areas",
    pattern: "{area:exists}/{controller=Dashboard}/{action=Index}/{id?}")
    .WithStaticAssets();

// 前台路由
app.MapControllerRoute(
    name: "default",
    pattern: "{controller=Home}/{action=Index}/{id?}")
    .WithStaticAssets();


app.Run();
