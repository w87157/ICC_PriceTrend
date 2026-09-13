using Microsoft.AspNetCore.Mvc;
using PriceTrend.Services;

namespace PriceTrend.Controllers
{
    public class SearchController : Controller
    {
        private readonly SearchService _searchService;

        public SearchController(SearchService searchService)
        {
            _searchService = searchService;
        }

        [HttpGet]
        public IActionResult Index(string keyword)
        {
            if (string.IsNullOrWhiteSpace(keyword))
            {
                return RedirectToAction("Index", "Shop");
            }

            return RedirectToAction("Index", "Shop", new { keyword = keyword });
        }
    }
}
