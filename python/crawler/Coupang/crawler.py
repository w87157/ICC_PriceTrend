import re
import time

from bs4 import BeautifulSoup
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
import undetected_chromedriver as uc

from models.raw_product import RawProduct
from normalizer import normalize_product_name
from product_analyzer import parse_product
from product_matcher import group_products
from product_repository import save_to_database


# =========================================================
# 酷澎設定
# =========================================================
TARGET_CATEGORY_NAME = "電腦3C"
TARGET_CATEGORY_URL = "https://www.tw.coupang.com/categories/%E9%9B%BB%E8%85%A63C-572307"
PLATFORM_NAME = "酷澎"
BASE_URL = "https://www.tw.coupang.com"


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

            url = TARGET_CATEGORY_URL if page == 1 else f"{TARGET_CATEGORY_URL}?page={page}"
            driver.get(url)

            # 判斷這一頁是不是沒有商品
            no_item = driver.find_elements(By.CSS_SELECTOR, "div.no-list-item")
            if no_item:
                print(f"第 {page} 頁沒有商品，停止爬蟲。")
                break

            # 等待商品載入
            try:
                WebDriverWait(driver, 20).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, "li[class*='ProductUnit_productUnit']"))
                )
            except Exception:
                print(f"第 {page} 頁等待商品逾時，跳過。")
                page += 1
                continue

            # 稍微等待網頁穩定
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
                price_element = product.select_one("div[class*='PriceArea_price'] strong[translate='no']")
                if not price_element:
                    print(f"找不到價格：{item_name}")
                    continue

                price_text = price_element.get_text(strip=True)
                # 移除非數字相關字元（保留數字與小數點）
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
                    raw_data={}
                )

                products.append(raw_product)

            page += 1

    finally:
        driver.quit()

    return products


# =========================================================
# 主程式
# =========================================================
def main():
    print("==============================")
    print(" 酷澎商品爬蟲")
    print("==============================")

    products = crawl_coupang()
    print(f"總共爬到 {len(products)} 筆原始商品")

    # 去除重複網址
    unique_products = []
    seen_urls = set()

    for product in products:
        if product.url in seen_urls:
            continue
        
        seen_urls.add(product.url)
        unique_products.append(product)

    products = unique_products
    print(f"去除重複後剩下 {len(products)} 筆商品")
    
    # 商品名稱標準化 + 商品分析
    analyzed_products = []
    for product in products:
        # 商品名稱標準化
        normalized_name = normalize_product_name(product.product_name)

        # 商品分析
        standard_product = parse_product(normalized_name)

        if standard_product is not None:
            analyzed_products.append(
                {
                    "raw_product": product,
                    "standard_product": standard_product
                }
            )

    print(f"成功分析 {len(analyzed_products)} 筆商品")
    
    # 商品比對與分組
    product_groups = group_products(analyzed_products)
    
    print(f"商品分組完成，共 {len(product_groups)} 個不同商品")
    
    for group in product_groups:
        print(f"商品：{group['item_name']} / 平台商品數：{len(group['products'])}")
        for product in group["products"]:
            print(f"    - {product['raw_product'].platform}： {product['raw_product'].product_name}")
    
    
    # 儲存到資料庫
    save_to_database(product_groups)


if __name__ == "__main__":
    main()