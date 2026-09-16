using Microsoft.EntityFrameworkCore;
using PriceTrend.Models;

namespace PriceTrend.Data
{
    // 將類別名稱改成 ApplicationDbContext
    public class ApplicationDbContext : DbContext
    {
        public ApplicationDbContext(DbContextOptions<ApplicationDbContext> options)
            : base(options)
        {
        }

        public DbSet<User> Users { get; set; }
        public DbSet<PriceTrend.Models.Product.Item> Items { get; set; }
        public DbSet<PriceTrend.Models.Product.Category> Categories { get; set; }
        public DbSet<PriceTrend.Models.Product.Platform> Platforms { get; set; }
        public DbSet<PriceTrend.Models.Product.PlatformItem> PlatformItems { get; set; }
    }
}