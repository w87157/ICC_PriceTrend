using System;
using System.ComponentModel.DataAnnotations;

namespace PriceTrend.Models
{
    public class FavoriteItem
    {
        [Key]
        public Guid FavoriteItemGuid { get; set; }
        public int UserId { get; set; } // 或對應您的使用者 ID 型別
        public Guid ItemGuid { get; set; }
        public DateTime CreatedAt { get; set; } = DateTime.Now;
    }
}