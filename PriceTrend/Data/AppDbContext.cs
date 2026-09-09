using PriceTrend.Models.Product;
using System.Runtime.InteropServices;
using Microsoft.EntityFrameworkCore;

namespace PriceTrend.Data
{
    public class AppDbContext : DbContext
    {
        public AppDbContext(DbContextOptions<AppDbContext> options)
            : base(options)
        {
        }

        public DbSet<Item> Items { get; set; }

        public DbSet<Category> Categories { get; set; }

        public DbSet<Platform> Platforms { get; set; }

        public DbSet<PlatformItem> PlatformItems { get; set; }
    }
}