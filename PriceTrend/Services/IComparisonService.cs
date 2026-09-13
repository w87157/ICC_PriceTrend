using PriceTrend.Models.Product;

namespace PriceTrend.Services
{
    public interface IComparisonService
    {
        List<PlatformItem> GetAllProducts();
    }
}