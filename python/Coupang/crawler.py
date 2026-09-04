import os
import time
from datetime import datetime, timezone
from pathlib import Path

import pyodbc
import pandas as pd
import undetected_chromedriver as uc

from dotenv import load_dotenv
from bs4 import BeautifulSoup
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# =========================================================
#  路徑/環境設定
# =========================================================
BASE_DIR = Path(__file__).resolve().parents[1]
load_dotenv(BASE_DIR / ".env")


# =========================================================
#  爬蟲設定
# =========================================================
TARGET_CATEGORY_NAME = "電腦3C"
TARGET_CATEGORY_URL = "https://www.tw.coupang.com/categories/%E9%9B%BB%E8%85%A63C-572307"

PLATFORM_NAME = "酷澎"

BASE_URL = "https://www.tw.coupang.com/"


# =========================================================
#  MSSQL 連線設定
# =========================================================
DB_CONNECTION_STRING = (
    "DRIVER={ODBC Driver 18 for SQL Server};"
    f"SERVER={os.getenv('DB_SERVER')};"
    f"DATABASE={os.getenv('DB_DATABASE')};"
    "Trusted_Connection=yes;"
    "TrustServerCertificate=yes;"
)


# =========================================================
#  連線資料庫
# =========================================================
def get_db_connection():
    return pyodbc.connect(DB_CONNECTION_STRING)


# =========================================================
#  取得 類別GUID
# =========================================================
def get_category_guid(cursor, category_name):
    cursor.execute(
        "SELECT CategoryGuid FROM dbo.Categories WHERE CategoryName = ?", category_name
    )
    
    row = cursor.fetchone()
    if row is None:
        raise Exception(
            f"找不到分類: {category_name}，請先在 Categories 建立資料。"
        )
    
    return row[0]


# =========================================================
#  取得 平台GUID
# =========================================================
def get_platform_guid(cursor, platform_name):
    cursor.execute(
        "SELECT PlatformGuid FROM dbo.Platforms WHERE PlatformName = ?", platform_name
    )
    
    row = cursor.fetchone()
    if row is None:
        raise Exception(
            f"找不到平台: {platform_name}，請先在 Platforms 建立資料。"
        )
    
    return row[0]


# =========================================================
#  找商品 Items
# =========================================================
def get_or_create_item(cursor, category_guid, item_name):
    cursor.execute(
        "SELECT ItemGuid FROM dbo.Items WHERE CategoryGuid = ? AND ItemName = ?", category_guid, item_name 
    )
    
    row = cursor.fetchone()
    if row is not None:
        return row[0]
    
    # 商品不存在則新增
    cursor.execute(
        "INSERT INTO dbo.Items(CategoryGuid, ItemName, Status) OUTPUT INSERTED.ItemGuid VALUES(?, ?, 1)", category_guid, item_name    
    )
    
    item_guid = cursor.fetchone()[0]
    
    return item_guid


# =========================================================
#  新增 / 更新 PlatformItems
# =========================================================
def upsert_platform_item(cursor, item_guid, platform_guid, item_name, item_url, current_price):
    cursor.execute(
        "SELECT PlatformItemGuid FROM dbo.PlatformItems WHERE ItemGuid = ? AND platformGuid = ? AND ItemUrl = ?", item_guid, platform_guid, item_url
    )
    
    row = cursor.fetchone()
    if row is not None:
        platform_item_guid = row[0]
        
        # 已存在則更新
        cursor.execute(
            "UPDATE dbo.PlatformItems SET PlatformItemName = ?, CurrentPrice = ?, LastScrapedAt = ? WHERE PlatformItemGuid = ?",
            item_name, current_price, datetime.now(timezone.utc), platform_item_guid
        )
        
        return platform_item_guid, "UPDATE"
        
    # 不存在則新增
    cursor.execute(
        "INSERT INTO dbo.PlatformItems(ItemGuid, PlatformGuid, PlatformItemName, ItemUrl, CurrentPrice, StockStatus, LastScrapedAt) OUTPUT INSERTED.PlatformItemGuid VALUES (?, ?, ?, ?, ?, 1, ?)",
        item_guid, platform_guid, item_name, item_url, current_price, datetime.now(timezone.utc)
    )
    
    platform_item_guid = cursor.fetchone()[0]
    
    return platform_item_guid, "INSERT"


