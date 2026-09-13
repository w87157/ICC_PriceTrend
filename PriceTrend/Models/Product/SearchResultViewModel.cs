namespace PriceTrend.Models.Product
{
    public class SearchResultViewModel
    {
        public Guid ItemGuid { get; set; }                      // 商品唯一識別碼
        public string ItemName { get; set; } = string.Empty;   // 商品名稱
        public string? Brand { get; set; }                      // 品牌名稱
        public string? Model { get; set; }                      // 商品型號
        public string? MainImageUrl { get; set; }               // 商品圖片 URL
        public string? LowestPrice { get; set; }                // 當前商品最低價
        public string? HighestPrice { get; set; }               // 當前商品最高價
    }
}

