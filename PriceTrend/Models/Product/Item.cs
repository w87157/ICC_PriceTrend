namespace PriceTrend.Models.Product
{
    public class Item
    {
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
        // Navigation Property
        public Category Category { get; set; }
    }
}