using Microsoft.EntityFrameworkCore;
using PriceTrend.Models;
using PriceTrend.Models.Product;

namespace PriceTrend.Data
{
    public class AppDbContext : DbContext
    {
        public AppDbContext(DbContextOptions<AppDbContext> options) : base(options) { }

        public DbSet<User> Users { get; set; }
        public DbSet<Item> Items { get; set; }
        public DbSet<Category> Categories { get; set; }
        public DbSet<Platform> Platforms { get; set; }
        public DbSet<PlatformItem> PlatformItems { get; set; }

        // 🌟 加上這段，明確宣告各個資料表的主鍵，徹底根除主鍵對應錯誤
        protected override void OnModelCreating(ModelBuilder modelBuilder)
        {
            base.OnModelCreating(modelBuilder);

            modelBuilder.Entity<Category>().HasKey(c => c.CategoryGuid);
            modelBuilder.Entity<Item>().HasKey(i => i.ItemGuid);
            modelBuilder.Entity<Platform>().HasKey(p => p.PlatformGuid);

            // 💡 如果您的 PlatformItem 主鍵名稱不是 PlatformItemGuid，請把它改成您實際寫的屬性名稱（例如 Id）
            modelBuilder.Entity<PlatformItem>().HasKey(pi => pi.PlatformItemGuid);
        }
    }
}