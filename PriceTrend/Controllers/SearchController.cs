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
        public async Task<IActionResult> Index(string? keyword)
        {
            var result = await _searchService.SearchAsync(keyword);

            return View(result);
        }
    }
}
