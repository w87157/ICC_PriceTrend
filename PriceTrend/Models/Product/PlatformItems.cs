using System.ComponentModel.DataAnnotations;
using System.ComponentModel.DataAnnotations.Schema;

namespace PriceTrend.Models.Product
{
    public class PlatformItem
    {
        [Key]
        public Guid PlatformItemGuid { get; set; }

        public Guid ItemGuid { get; set; }

        public Guid PlatformGuid { get; set; }

        public string? OuterItemId { get; set; }

        public string? PlatformItemName { get; set; }

        public string ItemUrl { get; set; }

        public decimal CurrentPrice { get; set; }

        public byte StockStatus { get; set; }

        public DateTime LastScrapedAt { get; set; }

        // Navigation Property
        [ForeignKey(nameof(ItemGuid))]
        public Item Item { get; set; }

        [ForeignKey(nameof(PlatformGuid))]
        public Platform Platform { get; set; }
    }
}