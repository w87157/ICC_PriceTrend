from csv_loader import load_all_csv
from normalizer import normalize_product_name
from product_analyzer import parse_product
from product_matcher import group_products
from product_repository import save_to_database


def main():
    print("========================================")
    print("        PriceTrend 商品資料處理")
    print("========================================")

    # =========================================================
    # 1. 讀取所有平台 CSV
    # =========================================================
    print("\n[1/5] 讀取 CSV")

    raw_products = load_all_csv()

    if not raw_products:
        print("沒有讀取到任何商品資料。")
        return

    print(f"共讀取 {len(raw_products)} 筆商品")

    # =========================================================
    # 2. 商品名稱正規化
    # =========================================================
    print("\n[2/5] 商品名稱正規化")

    normalized_products = []

    for product in raw_products:

        product.product_name = normalize_product_name(
            product.product_name
        )

        normalized_products.append(product)

    print(f"完成正規化：{len(normalized_products)} 筆")

    # =========================================================
    # 3. 商品規格分析
    # =========================================================
    print("\n[3/5] 商品規格分析")

    analyzed_products = []

    for product in normalized_products:

        standard_product = parse_product(
            product.product_name
        )

        # 無法解析的商品跳過
        if standard_product is None:
            print(
                f"無法分析商品：{product.product_name}"
            )
            continue
        
        analyzed_products.append({
            "standard_product": standard_product,
            "raw_product": product
        })

    print(f"完成分析：{len(analyzed_products)} 筆")

    # =========================================================
    # 4. 商品比對與分組
    # =========================================================
    print("\n[4/5] 商品比對與分組")

    product_groups = group_products(
        analyzed_products
    )

    print(f"完成分組：{len(product_groups)} 組")

    # =========================================================
    # 5. 儲存至 SQL Server
    # =========================================================
    print("\n[5/5] 儲存至 SQL Server")

    save_to_database(product_groups)

    print("\n========================================")
    print("        商品資料處理完成")
    print("========================================")


if __name__ == "__main__":
    main()