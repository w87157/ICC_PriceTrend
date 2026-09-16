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

        public IActionResult Index(string? keyword, string? sort, int page=1)
        {
            int pageSize = 20;

            var products = _searchService.Search(keyword);

            // 價格排序
            switch (sort)
            {
                case "price_asc":
                    products = products
                        .OrderBy(x => decimal.TryParse(x.LowestPrice, out var p) ? p:
                        decimal.MaxValue)
                        .ToList();
                    break;
                case "price_desc":
                    products = products
                        .OrderByDescending(x => decimal.TryParse(x.LowestPrice, out var p) ? p : 0)
                        .ToList();
                    break;
            }

            int totalCount = products.Count;

            var pageProducts = products
                .Skip((page - 1) * pageSize)
                .Take(pageSize)
                .ToList();

            ViewBag.CurrentPage = page;

            ViewBag.TotalPages =
                (int)Math.Ceiling(totalCount / (double)pageSize);

            ViewBag.Keyword = keyword;
            ViewBag.Sort = sort;

            return View(pageProducts);
        }
    }
}
