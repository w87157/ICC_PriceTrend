using Microsoft.AspNetCore.Mvc;
using PriceTrend.Services;

namespace PriceTrend.Controllers
{
    public class ProductController : Controller
    {
        private readonly IComparisonService _comparisonService;

        public ProductController(IComparisonService comparisonService)
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
