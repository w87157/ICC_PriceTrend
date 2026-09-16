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
                    i.ItemGuid,
                    i.ItemName,
                    i.Brand,
                    i.Model,
                    i.MainImageUrl,
                    MIN(pi.CurrentPrice) AS LowestPrice,
                    MAX(pi.CurrentPrice) AS HighestPrice
                FROM Items i
                LEFT JOIN PlatformItems pi
                    ON i.ItemGuid = pi.ItemGuid
                WHERE
                    @Keyword = ''
                    OR i.ItemName LIKE @KeywordPattern
                    OR i.Brand LIKE @KeywordPattern
                    OR i.Model LIKE @KeywordPattern
                GROUP BY
                    i.ItemGuid,
                    i.ItemName,
                    i.Brand,
                    i.Model,
                    i.MainImageUrl
                ORDER BY i.ItemName;
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
                    LowestPrice = reader.IsDBNull(reader.GetOrdinal("LowestPrice")) ? null : reader.GetDecimal(reader.GetOrdinal("LowestPrice")).ToString(),
                    HighestPrice = reader.IsDBNull(reader.GetOrdinal("HighestPrice")) ? null : reader.GetDecimal(reader.GetOrdinal("HighestPrice")).ToString()
                });
            }

            return results;
        }
        public SearchResultViewModel? GetProductById(Guid itemGuid)
        {
            var connectionString =
                _configuration.GetConnectionString("PriceTrend");

            const string sql = """
        SELECT
            ItemGuid,
            ItemName,
            Brand,
            Model,
            MainImageUrl,
            LowestPrice,
            HighestPrice
        FROM Items
        WHERE ItemGuid = @ItemGuid
        """;

            using var connection =
                new SqlConnection(connectionString);

            connection.Open();

            using var command =
                new SqlCommand(sql, connection);

            command.Parameters.AddWithValue(
                "@ItemGuid",
                itemGuid);

            using var reader =
                command.ExecuteReader();

            if (reader.Read())
            {
                return new SearchResultViewModel
                {
                    ItemGuid =reader.GetGuid(reader.GetOrdinal("ItemGuid")),
                    ItemName =reader.GetString(reader.GetOrdinal("ItemName")),
                    Brand =reader.IsDBNull(reader.GetOrdinal("Brand"))? null: reader.GetString(reader.GetOrdinal("Brand")),
                    Model =reader.IsDBNull(reader.GetOrdinal("Model"))? null: reader.GetString(reader.GetOrdinal("Model")),
                    MainImageUrl =reader.IsDBNull(reader.GetOrdinal("MainImageUrl")) ? null : reader.GetString(
                                reader.GetOrdinal("MainImageUrl")),
                    LowestPrice =reader.IsDBNull(reader.GetOrdinal("LowestPrice")) ? null : reader.GetString(
                                reader.GetOrdinal("LowestPrice")),
                    HighestPrice = reader.IsDBNull(reader.GetOrdinal("HighestPrice")) ? null: reader.GetString(
                                reader.GetOrdinal("HighestPrice"))
                };
            }

            return null;
        }
        public ProductDetailViewModel? GetProductDetail(Guid itemGuid)
        {
            var connectionString = _configuration.GetConnectionString("PriceTrend");
            const string sql = """
                SELECT
                i.ItemGuid,
                i.ItemName,
                i.Brand,
                i.Model,
                i.MainImageUrl,
                p.PlatformName,
                p.LogoUrl,
                pi.CurrentPrice,
                pi.ItemUrl
            FROM Items i
            INNER JOIN PlatformItems pi
                ON i.ItemGuid = pi.ItemGuid
            INNER JOIN Platforms p
                ON pi.PlatformGuid = p.PlatformGuid
            WHERE i.ItemGuid = @ItemGuid
            """;
            using var connection = new SqlConnection(connectionString);
            connection.Open();
            using var command = new SqlCommand(sql, connection);
            command.Parameters.AddWithValue("@ItemGuid", itemGuid);
            using var reader = command.ExecuteReader();

            ProductDetailViewModel? model = null;
            while (reader.Read())
            {

                if (model == null)
                {
                    model = new ProductDetailViewModel
                    {
                        ItemGuid = reader.GetGuid(reader.GetOrdinal("ItemGuid")),
                        ItemName = reader.GetString(reader.GetOrdinal("ItemName")),
                        Brand = reader.IsDBNull(reader.GetOrdinal("Brand")) ? null : reader.GetString(reader.GetOrdinal("Brand")),
                        Model = reader.IsDBNull(reader.GetOrdinal("Model")) ? null : reader.GetString(reader.GetOrdinal("Model")),
                        MainImageUrl = reader.IsDBNull(reader.GetOrdinal("MainImageUrl")) ? null : reader.GetString(reader.GetOrdinal("MainImageUrl")),
                        PlatformName = reader.GetString(reader.GetOrdinal("PlatformName")),
                        LogoUrl = reader.IsDBNull(reader.GetOrdinal("LogoUrl")) ? null : reader.GetString(reader.GetOrdinal("LogoUrl")),
                        CurrentPrice = reader.IsDBNull(reader.GetOrdinal("CurrentPrice")) ? null : reader.GetDecimal(reader.GetOrdinal("CurrentPrice")).ToString(),
                        ItemUrl = reader.IsDBNull(reader.GetOrdinal("ItemUrl")) ? null : reader.GetString(reader.GetOrdinal("ItemUrl")),
                        Prices = new List<PlatformPriceViewModel>()
                    };
                }

                model.Prices.Add(new PlatformPriceViewModel
                {
                    PlatformName = reader.GetString(reader.GetOrdinal("PlatformName")),
                    PlatformLogo = reader.IsDBNull(reader.GetOrdinal("LogoUrl")) ? null : reader.GetString(reader.GetOrdinal("LogoUrl")),
                    Price = reader.IsDBNull(reader.GetOrdinal("CurrentPrice")) ? null : reader.GetDecimal(reader.GetOrdinal("CurrentPrice")).ToString("N0"),
                    ItemUrl = reader.IsDBNull(reader.GetOrdinal("ItemUrl")) ? null : reader.GetString(reader.GetOrdinal("ItemUrl"))
                });
            }
            return model;
        }
    }
}