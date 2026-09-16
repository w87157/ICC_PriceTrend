import os
from datetime import datetime, timezone
from pathlib import Path

import pyodbc
from dotenv import load_dotenv

from product_matcher import is_same_existing_item

# ============================================================
# 讀取 .env
# ============================================================
BASE_DIR = Path(__file__).resolve().parent
load_dotenv(BASE_DIR / ".env")


# ============================================================
# SQL Server 連線設定
# ============================================================
DB_CONNECTION_STRING = (
    "DRIVER={ODBC Driver 18 for SQL Server};"
    f"SERVER={os.getenv('DB_SERVER')};"
    f"DATABASE={os.getenv('DB_DATABASE')};"
    "Trusted_Connection=yes;"
    "TrustServerCertificate=yes;"
)


# ============================================================
# 建立資料庫連線
# ============================================================
def get_db_connection():
    return pyodbc.connect(DB_CONNECTION_STRING)


# ============================================================
# 取得分類 CategoryGuid
# ============================================================
def get_category_guid(cursor, category_name):
    sql = """
        SELECT CategoryGuid
        FROM dbo.Categories
        WHERE CategoryName = ?
    """

    cursor.execute(sql, category_name)
    row = cursor.fetchone()

    if row is None:
        raise ValueError(f"找不到商品分類：{category_name}")

    return row[0]


# ============================================================
# 取得平台 PlatformGuid
# ============================================================
def get_platform_guid(cursor, platform_name):
    sql = """
        SELECT PlatformGuid
        FROM dbo.Platforms
        WHERE PlatformName = ?
    """

    cursor.execute(sql, platform_name)
    row = cursor.fetchone()

    if row is None:
        raise ValueError(f"找不到平台：{platform_name}")

    return row[0]


# ============================================================
# 依 Brand + Model 查詢既有 Items
# ============================================================
def find_existing_items(cursor, category_guid, brand, model):
    sql = """
        SELECT
            ItemGuid,
            CategoryGuid,
            ItemName,
            Brand,
            Model,
            MainImageUrl
        FROM dbo.Items
        WHERE CategoryGuid = ?
          AND Brand = ?
          AND Model = ?
    """

    cursor.execute(
        sql,
        category_guid,
        brand,
        model
    )

    rows = cursor.fetchall()

    items = []

    for row in rows:
        items.append({
            "ItemGuid": row[0],
            "CategoryGuid": row[1],
            "ItemName": row[2],
            "Brand": row[3],
            "Model": row[4],
            "MainImageUrl": row[5],
        })

    return items


# ============================================================
# 判斷是否可以使用既有 Items
# ============================================================
def find_matching_item(cursor, category_guid, standard_product):
    brand = standard_product.brand
    model = standard_product.model

    # Brand / Model 缺少任一項，不進行跨平台匹配
    if not brand or not model:
        return None

    candidates = find_existing_items(
        cursor,
        category_guid,
        brand,
        model
    )

    for item in candidates:
        if is_same_existing_item(standard_product, item):
            return item

    return None


# ============================================================
# 建立新的 Items
# ============================================================
def create_item(
    cursor,
    category_guid,
    item_name,
    brand,
    model,
    image_url
):
    sql = """
        INSERT INTO dbo.Items
        (
            CategoryGuid,
            ItemName,
            Brand,
            Model,
            MainImageUrl
        )
        OUTPUT INSERTED.ItemGuid
        VALUES (?, ?, ?, ?, ?)
    """

    cursor.execute(
        sql,
        category_guid,
        item_name,
        brand,
        model,
        image_url
    )

    row = cursor.fetchone()

    return row[0]


# ============================================================
# 取得或建立商品 Items
# ============================================================
def get_or_create_item(
    cursor,
    category_guid,
    item_name,
    brand,
    model,
    image_url,
    standard_product
):
    # --------------------------------------------------------
    # 先用 Brand + Model 尋找既有商品
    # --------------------------------------------------------
    matched_item = find_matching_item(
        cursor,
        category_guid,
        standard_product
    )

    if matched_item is not None:
        item_guid = matched_item["ItemGuid"]

        # 找到既有商品 → 共用 ItemGuid
        # 若目前資料沒有主圖，才補上新平台的圖片
        if not matched_item["MainImageUrl"] and image_url:
            sql = """
                UPDATE dbo.Items
                SET MainImageUrl = ?
                WHERE ItemGuid = ?
            """

            cursor.execute(
                sql,
                image_url,
                item_guid
            )

        return item_guid

    # --------------------------------------------------------
    # 找不到既有商品 → 建立新的 Items
    # --------------------------------------------------------
    return create_item(
        cursor,
        category_guid,
        item_name,
        brand,
        model,
        image_url
    )


