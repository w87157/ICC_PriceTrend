using Microsoft.AspNetCore.Mvc;
using PriceTrend.Services;

namespace PriceTrend.Controllers
{
    public class ShopController : Controller
    {
        // 若使用 /Shop 預設路徑，轉到 Shop action
        private readonly ComparisonService _comparisonService;

        public ShopController(ComparisonService comparisonService)
        {
            _comparisonService = comparisonService;
        }

        public IActionResult Index()
        {
            var products = _comparisonService.GetAllProducts();

            return View(products);
        }
    }
}
