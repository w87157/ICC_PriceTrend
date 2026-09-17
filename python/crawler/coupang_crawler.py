import pandas as pd
import re
import time
from pathlib import Path

from bs4 import BeautifulSoup
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
import undetected_chromedriver as uc

from models.raw_product import RawProduct

# =========================================================
# 酷澎設定
# =========================================================
TARGET_CATEGORY_NAME = "電腦3C"
TARGET_CATEGORY_URL = (
    "https://www.tw.coupang.com/categories/%E9%9B%BB%E8%85%A63C-572307"
)
PLATFORM_NAME = "酷澎"
BASE_URL = "https://www.tw.coupang.com"

# =========================================================
# CSV 設定
# =========================================================
BASE_DIR = Path(__file__).resolve().parent.parent
RAW_DATA_DIR = BASE_DIR / "data" / "raw"
CSV_FILE_PATH = RAW_DATA_DIR / "coupang_products.csv"


# =========================================================
# 爬取酷澎商品
# =========================================================
def crawl_coupang():
    options = uc.ChromeOptions()
    options.add_argument("--start-maximized")
    options.add_argument("--disable-popup-blocking")
    options.add_argument("--lang=zh-TW")
    options.add_argument(
        "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/125.0.0.0 Safari/537.36"
    )

    driver = uc.Chrome(options=options)
    products = []

    try:
        page = 1
        while True:
            print(f"正在爬取第 {page} 頁...")

            url = (
                TARGET_CATEGORY_URL
                if page == 1
                else f"{TARGET_CATEGORY_URL}?page={page}"
            )
            driver.get(url)

            # 判斷這一頁是不是沒有商品
            no_item = driver.find_elements(By.CSS_SELECTOR, "div.no-list-item")
            if no_item:
                print(f"第 {page} 頁沒有商品，停止爬蟲。")
                break

            # 等待商品載入
            try:
                WebDriverWait(driver, 20).until(
                    EC.presence_of_element_located(
                        (By.CSS_SELECTOR, "li[class*='ProductUnit_productUnit']")
                    )
                )
            except Exception:
                print(f"第 {page} 頁等待商品逾時，跳過。")
                page += 1
                continue

            time.sleep(2)
            
            soup = BeautifulSoup(driver.page_source, "html.parser")
            product_elements = soup.select("li[class*='ProductUnit_productUnit']")

            print(f"第 {page} 頁找到 {len(product_elements)} 個商品")

            for product in product_elements:
                # 商品名稱
                title_element = product.select_one("div[class*='productName']")
                if not title_element:
                    continue
                item_name = title_element.get_text(strip=True)
                if not item_name:
                    continue

                # 商品價格
                price_element = product.select_one(
                    "div[class*='PriceArea_price'] strong[translate='no']"
                )
                if not price_element:
                    print(f"找不到價格：{item_name}")
                    continue

                price_text = price_element.get_text(strip=True)
                price_text = re.sub(r"[^\d.]", "", price_text)

                try:
                    price = float(price_text)
                except ValueError:
                    print(f"價格格式錯誤：{item_name} / {price_text}")
                    continue

                # 商品網址
                link_element = product.select_one("a")
                if not link_element:
                    continue

                item_url = link_element.get("href")
                if not item_url:
                    continue

                if item_url.startswith("/"):
                    item_url = BASE_URL + item_url

                # 商品圖片
                image_url = None
                image_element = product.select_one("img")
                if image_element:
                    image_url = (
                        image_element.get("src")
                        or image_element.get("data-src")
                        or image_element.get("data-original")
                    )

                # 平台商品 ID
                platform_item_id = product.get("data-product-id")
                if platform_item_id is not None:
                    platform_item_id = str(platform_item_id)

                # 建立 RawProduct
                raw_product = RawProduct(
                    platform=PLATFORM_NAME,
                    platform_item_id=platform_item_id,
                    product_name=item_name,
                    price=price,
                    url=item_url,
                    image_url=image_url,
                    category_name=TARGET_CATEGORY_NAME,
                )
                products.append(raw_product)

            page += 1

    finally:
        driver.quit()

    return products


# =========================================================
# 儲存 Raw CSV
# =========================================================
def save_products_to_csv(products, file_path=CSV_FILE_PATH):
    file_path.parent.mkdir(parents=True, exist_ok=True)

    data = []

    for product in products:
        data.append(
            {
                "platform": product.platform,
                "platform_item_id": product.platform_item_id,
                "product_name": product.product_name,
                "price": product.price,
                "url": product.url,
                "image_url": product.image_url,
                "category_name": product.category_name,
            }
        )

    df = pd.DataFrame(data)
    df.to_csv(file_path, index=False, encoding="utf-8-sig")

    print(f"CSV 儲存完成：{file_path}")


# =========================================================
# 主程式
# =========================================================
def main():
    print("==============================")
    print(" 酷澎商品爬蟲")
    print("==============================")

    products = crawl_coupang()
    print(f"總共爬到 {len(products)} 筆原始商品")

    save_products_to_csv(products)


if __name__ == "__main__":
    main()