using System.ComponentModel.DataAnnotations; // 1. 務必引入這個命名空間

namespace PriceTrend.Models.Product
{
    public class Category
    {
        [Key] // 2. 加上這行，明確宣告這是主鍵
        public Guid CategoryGuid { get; set; }

        public string CategoryName { get; set; }

        public ICollection<Item> Items { get; set; }
    }
}