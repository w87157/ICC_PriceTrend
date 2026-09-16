using System;
using Microsoft.EntityFrameworkCore.Migrations;

#nullable disable

namespace PriceTrend.Migrations
{
    /// <inheritdoc />
    public partial class AddUsersTable : Migration
    {
        /// <inheritdoc />
        protected override void Up(MigrationBuilder migrationBuilder)
        {
            migrationBuilder.CreateTable(
                name: "Categories",
                columns: table => new
                {
                    CategoryGuid = table.Column<Guid>(type: "uniqueidentifier", nullable: false),
                    CategoryName = table.Column<string>(type: "nvarchar(max)", nullable: false)
                },
                constraints: table =>
                {
                    table.PrimaryKey("PK_Categories", x => x.CategoryGuid);
                });

            migrationBuilder.CreateTable(
                name: "Platforms",
                columns: table => new
                {
                    PlatformGuid = table.Column<Guid>(type: "uniqueidentifier", nullable: false),
                    PlatformName = table.Column<string>(type: "nvarchar(max)", nullable: false),
                    BaseUrl = table.Column<string>(type: "nvarchar(max)", nullable: true),
                    LogoUrl = table.Column<string>(type: "nvarchar(max)", nullable: true),
                    Status = table.Column<byte>(type: "tinyint", nullable: false),
                    CreatedAt = table.Column<DateTime>(type: "datetime2", nullable: false)
                },
                constraints: table =>
                {
                    table.PrimaryKey("PK_Platforms", x => x.PlatformGuid);
                });

            migrationBuilder.CreateTable(
                name: "Users",
                columns: table => new
                {
                    Id = table.Column<int>(type: "int", nullable: false)
                        .Annotation("SqlServer:Identity", "1, 1"),
                    Email = table.Column<string>(type: "nvarchar(max)", nullable: true),
                    Password = table.Column<string>(type: "nvarchar(max)", nullable: true),
                    FirstName = table.Column<string>(type: "nvarchar(max)", nullable: true),
                    LastName = table.Column<string>(type: "nvarchar(max)", nullable: true),
                    PhoneNumber = table.Column<string>(type: "nvarchar(max)", nullable: true)
                },
                constraints: table =>
                {
                    table.PrimaryKey("PK_Users", x => x.Id);
                });

            migrationBuilder.CreateTable(
                name: "Items",
                columns: table => new
                {
                    ItemGuid = table.Column<Guid>(type: "uniqueidentifier", nullable: false),
                    CategoryGuid = table.Column<Guid>(type: "uniqueidentifier", nullable: false),
                    ItemName = table.Column<string>(type: "nvarchar(max)", nullable: false),
                    Brand = table.Column<string>(type: "nvarchar(max)", nullable: false),
                    Model = table.Column<string>(type: "nvarchar(max)", nullable: false),
                    MainImageUrl = table.Column<string>(type: "nvarchar(max)", nullable: false),
                    LowestPrice = table.Column<decimal>(type: "decimal(18,2)", nullable: true),
                    HighestPrice = table.Column<decimal>(type: "decimal(18,2)", nullable: true),
                    HistoricalLowestPrice = table.Column<decimal>(type: "decimal(18,2)", nullable: true),
                    Status = table.Column<byte>(type: "tinyint", nullable: false),
                    UpdatedAt = table.Column<DateTime>(type: "datetime2", nullable: false),
                    CreatedAt = table.Column<DateTime>(type: "datetime2", nullable: false),
                    CategoryGuid1 = table.Column<Guid>(type: "uniqueidentifier", nullable: false)
                },
                constraints: table =>
                {
                    table.PrimaryKey("PK_Items", x => x.ItemGuid);
                    table.ForeignKey(
                        name: "FK_Items_Categories_CategoryGuid1",
                        column: x => x.CategoryGuid1,
                        principalTable: "Categories",
                        principalColumn: "CategoryGuid",
                        onDelete: ReferentialAction.Cascade);
                });

            migrationBuilder.CreateTable(
                name: "PlatformItems",
                columns: table => new
                {
                    PlatformItemGuid = table.Column<Guid>(type: "uniqueidentifier", nullable: false),
                    ItemGuid = table.Column<Guid>(type: "uniqueidentifier", nullable: false),
                    PlatformGuid = table.Column<Guid>(type: "uniqueidentifier", nullable: false),
                    OuterItemId = table.Column<string>(type: "nvarchar(max)", nullable: true),
                    PlatformItemName = table.Column<string>(type: "nvarchar(max)", nullable: true),
                    ItemUrl = table.Column<string>(type: "nvarchar(max)", nullable: false),
                    CurrentPrice = table.Column<decimal>(type: "decimal(18,2)", nullable: false),
                    StockStatus = table.Column<byte>(type: "tinyint", nullable: false),
                    LastScrapedAt = table.Column<DateTime>(type: "datetime2", nullable: false)
                },
                constraints: table =>
                {
                    table.PrimaryKey("PK_PlatformItems", x => x.PlatformItemGuid);
                    table.ForeignKey(
                        name: "FK_PlatformItems_Items_ItemGuid",
                        column: x => x.ItemGuid,
                        principalTable: "Items",
                        principalColumn: "ItemGuid",
                        onDelete: ReferentialAction.Cascade);
                    table.ForeignKey(
                        name: "FK_PlatformItems_Platforms_PlatformGuid",
                        column: x => x.PlatformGuid,
                        principalTable: "Platforms",
                        principalColumn: "PlatformGuid",
                        onDelete: ReferentialAction.Cascade);
                });

            migrationBuilder.CreateIndex(
                name: "IX_Items_CategoryGuid1",
                table: "Items",
                column: "CategoryGuid1");

            migrationBuilder.CreateIndex(
                name: "IX_PlatformItems_ItemGuid",
                table: "PlatformItems",
                column: "ItemGuid");

            migrationBuilder.CreateIndex(
                name: "IX_PlatformItems_PlatformGuid",
                table: "PlatformItems",
                column: "PlatformGuid");
        }

        /// <inheritdoc />
        protected override void Down(MigrationBuilder migrationBuilder)
        {
            migrationBuilder.DropTable(
                name: "PlatformItems");

            migrationBuilder.DropTable(
                name: "Users");

            migrationBuilder.DropTable(
                name: "Items");

            migrationBuilder.DropTable(
                name: "Platforms");

            migrationBuilder.DropTable(
                name: "Categories");
        }
    }
}
