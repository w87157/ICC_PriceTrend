using System.ComponentModel.DataAnnotations;
using System.ComponentModel.DataAnnotations.Schema;

namespace PriceTrend.Models.Product
{
    public class Platform
    {
        [Key]
        public Guid PlatformGuid { get; set; }

        public string PlatformName { get; set; }

        public string? BaseUrl { get; set; }

        public string? LogoUrl { get; set; }

        public byte Status { get; set; }

        public DateTime CreatedAt { get; set; }

        // 一個平台可對應多個商品
        public ICollection<PlatformItem> PlatformItems { get; set; }
            = new List<PlatformItem>();
    }
}