# =========================================================
#  爬取 酷澎商品
# =========================================================
def crawl_coupang():
    options = uc.ChromeOptions()
    options.add_argument("--start-maximized")
    options.add_argument("--disable-popup-blocking")
    options.add_argument("--lang=zh-TW")
    options.add_argument(
        "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36"
    )
    
    driver = uc.Chrome(options=options)
    
    products = []
    
    try:
        page = 1
        while True:
            print(f"正在爬取第 {page} 頁...")
            url = TARGET_CATEGORY_URL
            
            if page > 1:
                url = f"{TARGET_CATEGORY_URL}?page={page}"
                
            driver.get(url)
            
            no_item = driver.find_elements(By.CSS_SELECTOR, "div.no-list-item")
            if no_item:
                print(f"第 {page} 頁沒有商品，停止爬蟲。")
                break
            
            try:
                WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.CSS_SELECTOR, "li[class*='ProductUnit_productUnit']")))
            except Exception:
                print(f"第 {page} 頁等待商品逾時，跳過。")
                continue
            
            time.sleep(2)
            
            soup = BeautifulSoup(driver.page_source, "html.parser")
            product_elements = soup.select("li[class*='ProductUnit_productUnit']")
            print(f"第 {page} 頁找到 {len(product_elements)} 個商品")
            for product in product_elements:
                # 商品名稱
                title_element = product.select_one("div[class*='productName']")
                if title_element is None:
                    continue
                
                item_name = title_element.get_text(strip=True)
                if not item_name:
                    continue
                
                # 商品價格
                price_element = product.select_one("div[class*='PriceArea_price'] strong[translate='no']")
                if price_element is None:
                    print(f"找不到價格：{item_name}")
                    continue
                
                price_text = price_element.get_text(strip=True).replace(",", "").replace("$", "").replace("NT", "").strip()
                try:
                    price = eval(price_text)
                except ValueError:
                    print(f"價格格式錯誤： {item_name} / {price_text}")
                    continue
                
                # 商品網址
                link_element = product.select_one("a")
                if link_element is None:
                    continue
                
                item_url = link_element.get("href")
                if not item_url:
                    continue
                
                if item_url.startswith("/"):
                    item_url = (BASE_URL + item_url)
                
                products.append(
                    {
                        "category_name": TARGET_CATEGORY_NAME,
                        "item_name": item_name,
                        "price": price,
                        "link": item_url
                    }    
                )
                
            page += 1
                
    finally:
        driver.quit()
    
    return products


# =========================================================
#  寫入 MSSQL
# =========================================================
def save_to_database(products):
    if not products:
        print("沒有商品資料，不寫入資料庫。")
        return
    
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        
        category_guid = get_category_guid(cursor, TARGET_CATEGORY_NAME)
        platform_guid = get_platform_guid(cursor, PLATFORM_NAME)
        print(f"CategoryGuid: {category_guid}")
        print(f"PlatformGuid: {platform_guid}")

        insert_count = 0
        update_count = 0
        
        for product in products:
            item_name = product["item_name"]
            price = product["price"]
            item_url = product["link"]
            
            try:
                # Items
                item_guid = get_or_create_item(cursor, category_guid, item_name)
                
                # PlatformItems
                platform_item_guid, action = (
                    upsert_platform_item(cursor, item_guid, platform_guid, item_name, item_url, price)
                )
                
                if action == "INSERT":
                    insert_count += 1
                else:
                    update_count += 1
                    
                print(f"[{action}] {item_name} | ${price}")
            except Exception as e:
                print(f"[ERROR] {item_name}：{e}")
                
            conn.commit()
            
            print("==============================")
            print("資料庫寫入完成")
            print("==============================")
            print(f"新增 PlatformItems：{insert_count}")
            print(f"更新 PlatformItems：{update_count}")
        
    except Exception:
        conn.rollback()
        raise
    
    finally:
        cursor.close()
        conn.close()


# =========================================================
#  主程式
# =========================================================
def main():
    print("==============================")
    print(" 商品爬蟲")
    print("==============================")
    
    products = crawl_coupang()
    print(f"總共爬到 {len(products)} 筆資料")
    
    df = pd.DataFrame(products)
    if df.empty:
        print("沒有取得任何商品")
        return
    
    # 去除重複商品
    df = df.drop_duplicates(subset=["link"]).reset_index(drop=True)
    print(f"去除重複後剩下 {len(df)} 筆商品")
    
    # df.to_csv("coupang_products.csv", index=False, encoding="utf-8-sig")
    # print("CSV 備份完成： coupang_products.csv")
    
    save_to_database(df.to_dict("records"))
    
    
# =========================================================
#  執行
# =========================================================
if __name__ == "__main__":
    main()

