using Microsoft.AspNetCore.Mvc;
using PriceTrend.Services;

namespace PriceTrend.Controllers
{
    public class ShopController : Controller
    {
        private readonly SearchService _searchService;

        public ShopController(SearchService searchService)
        {
            _searchService = searchService;
        }

        public IActionResult Index(string? keyword)
        {
            var products = _searchService.Search(keyword);

            return View(products);
        }
    }
}
