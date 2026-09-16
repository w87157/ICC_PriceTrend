from selenium.webdriver.common.by import By
from selenium import webdriver
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
import time
import csv
import json
import os
import random
import sqlite3  # <-- 新增：匯入內建資料庫套件

# 自動抓取你現在這支 Python 檔案所在的資料夾路徑
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

INPUT_CSV = os.path.join(BASE_DIR, "分類網頁連結.csv")
OUTPUT_CSV = os.path.join(BASE_DIR, "pchome商品.csv")
PROGRESS_FILE = os.path.join(BASE_DIR, "pchome_selenium_progress.json")
DB_NAME = os.path.join(BASE_DIR, "pchome_products.db")  # 強制建立在同一個資料夾

RESTART_INTERVAL = 200          # 累計滾動幾次後，換下一個分類時重啟 Chrome（釋放記憶體）
MAX_STAGNANT_ROUNDS = 3         # 連續幾輪抓不到新商品就判定該分類已到底
MAX_CATEGORY_RETRIES = 3        # 單一分類載入失敗時的重試次數
SCROLL_PAUSE = 1.5

CATEGORY_DELAY = (3.0, 6.0)     # 換分類之間的延遲區間（秒）

FIELDNAMES = ["大類", "小類", "商品ID", "商品名稱", "價格", "連結"]

FAILED_LOG = "抓取失敗記錄.csv"


def log_failed_category(category_big, category_small, url):
    file_exists = os.path.exists(FAILED_LOG)
    with open(FAILED_LOG, "a", newline="", encoding="utf-8-sig") as f:
        writer = csv.writer(f)
        if not file_exists:
            writer.writerow(["大類", "小分類", "連結"])
        writer.writerow([category_big, category_small, url])


