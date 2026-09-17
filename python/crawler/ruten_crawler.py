# -*- coding: utf-8 -*-
"""
Created on Sat Sep  5 16:36:52 2026

@author: a0909
"""
import sys
import time
from pathlib import Path
import csv
from pandas import pd 
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# =========================================================
# normalizer 路徑
# =========================================================
sys.path.append(str(Path(__file__).resolve().parents[1]))


# =========================================================
#  路徑/環境設定
# =========================================================
BASE_DIR = Path(__file__).resolve().parents[1]
INPUT_CSV = BASE_DIR / "data" / "input" / "ruten_category_links.csv"
OUTPUT_CSV = BASE_DIR / "data" / "raw" / "ruten_raw_products.csv"
OUTPUT_CSV.parent.mkdir(parents=True, exist_ok=True)

FIELDNAMES = [
    "platform",
    "platform_item_id",
    "product_name",
    "price",
    "url",
    "image_url",
    "category_name",
]


# =========================================================
#  爬蟲設定
# =========================================================
TARGET_CATEGORY_NAME = "電腦3C"

PLATFORM_NAME = "露天拍賣"

BASE_URL = "https://www.ruten.com.tw/"


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
#  爬取 露天商品
# =========================================================
def crawl_ruten():
    chrome_options = Options()
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")
    chrome_options.add_argument("--disable-gpu")
    driver = webdriver.Chrome(options=chrome_options)

    results = []

    with open(INPUT_CSV, "r", encoding="utf-8-sig") as f_read:
        reader = csv.DictReader(f_read)

        for row in reader:
            category_name = f"{row.get('大類', '')} > {row.get('小分類', '')}"
            url = row.get("連結", "")

            if not url:
                continue

            driver.get(url)

            try:
                WebDriverWait(driver, 10).until(
                    EC.presence_of_all_elements_located(
                        (By.CSS_SELECTOR, "div.product-item")
                    )
                )
            except Exception:
                print(f"商品載入失敗，跳過分類：{category_name}")
                continue

            for i in range(10):
                driver.execute_script(
                    f"window.scrollTo(0, {(i + 1) / 10} * document.body.scrollHeight);"
                )
                time.sleep(1)

            products = driver.find_elements(
                By.CSS_SELECTOR,
                "div.search-result-container.top-part div.product-item, "
                "div.search-result-container.bottom-part div.product-item"
            )

            for product in products:
                try:
                    title = product.find_element(
                        By.CSS_SELECTOR, "p.rt-product-card-name"
                    ).text.strip()

                    price = product.find_element(
                        By.CSS_SELECTOR, "div.price-range-container"
                    ).text.strip()

                    link = product.find_element(
                        By.CSS_SELECTOR, "a.rt-product-card-name-wrap"
                    ).get_attribute("href") or ""

                    image_url = ""
                    try:
                        image = product.find_element(
                            By.CSS_SELECTOR, "img.rt-product-card-img"
                        )
                        image_url = (
                            image.get_attribute("src")
                            or image.get_attribute("data-src")
                            or ""
                        )
                    except Exception:
                        pass

                    product_id = link.rstrip("/").split("/")[-1].split("?")[0]

                    results.append({
                        "platform": PLATFORM_NAME,
                        "platform_item_id": product_id,
                        "product_name": title,
                        "price": price,
                        "url": link,
                        "image_url": image_url or None,
                        "category_name": category_name,
                    })

                    print("  -", title, price, link)

                except Exception:
                    continue

            del products

    driver.quit()
    return results


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
    print(f"CSV 備份完成：{OUTPUT_CSV}")
    
    
# =========================================================
#  執行
# =========================================================
if __name__ == "__main__":
    main()