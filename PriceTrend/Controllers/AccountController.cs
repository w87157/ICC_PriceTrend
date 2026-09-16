using Microsoft.AspNetCore.Authentication;
using Microsoft.AspNetCore.Authentication.Cookies;
using Microsoft.AspNetCore.Mvc;
using PriceTrend.Data;
using PriceTrend.Models;
using System.Security.Claims;

public class AccountController : Controller
{
    private readonly AppDbContext _context; // 這裡改為 AppDbContext

    // 透過「依賴注入」取得資料庫連線
    public AccountController(AppDbContext context) // 這裡改為 AppDbContext
    {
        _context = context;
    }

    [HttpGet]
    public IActionResult Register()
    {
        return View();
    }

    [HttpPost]
    public IActionResult Register(string firstName, string lastName, string email, string password)
    {
        // 1. 檢查信箱是否已存在資料庫
        if (_context.Users.Any(u => u.Email == email))
        {
            ViewBag.ErrorMessage = "這個電子郵件已經註冊過了！";
            return View();
        }

        // 2. 建立新會員並存入資料庫
        var newUser = new User
        {
            FirstName = firstName,
            LastName = lastName,
            Email = email,
            Password = password // 實務上上線前需加密，此處先以明文示範
        };

        _context.Users.Add(newUser);
        _context.SaveChanges();

        // 3. 註冊成功，導向登入頁
        return RedirectToAction("Login");
    }

    [HttpGet]
    public IActionResult Login()
    {
        return View();
    }

    [HttpPost]
    public async Task<IActionResult> Login(string email, string password)
    {
        // 1. 去資料庫尋找有沒有這組帳號密碼
        var user = _context.Users.FirstOrDefault(u => u.Email == email && u.Password == password);

        if (user != null)
        {
            // 2. 登入成功，發行 Cookie 憑證，系統會標記 User.Identity.IsAuthenticated = true
            var claims = new List<Claim>
            {
                new Claim(ClaimTypes.Name, user.Email),
                new Claim("FullName", $"{user.FirstName} {user.LastName}")
            };

            var claimsIdentity = new ClaimsIdentity(claims, CookieAuthenticationDefaults.AuthenticationScheme);
            await HttpContext.SignInAsync(CookieAuthenticationDefaults.AuthenticationScheme, new ClaimsPrincipal(claimsIdentity));

            return RedirectToAction("Index", "Home");
        }

        // 3. 登入失敗，退回登入頁並顯示錯誤
        ViewBag.ErrorMessage = "帳號或密碼錯誤！";
        return View();
    }

    public async Task<IActionResult> Logout()
    {
        // 登出並清除 Cookie
        await HttpContext.SignOutAsync(CookieAuthenticationDefaults.AuthenticationScheme);
        return RedirectToAction("Index", "Home");
    }
}