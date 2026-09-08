namespace PriceTrend.Models.Product
{
    public class Category
    {
        public Guid CategoryGuid { get; set; }

        public string CategoryName { get; set; }

        public ICollection<Item> Items { get; set; }
    }
}