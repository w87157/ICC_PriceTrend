namespace PriceTrend.Models.Product
    {
    public class ProductDetailViewModel
    {
        public Guid ItemGuid { get; set; }
        public string ItemName { get; set; } = "";
        public string? Brand { get; set; }
        public string? Model { get; set; }
        public string? MainImageUrl { get; set; }
        public string? LowestPrice { get; set; }
        public string? HighestPrice { get; set; }
        public List<PlatformPriceViewModel> Prices { get; set; }
            = new();
        public string PlatformName { get; internal set; }
        public string? LogoUrl { get; internal set; }
        public string? CurrentPrice { get; internal set; }
        public string? ItemUrl { get; internal set; }
    }

    public class PlatformPriceViewModel
    {
        public string PlatformName { get; set; } = "";
        public string PlatformLogo { get; set; } = "";
        public string Price { get; set; } = "";
        public string ItemUrl { get; set; } = "";
    }
}

