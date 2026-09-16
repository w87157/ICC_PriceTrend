import csv
from pathlib import Path

from models.raw_product import RawProduct

# ============================================================
# 路徑設定
# ============================================================
BASE_DIR = Path(__file__).resolve().parent
RAW_DATA_DIR = BASE_DIR / "data" / "raw"


# ============================================================
# 讀取單一 CSV
# ============================================================
def load_csv(file_path):
    file_path = Path(file_path)

    if not file_path.exists():
        raise FileNotFoundError(f"找不到 CSV 檔案：{file_path}")

    products = []
    with open(file_path, "r", encoding="utf-8-sig", newline="") as file:
        reader = csv.DictReader(file)
        for row in reader:
            product = RawProduct.from_dict(row)
            products.append(product)

    print(f"讀取 {file_path.name}：{len(products)} 筆商品")
    return products


# ============================================================
# 讀取所有平台 CSV
# ============================================================
def load_all_csv(data_dir=RAW_DATA_DIR):
    data_dir = Path(data_dir)

    if not data_dir.exists():
        raise FileNotFoundError(f"找不到 Raw CSV 資料夾：{data_dir}")

    csv_files = sorted(data_dir.glob("*.csv"))

    if not csv_files:
        print(f"資料夾內沒有 CSV：{data_dir}")
        return []

    all_products = []
    for csv_file in csv_files:
        products = load_csv(csv_file)
        all_products.extend(products)

    print("==============================")
    print(f"所有平台共讀取 {len(all_products)} 筆商品")
    print("==============================")

    return all_products

if __name__ == "__main__":

    products = load_all_csv()

    print(
        f"總商品數：{len(products)}"
    )

    if products:
        print()
        print(products[0])