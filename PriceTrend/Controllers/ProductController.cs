using Microsoft.AspNetCore.Mvc;
using PriceTrend.Services;
using PriceTrend.Models.Product;

namespace PriceTrend.Controllers
{
    public class ProductController : Controller
    {
        private readonly IComparisonService _comparisonService;
        private readonly SearchService _searchService;

        public ProductController(IComparisonService comparisonService, SearchService searchService)
        {
            _comparisonService = comparisonService;
            _searchService = searchService;
        }

        public IActionResult Index()
        {
            var products = _comparisonService.GetAllProducts();

            return View(products);
        }
        public IActionResult Single(Guid id)
        {
            var product = _searchService.GetProductDetail(id);

            if (product == null)
            {
                return NotFound();
            }
            return View(product);
        }
    }
}
