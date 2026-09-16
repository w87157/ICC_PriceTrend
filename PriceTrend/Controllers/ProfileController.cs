using Microsoft.AspNetCore.Authorization;
using Microsoft.AspNetCore.Mvc;
using Microsoft.EntityFrameworkCore;
using PriceTrend.Data;
using System.Threading.Tasks;

namespace PriceTrend.Controllers
{
    [Authorize] // 強制要求必須登入才能存取
    public class ProfileController : Controller
    {
        private readonly AppDbContext _context;

        public ProfileController(AppDbContext context)
        {
            _context = context;
        }

        // 1. 顯示會員中心畫面
        public async Task<IActionResult> Index()
        {
            var userEmail = User.Identity?.Name;

            if (string.IsNullOrEmpty(userEmail))
            {
                return RedirectToAction("Login", "Account");
            }

            var user = await _context.Users.FirstOrDefaultAsync(u => u.Email == userEmail);

            if (user == null)
            {
                return NotFound("找不到使用者資料。");
            }

            return View(user);
        }

        // 2. 接收並處理「更新個人資料」
        [HttpPost]
        public async Task<IActionResult> UpdateProfile(string firstName, string lastName, string phoneNumber)
        {
            var userEmail = User.Identity?.Name;
            var user = await _context.Users.FirstOrDefaultAsync(u => u.Email == userEmail);

            if (user != null)
            {
                // 更新資料
                user.FirstName = firstName;
                user.LastName = lastName;
                user.PhoneNumber = phoneNumber;

                await _context.SaveChangesAsync(); // 儲存進資料庫

                // 傳遞成功訊息給畫面
                TempData["SuccessMessage"] = "個人資料已成功更新！";
            }

            // 重新導向回會員中心，並利用 # 標記讓 JavaScript 自動切換到個人資料頁籤
            return Redirect(Url.Action("Index") + "#v-pills-profile");
        }

        // 3. 接收並處理「修改密碼」
        [HttpPost]
        public async Task<IActionResult> ChangePassword(string currentPassword, string newPassword)
        {
            var userEmail = User.Identity?.Name;
            var user = await _context.Users.FirstOrDefaultAsync(u => u.Email == userEmail);

            if (user != null)
            {
                // 比對資料庫裡的舊密碼是否跟使用者輸入的一樣
                if (user.Password == currentPassword)
                {
                    user.Password = newPassword; // 實務上正式上線會做加密，目前以明文示範
                    await _context.SaveChangesAsync();

                    TempData["SuccessMessage"] = "密碼修改成功！下次登入請使用新密碼。";
                }
                else
                {
                    TempData["ErrorMessage"] = "目前的密碼輸入錯誤，請重新確認！";
                }
            }

            // 重新導向回會員中心，並利用 # 標記讓 JavaScript 自動切換到帳號設定頁籤
            return Redirect(Url.Action("Index") + "#v-pills-settings");
        }
    }
}