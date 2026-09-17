using System.ComponentModel.DataAnnotations; // 1. 確保有這行
namespace PriceTrend.Models.Product
{
    public class Item
    {
        [Key] // 2. 加上這行
        public Guid ItemGuid { get; set; }
        public Guid CategoryGuid { get; set; }
        public string ItemName { get; set; }
        public string Brand { get; set; }
        public string Model { get; set; }
        public string MainImageUrl { get; set; }
        public decimal? LowestPrice { get; set; }
        public decimal? HighestPrice { get; set; }
        public decimal? HistoricalLowestPrice { get; set; }
        public byte Status { get; set; }
        public DateTime UpdatedAt { get; set; }
        public DateTime CreatedAt { get; set; }
        public Category Category { get; set; }
    }
}