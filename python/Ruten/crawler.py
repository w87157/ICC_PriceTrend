# -*- coding: utf-8 -*-
"""
Created on Sat Sep  5 16:36:52 2026

@author: a0909
"""
import sys
import os
import time
from datetime import datetime, timezone
from pathlib import Path
import csv
import pyodbc
import pandas as pd
from selenium import webdriver
from dotenv import load_dotenv
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# =========================================================
# normalizer 路徑
# =========================================================
sys.path.append(str(Path(__file__).resolve().parents[1]))

from normalizer import normalize_product_name
from product_parser import parse_product

# =========================================================
#  路徑/環境設定
# =========================================================
BASE_DIR = Path(__file__).resolve().parents[1]
load_dotenv(BASE_DIR / ".env")


# =========================================================
#  爬蟲設定
# =========================================================
TARGET_CATEGORY_NAME = "電腦3C"

PLATFORM_NAME = "露天拍賣"

BASE_URL = "https://www.ruten.com.tw/"


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
#  讀取分類連結檔案
# =========================================================
def load_categories(csv_file):
    categories = []

    with open(csv_file, "r", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)

        for row in reader:
            categories.append(
                {
                    "big_category": row["大類"],
                    "small_category": row["小分類"],
                    "url": row["連結"]
                }
            )

    return categories
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
#  爬取 露天商品
# =========================================================
def crawl_ruten():
    chrome_options = Options()
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")
    chrome_options.add_argument("--disable-gpu")
    driver=webdriver.Chrome(options=chrome_options)


    RESTART_INTERVAL = 200
    page_counter = 0
    results = []
    # 開檔
    with open("電腦電子.csv","r",encoding="utf-8-sig") as f_read:
        reader = csv.DictReader(f_read)
        for row in reader:
            url = row["連結"]
            driver.get(url)

        
            retries = 0
            while True:
                # 等待商品載入
                try:
                    WebDriverWait(driver, 10).until(
                        EC.presence_of_all_elements_located(
                            (By.CSS_SELECTOR, "div.product-item")
                        )
                    )
                    retries = 0
                except:
                    retries += 1
                    print(f"商品載入失敗，重試第 {retries} 次")
                    time.sleep(2)
            
                    if retries >= 3:
                        print("商品載入失敗，跳過此分類")
                        break
                    else:
                        continue
                
                for i in range(10):  # 分段滾動
                    driver.execute_script(f"window.scrollTo(0, {(i+1)/10}*document.body.scrollHeight);")
                    time.sleep(1)
                        
            #找到商品位置
                products = driver.find_elements(By.CSS_SELECTOR, "div.search-result-container.top-part div.product-item, div.search-result-container.bottom-part div.product-item")
                for p in products:
                    try:
                        title = p.find_element(By.CSS_SELECTOR,"p.rt-product-card-name").text
                        price = p.find_element(By.CSS_SELECTOR,"div.price-range-container").text
                        link = p.find_element(By.CSS_SELECTOR,"a.rt-product-card-name-wrap").get_attribute("href")
                        # img_url = p.find_element(By.CSS_SELECTOR,"img.rt-product-card-img").get_attribute("src")
                        normalized_name = normalize_product_name(title)
                        parsed_product = parse_product(normalized_name)
                        
                        results.append({
                            "category": "電腦3C",
                            "item_name": title,
                            "normalized_name": normalized_name,
                    
                            "brand": parsed_product["brand"],
                            "series": parsed_product["series"],
                            "model": parsed_product["model"],
                            "product_type": parsed_product["product_type"],
                    
                            "screen_size": parsed_product["screen_size"],
                            "resolution": parsed_product["resolution"],
                            "panel": parsed_product["panel"],
                            "refresh_rate": parsed_product["refresh_rate"],
                            "response_time": parsed_product["response_time"],
                    
                            "ram": parsed_product["ram"],
                            "storage": parsed_product["storage"],
                    
                            "wifi": parsed_product["wifi"],
                            "wifi_class": parsed_product["wifi_class"],
                    
                            "usb_versions": parsed_product["usb_versions"],
                            "interfaces": parsed_product["interfaces"],
                    
                            "color": parsed_product["color"],
                            "speaker": parsed_product["speaker"],
                            
                            "price": price,
                            "link": link,
                            #"img_url": img_url
                        })
     
                        print("  -", title, price, link)
                        
                    except:
                        continue
                del products  
                        
            # 翻頁
                try:
                    next_btn = driver.find_element(By.CSS_SELECTOR, "a.pager-next")
                    if "is-disabled" in next_btn.get_attribute("class"):
                        break
                    next_btn.click()
                    WebDriverWait(driver, 10).until(
                        EC.presence_of_element_located((By.CSS_SELECTOR, "div.product-item"))
                    )
                    time.sleep(2)  
                except:
                    continue
                page_counter += 1
                
                # 定期重啟 Chrome
                if page_counter % RESTART_INTERVAL == 0:
                    current_url = driver.current_url
    
                    driver.quit()
                    
                    driver = webdriver.Chrome(options=chrome_options)
                    driver.get(current_url)
                    
                    
                    try:
                        WebDriverWait(driver, 10).until(
                            EC.presence_of_all_elements_located(
                                (By.CSS_SELECTOR, "div.product-item")
                                )
                        )
                    except:
                        continue

    driver.quit()
    
    return results


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
    
    products = crawl_ruten()
    print(f"總共爬到 {len(products)} 筆資料")
    
    df = pd.DataFrame(products)
    if df.empty:
        print("沒有取得任何商品")
        return
    
    # 去除重複商品
    df = df.drop_duplicates(subset=["link"]).reset_index(drop=True)
    print(f"去除重複後剩下 {len(df)} 筆商品")
    
    df.to_csv("coupang_products.csv", index=False, encoding="utf-8-sig")
    print("CSV 備份完成： coupang_products.csv")
    
    save_to_database(df.to_dict("records"))
    
    
# =========================================================
#  執行
# =========================================================
if __name__ == "__main__":
    main()