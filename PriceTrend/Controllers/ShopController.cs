using Microsoft.AspNetCore.Mvc;
using PriceTrend.Services;
using System.Linq;

namespace PriceTrend.Controllers
{
    public class ShopController : Controller
    {
        private readonly SearchService _searchService;

        public ShopController(SearchService searchService)
        {
            _searchService = searchService;
        }

        public IActionResult Index(string? keyword, int page=1)
        {
            int pageSize = 60;

            var products = _searchService.Search(keyword);

            int totalCount = products.Count;

            var pageProducts = products
                .Skip((page - 1) * pageSize)
                .Take(pageSize)
                .ToList();

            ViewBag.CurrentPage = page;

            ViewBag.TotalPages =
                (int)Math.Ceiling(totalCount / (double)pageSize);

            ViewBag.Keyword = keyword;

            return View(pageProducts);
        }
    }
}
