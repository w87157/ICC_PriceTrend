using Microsoft.AspNetCore.Connections;
using Microsoft.Data.SqlClient;
using PriceTrend.Data;
using PriceTrend.Models.Product;


namespace PriceTrend.Services
{
    public class ComparisonService : IComparisonService
    {

        public readonly IConfiguration _configuration;

        public ComparisonService(IConfiguration configuration)
        {
            _configuration = configuration;
        }

        public List<PlatformItem> GetAllProducts()

        {
            List<PlatformItem> Platformitems = new List<PlatformItem>();
            var connectionString = _configuration.GetConnectionString("DefaultConnection");

            if (string.IsNullOrWhiteSpace(connectionString))
            {
                throw new InvalidOperationException("查無字串");
            }

            const string sql = """
            select

            PlatformItemName,
            ItemUrl,
            CurrentPrice

            from PlatformItems
            order by CurrentPrice
            """;

            using var connection = new SqlConnection(connectionString);
            connection.Open();
            using var command = new SqlCommand(sql, connection);

            var reader = command.ExecuteReader();
            while (reader.Read()) {
                Platformitems.Add(new PlatformItem
                {
                    PlatformItemName = reader.GetString(reader.GetOrdinal("PlatformItemName")),
                    ItemUrl = reader.GetString(reader.GetOrdinal("ItemUrl")),
                    CurrentPrice = reader.GetDecimal(reader.GetOrdinal("CurrentPrice"))
                });
                
            }return Platformitems;
        }

    }
}