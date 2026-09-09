using Microsoft.Data.SqlClient;
using PriceTrend.Models.Product;

namespace PriceTrend.Services
{
    public class SearchService
    {
        private readonly IConfiguration _configuration;

        public SearchService (IConfiguration configuration)
        {
            _configuration = configuration;
        }

        public List<SearchResultViewModel> Search(string? keyword)
        {
            var results = new List<SearchResultViewModel>();
            var connectionString = _configuration.GetConnectionString("PriceTrend");

            if (string.IsNullOrWhiteSpace(connectionString))
            {
                throw new InvalidOperationException("找不到 PriceTrend 資料庫連線字串。");
            }

            const string sql = """
                SELECT
                    ItemGuid, ItemName, Brand, Model, MainImageUrl, LowestPrice, HighestPrice
                FROM Items
                WHERE
                    @Keyword = ''
                    OR ItemName LIKE @KeywordPattern 
                    OR Brand LIKE @KeywordPattern
                    OR Model LIKE @KeywordPattern
                ORDER BY ItemName;
            """;

            using var connection = new SqlConnection(connectionString);
            connection.Open();
            using var command = new SqlCommand(sql, connection);

            var searchKeyword = keyword?.Trim() ?? "";
            command.Parameters.AddWithValue("@Keyword", searchKeyword);
            command.Parameters.AddWithValue("@KeywordPattern", $"%{searchKeyword}%");

            using var reader = command.ExecuteReader();
            while (reader.Read())
            {
                results.Add(new SearchResultViewModel
                {
                    ItemGuid = reader.GetGuid(reader.GetOrdinal("ItemGuid")),
                    ItemName = reader.GetString(reader.GetOrdinal("ItemName")),
                    Brand = reader.IsDBNull(reader.GetOrdinal("Brand")) ? null : reader.GetString(reader.GetOrdinal("Brand")),
                    Model = reader.IsDBNull(reader.GetOrdinal("Model")) ? null : reader.GetString(reader.GetOrdinal("Model")),
                    MainImageUrl = reader.IsDBNull(reader.GetOrdinal("MainImageUrl")) ? null : reader.GetString(reader.GetOrdinal("MainImageUrl")),
                    LowestPrice = reader.IsDBNull(reader.GetOrdinal("LowestPrice")) ? null : reader.GetString(reader.GetOrdinal("LowestPrice")),
                    HighestPrice = reader.IsDBNull(reader.GetOrdinal("HighestPrice")) ? null : reader.GetString(reader.GetOrdinal("HighestPrice"))
                });
            }

            return results;
        }
    }
}