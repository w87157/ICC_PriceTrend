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

        public async Task<List<SearchResultViewModel>> SearchAsync(string? keyword, string? category)
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

            await using var connection = new SqlConnection(connectionString);
            await connection.OpenAsync();
            await using var command = new SqlCommand(sql, connection);

            var searchKeyword = keyword?.Trim() ?? "";
            command.Parameters.AddWithValue("@Keyword", searchKeyword);
            command.Parameters.AddWithValue("@KeywordPattern", $"%{searchKeyword}%");

            await using var reader = await command.ExecuteReaderAsync();
            while (await reader.ReadAsync())
            {
                results.Add(new SearchResultViewModel
                {
                    ItemGuid = reader.GetGuid(reader.GetOrdinal("ItemGuid")),
                    ItemName = reader.GetString(reader.GetOrdinal("ItemName")),
                    Brand = reader.IsDBNull(reader.GetOrdinal("Brand")) ? null : reader.GetString(reader.GetOrdinal("Brand")),
                    Model = reader.IsDBNull(reader.GetOrdinal("Model")) ? null : reader.GetString(reader.GetOrdinal("Model")),
                    MainImageUrl = reader.IsDBNull(reader.GetOrdinal("MainImageUrl")) ? null : reader.GetString(reader.GetOrdinal("MainImageUrl"))
                });
            }

            return results;
        }
    }
}