# ============================================================
# 新增或更新 PlatformItems
# ============================================================
def upsert_platform_item(
    cursor,
    item_guid,
    platform_guid,
    platform_item_id,
    item_name,
    item_url,
    current_price
):
    scraped_at = datetime.now(timezone.utc)

    # --------------------------------------------------------
    # 先確認 PlatformItems 是否已經存在
    # --------------------------------------------------------
    sql = """
        SELECT PlatformItemGuid
        FROM dbo.PlatformItems
        WHERE ItemGuid = ?
          AND PlatformGuid = ?
          AND ItemUrl = ?
    """

    cursor.execute(
        sql,
        item_guid,
        platform_guid,
        item_url
    )

    row = cursor.fetchone()

    # --------------------------------------------------------
    # 已存在 → 更新
    # --------------------------------------------------------
    if row is not None:
        platform_item_guid = row[0]

        sql = """
            UPDATE dbo.PlatformItems
            SET OuterItemId = ?,
                PlatformItemName = ?,
                CurrentPrice = ?,
                LastScrapedAt = ?
            WHERE PlatformItemGuid = ?
        """

        cursor.execute(
            sql,
            platform_item_id,
            item_name,
            current_price,
            scraped_at,
            platform_item_guid
        )

        return platform_item_guid

    # --------------------------------------------------------
    # 不存在 → 新增
    # --------------------------------------------------------
    sql = """
        INSERT INTO dbo.PlatformItems
        (
            ItemGuid,
            PlatformGuid,
            OuterItemId,
            PlatformItemName,
            ItemUrl,
            CurrentPrice,
            StockStatus,
            LastScrapedAt
        )
        OUTPUT INSERTED.PlatformItemGuid
        VALUES (?, ?, ?, ?, ?, ?, 1, ?)
    """

    cursor.execute(
        sql,
        item_guid,
        platform_guid,
        platform_item_id,
        item_name,
        item_url,
        current_price,
        scraped_at
    )

    row = cursor.fetchone()

    return row[0]


# ============================================================
# 儲存商品資料
# ============================================================
def save_to_database(product_groups):

    if not product_groups:
        return

    connection = None
    cursor = None

    try:
        connection = get_db_connection()
        cursor = connection.cursor()

        # 分類
        first_product = product_groups[0]["products"][0]
        first_raw_product = first_product["raw_product"]

        category_name = first_raw_product.category_name

        category_guid = get_category_guid(
            cursor,
            category_name
        )

        # 逐個商品群組處理
        for group in product_groups:

            # =================================================
            # Items
            # =================================================
            item_name = group["item_name"]

            standard_product = group["standard_product"]

            brand = standard_product.brand
            model = standard_product.model
            
            if not brand or not model:
                continue

            # 第一筆商品作為主圖片
            first_product = group["products"][0]
            first_raw_product = first_product["raw_product"]

            image_url = first_raw_product.image_url

            item_guid = get_or_create_item(
                cursor,
                category_guid,
                item_name,
                brand,
                model,
                image_url,
                standard_product
            )

            # =================================================
            # PlatformItems
            # =================================================
            for product in group["products"]:
                raw_product = product["raw_product"]

                platform_guid = get_platform_guid(cursor, raw_product.platform)

                upsert_platform_item(
                    cursor,
                    item_guid,
                    platform_guid,
                    raw_product.platform_item_id,
                    raw_product.product_name,
                    raw_product.url,
                    raw_product.price
                )

        # Commit
        connection.commit()

        print(f"成功儲存 {len(product_groups)} 個商品")

    except Exception as e:
        if connection is not None:
            connection.rollback()

        print(f"儲存資料庫失敗：{e}")
        raise

    finally:
        if cursor is not None:
            cursor.close()

        if connection is not None:
            connection.close()