# ----------------------------
# 資料庫 (SQLite) 操作函式
# ----------------------------
def init_db():
    """初始化資料庫與資料表"""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    # 建立商品資料表 (若不存在)。設定 product_id 為 PRIMARY KEY，確保商品不重複
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS products (
            product_id TEXT PRIMARY KEY,
            category_big TEXT,
            category_small TEXT,
            title TEXT,
            price TEXT,
            link TEXT,
            update_time DATETIME DEFAULT (datetime('now', 'localtime'))
        )
    ''')
    conn.commit()
    conn.close()
    print(f"📁 資料庫 {DB_NAME} 初始化完成。")

def save_to_db(rows):
    """將抓取的資料存入資料庫"""
    if not rows:
        return
    
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    # 使用 INSERT OR REPLACE：如果 product_id 已存在，就更新它的資料（例如最新價格）
    sql = '''
        INSERT OR REPLACE INTO products 
        (category_big, category_small, product_id, title, price, link, update_time)
        VALUES (?, ?, ?, ?, ?, ?, datetime('now', 'localtime'))
    '''
    
    cursor.executemany(sql, rows)
    conn.commit()
    conn.close()
    
# ----------------------------
# Chrome 建立函式
# ----------------------------
def create_driver():
    chrome_options = Options()
    chrome_options.page_load_strategy = 'eager'
    chrome_options.add_argument("--headless=new")
    chrome_options.add_argument("--window-size=1440,2000")
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
    chrome_options.add_experimental_option("useAutomationExtension", False)
    chrome_options.add_argument(
        "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    )

    driver = webdriver.Chrome(options=chrome_options)
    try:
        driver.set_window_size(1440, 2000)
    except Exception:
        pass
    driver.execute_cdp_cmd(
        "Page.addScriptToEvaluateOnNewDocument",
        {"source": "Object.defineProperty(navigator, 'webdriver', {get: () => undefined})"},
    )
    return driver


# ----------------------------
# 斷點續傳：進度存取
# ----------------------------
def load_progress():
    if os.path.exists(PROGRESS_FILE):
        with open(PROGRESS_FILE, "r", encoding="utf-8") as f:
            return set(json.load(f))
    return set()


def save_progress(done_keys):
    with open(PROGRESS_FILE, "w", encoding="utf-8") as f:
        json.dump(sorted(done_keys), f, ensure_ascii=False, indent=2)


def ensure_csv_header():
    if not os.path.exists(OUTPUT_CSV):
        with open(OUTPUT_CSV, "w", newline="", encoding="utf-8-sig") as f:
            writer = csv.writer(f)
            writer.writerow(FIELDNAMES)


def append_rows(rows):
    if not rows:
        return
    with open(OUTPUT_CSV, "a", newline="", encoding="utf-8-sig") as f:
        writer = csv.writer(f)
        writer.writerows(rows)


# ----------------------------
# 找商品
# ----------------------------
def findProducts(driver):
    products = driver.find_elements(By.CSS_SELECTOR, "div.c-prodInfoV2")
    results = []

    for p in products:
        try:
            link_el = p.find_element(By.CSS_SELECTOR, "a.c-prodInfoV2__link")
        except Exception:
            continue

        link = link_el.get_attribute("href") or ""
        if link and link.startswith("/"):
            link = "https://24h.pchome.com.tw" + link

        prod_id = link.rstrip("/").split("/")[-1].split("?")[0] if link else ""

        title = ""
        try:
            title_el = p.find_element(By.CSS_SELECTOR, "h3.c-prodInfoV2__title")
            title = title_el.get_attribute("title") or title_el.text
        except Exception:
            pass
        if not title:
            try:
                img_el = p.find_element(By.CSS_SELECTOR, "div.c-prodInfoV2__img img")
                title = img_el.get_attribute("alt") or ""
            except Exception:
                pass

        price = ""
        price_candidates = [
            "div.c-prodInfoV2__price div.c-prodInfoV2__priceValue",
            "div.c-prodPrice__priceBox div.c-prodPrice__price",
            "div.c-prodInfoV2__priceValue",
            "div.c-prodPrice__price",
            "div.c-prodInfoV2__price",
            "div.c-prodPrice",
            "span.price",
            ".value"
        ]

        for retry in range(5):
            for selector in price_candidates:
                try:
                    price_els = p.find_elements(By.CSS_SELECTOR, selector)
                    for el in price_els:
                        raw_text = el.get_attribute("textContent")
                        
                        if raw_text:
                            clean_text = raw_text.replace("$", "").replace(",", "").replace("起", "").strip()
                            
                            if clean_text.isdigit():
                                price = clean_text
                                break
                except Exception:
                    continue
                
                if price:
                    break
            
            if price:
                break
                
            try:
                driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", p)
            except:
                pass
            
            time.sleep(0.6) 

        if not price:
            try:
                card_text = p.get_attribute("textContent")
                if card_text and ("售完" in card_text or "補貨中" in card_text):
                    price = "售完/補貨中"
            except:
                pass

        if link:
            results.append([prod_id, title, price, link])

    if not results:
        anchors = driver.find_elements(By.CSS_SELECTOR, "a[href*='/prod/']")
        seen_href = set()
        for a in anchors:
            link = a.get_attribute("href") or ""
            if not link or link in seen_href:
                continue
            seen_href.add(link)
            prod_id = link.rstrip("/").split("/")[-1].split("?")[0]
            title = a.get_attribute("title") or ""
            if not title:
                try:
                    img_el = a.find_element(By.CSS_SELECTOR, "img")
                    title = img_el.get_attribute("alt") or ""
                except Exception:
                    pass
            results.append([prod_id, title, "", link])

    del products
    return results


# ----------------------------
# 捲動頁面觸發 lazy-load
# ----------------------------
def scrollPage(driver, segment=10):
    for i in range(segment):
        driver.execute_script(
            f"window.scrollTo(0,{(i + 1) / segment}*document.body.scrollHeight);"
        )
        time.sleep(SCROLL_PAUSE / segment if segment else SCROLL_PAUSE)


# ----------------------------
# 嘗試點擊「顯示更多 / 載入更多」按鈕
# ----------------------------
def clickLoadMoreIfExists(driver):
    try:
        btn = driver.find_element(
            By.XPATH,
            "//button[contains(text(),'顯示更多') or contains(text(),'查看更多') or contains(text(),'載入更多')]",
        )
        driver.execute_script("arguments[0].scrollIntoView(true);", btn)
        time.sleep(0.5)
        btn.click()
        time.sleep(2)
        return True
    except Exception:
        return False


def load_category_page(driver, url, category_label="", retries=MAX_CATEGORY_RETRIES):
    for attempt in range(1, retries + 1):
        driver.get(url)
        try:
            driver.execute_script("""
                let overlays = document.querySelectorAll('[class*="ad-"], [class*="modal"], [id*="popup"], [class*="app-download"]');
                overlays.forEach(el => el.remove());
            """)
        except Exception:
            pass

        try:
            driver.execute_script("window.scrollTo(0, 300);")
            time.sleep(0.5)
        except Exception:
            pass

        wait_seconds = 10 + (attempt - 1) * 8
        try:
            WebDriverWait(driver, wait_seconds).until(
                lambda d: d.find_elements(By.CSS_SELECTOR, "div.c-prodInfoV2")
                          or d.find_elements(By.CSS_SELECTOR, "a[href*='/prod/']")
            )
            return True
        except Exception:
            print(f"  [警告] 第 {attempt} 次載入失敗（等待 {wait_seconds}s 仍未出現商品），重試中...")
            time.sleep(random.uniform(2.0, 4.0))

    try:
        safe_name = "".join(c if c.isalnum() else "_" for c in category_label)[:50]
        ts = int(time.time())
        screenshot_path = f"失敗截圖_{safe_name}_{ts}.png"
        html_path = f"失敗頁面_{safe_name}_{ts}.html"
        driver.save_screenshot(screenshot_path)
        with open(html_path, "w", encoding="utf-8") as f:
            f.write(driver.page_source)
        print(f"  [已存檔] 失敗當下的截圖與頁面原始碼：{screenshot_path} / {html_path}")
    except Exception as e:
        print(f"  [警告] 存檔失敗截圖時發生錯誤: {e}")

    return False


def crawl_one_category(driver, category_big, category_small, url, scroll_counter):
    if not load_category_page(driver, url, category_label=f"{category_big}_{category_small}"):
        print("  ❌ 商品載入失敗（已重試多次），跳過此分類")
        log_failed_category(category_big, category_small, url)
        return [], scroll_counter, driver

    seen_links = set()
    stagnant_rounds = 0
    collected_rows = []

    while True:
        scrollPage(driver)
        clicked = clickLoadMoreIfExists(driver)
        if not clicked:
            time.sleep(1.5)

        time.sleep(0.8)

        products = findProducts(driver)
        new_products = [p for p in products if p[3] not in seen_links] 

        for prod_id, title, price, link in new_products:
            seen_links.add(link)
            collected_rows.append(
                [category_big, category_small, prod_id, title, price, link]
            )

        del products

        if not new_products:
            stagnant_rounds += 1
        else:
            stagnant_rounds = 0

        if stagnant_rounds >= MAX_STAGNANT_ROUNDS:
            print(f"  已到底，共取得 {len(seen_links)} 筆")
            break

        scroll_counter += 1

        if scroll_counter % RESTART_INTERVAL == 0:
            print("  [重啟] 累積滾動次數達門檻，將於本分類結束後重啟 Chrome 釋放記憶體")

    return collected_rows, scroll_counter, driver


# ============================
# 開始作業
# ============================
if __name__ == "__main__":
    if not os.path.exists(INPUT_CSV):
        print(f"[錯誤] 找不到輸入檔案：{INPUT_CSV}")
        raise SystemExit(1)

    with open(INPUT_CSV, "r", encoding="utf-8-sig") as f_check:
        reader_check = csv.DictReader(f_check)
        required_cols = {"大類", "小分類", "連結"}
        missing = required_cols - set(reader_check.fieldnames or [])
        if missing:
            print(f"[錯誤] 輸入 CSV 缺少必要欄位：{missing}")
            print(f"目前的欄位是：{reader_check.fieldnames}")
            raise SystemExit(1)

    # 初始化 CSV 與 SQLite DB
    ensure_csv_header()
    init_db()  # <-- 新增：確保資料庫被建立
    
    done_keys = load_progress()

    with open(INPUT_CSV, "r", encoding="utf-8-sig") as f_read:
        reader = csv.DictReader(f_read)
        all_rows = list(reader)

    remaining = [row for row in all_rows
                 if f"{row['大類']}|{row['小分類']}" not in done_keys]

    print(f"分類總數: {len(all_rows)}｜已完成: {len(all_rows) - len(remaining)}｜剩餘: {len(remaining)}\n")

    if not remaining:
        print("🎉 全部分類都已抓取完畢！")
        raise SystemExit(0)

    driver = create_driver()
    scroll_counter = 0

    try:
        for idx, row in enumerate(remaining, 1):
            category_big = row["大類"]
            category_small = row["小分類"]
            url = row["連結"]
            key = f"{category_big}|{category_small}"

            print(f"\n[{idx}/{len(remaining)}] === 分類：{category_big} > {category_small} ===")

            rows, scroll_counter, driver = crawl_one_category(
                driver, category_big, category_small, url, scroll_counter
            )

            # 同時寫入 CSV 與 SQLite DB（雙重備份更安全）
            append_rows(rows)
            save_to_db(rows)  # <-- 新增：將此分類抓到的商品寫入資料庫
            
            done_keys.add(key)
            save_progress(done_keys)

            print(f"  ✅ 本分類寫入 {len(rows)} 筆 (已存至 CSV 與 資料庫)")

            if scroll_counter >= RESTART_INTERVAL:
                print("  [重啟] 重新啟動 Chrome 釋放記憶體...")
                driver.quit()
                driver = create_driver()
                scroll_counter = 0

            time.sleep(random.uniform(*CATEGORY_DELAY))

    finally:
        driver.quit()

    remaining_after = len(all_rows) - len(done_keys)
    if remaining_after > 0:
        print(f"\n本次執行結束，還剩 {remaining_after} 個分類尚未抓取。")
        print("重新執行程式即可自動接續。")
    else:
        print(f"\n✅ 全部完成，已存至 {OUTPUT_CSV} 以及 {DB_NAME} 資料庫！")