import re


# ============================================================
# 品牌名稱統一
# ============================================================
BRAND_ALIASES = {
    "華碩": "ASUS",
    "ASUSTeK": "ASUS",
    "宏碁": "ACER",
    "宏碁AOPEN": "AOPEN",
    "威剛": "ADATA",
    "技嘉": "GIGABYTE",
    "微星": "MSI",
    "華擎": "ASROCK",
    "聯想": "LENOVO",
    "惠普": "HP",
    "戴爾": "DELL",
    "三星": "SAMSUNG",
    "索尼": "SONY",
    "羅技": "LOGITECH",
    "雷蛇": "RAZER",
    "創見": "TRANSCEND",
    "十銓": "TEAM",
    "金士頓": "KINGSTON",
}


# ============================================================
# 可以移除的行銷文字
# ============================================================
REMOVE_WORDS = [

    # 保固
    r"原廠保固",
    r"原廠保證",
    r"\d+\s*年保固",
    r"\d+\s*年保",
    r"保固\d*年?",
    r"保固",

    # 出貨 / 銷售
    r"官方旗艦",
    r"官方授權",
    r"公司貨",
    r"平輸",
    r"福利品",
    r"福利",
    r"全新",
    r"新品",

    # 配送
    r"快速到貨",
    r"隔日到貨",
    r"現貨",

    # 優惠 / 行銷
    r"限時優惠",
    r"優惠",
    r"特價",
    r"促銷",
    r"熱銷",
    r"人氣",
    r"推薦",
]


# ============================================================
# 可以移除的數量表示
# ============================================================
QUANTITY_PATTERNS = [
    r"\b\d+\s*個\b",
    r"\b\d+\s*入\b",
    r"\b\d+\s*件\b",
    r"\b\d+\s*組\b",
    r"\b\d+\s*包\b",
    r"\b\d+\s*盒\b",
    r"\b\d+\s*顆\b",
    r"\b\d+\s*支\b",
    r"\b\d+\s*條\b",
    r"\b\d+\s*台\b",

    r"一個",
    r"一入",
    r"一件",
    r"一組",
    r"一包",
    r"一盒",
    r"單入",
    r"單個",
]


# ============================================================
# 1. 符號統一
# ============================================================
def normalize_symbols(text):

    if not text:
        return ""

    text = text.replace("　", " ")
    text = text.replace("–", "-")
    text = text.replace("—", "-")
    text = text.replace("－", "-")
    text = text.replace("／", "/")
    text = text.replace("×", "x")
    text = text.replace("＊", "*")

    return text


# ============================================================
# 2. 移除行銷文字
# ============================================================
def remove_marketing_words(text):

    if not text:
        return ""

    for word in REMOVE_WORDS:

        text = re.sub(
            word,
            " ",
            text,
            flags=re.IGNORECASE
        )

    return text


# ============================================================
# 3. 移除銷售數量
# ============================================================
def remove_quantity_words(text):

    if not text:
        return ""

    for pattern in QUANTITY_PATTERNS:

        text = re.sub(
            pattern,
            " ",
            text,
            flags=re.IGNORECASE
        )

    return text


# ============================================================
# 4. 品牌名稱統一
# ============================================================
def normalize_brand_names(text):

    if not text:
        return ""

    # 先處理比較長的品牌名稱
    brand_list = sorted(
        BRAND_ALIASES.keys(),
        key=len,
        reverse=True
    )

    for brand in brand_list:

        text = re.sub(
            re.escape(brand),
            BRAND_ALIASES[brand],
            text,
            flags=re.IGNORECASE
        )

    return text


# ============================================================
# 5. 移除重複品牌
# ============================================================
def remove_duplicate_brands(text):

    if not text:
        return ""

    # 取得所有標準品牌名稱
    brand_names = set()

    for brand in BRAND_ALIASES.values():
        brand_names.add(brand.upper())

    words = text.split()

    result = []
    previous_word = ""

    for word in words:

        if (
            word.upper() in brand_names
            and word.upper() == previous_word.upper()
        ):
            continue

        result.append(word)
        previous_word = word

    return " ".join(result)


# ============================================================
# 6. 尺寸單位統一
# ============================================================
def normalize_size_units(text):

    if not text:
        return ""

    # 英吋統一成吋
    text = re.sub(
        r"(\d+(?:\.\d+)?)\s*英吋",
        r"\1吋",
        text
    )

    return text


# ============================================================
# 7. 常見單位統一
# ============================================================
def normalize_common_units(text):

    if not text:
        return ""

    # GB
    text = re.sub(
        r"(\d+(?:\.\d+)?)\s*GB",
        r"\1GB",
        text,
        flags=re.IGNORECASE
    )

    # TB
    text = re.sub(
        r"(\d+(?:\.\d+)?)\s*TB",
        r"\1TB",
        text,
        flags=re.IGNORECASE
    )

    # MB
    text = re.sub(
        r"(\d+(?:\.\d+)?)\s*MB",
        r"\1MB",
        text,
        flags=re.IGNORECASE
    )

    # Hz
    text = re.sub(
        r"(\d+(?:\.\d+)?)\s*Hz",
        r"\1Hz",
        text,
        flags=re.IGNORECASE
    )

    # W
    text = re.sub(
        r"(\d+(?:\.\d+)?)\s*W\b",
        r"\1W",
        text,
        flags=re.IGNORECASE
    )

    return text


# ============================================================
# 8. Wi-Fi 統一
# ============================================================
def normalize_wifi(text):

    if not text:
        return ""

    text = re.sub(
        r"wi[\s-]?fi",
        "WIFI",
        text,
        flags=re.IGNORECASE
    )

    return text


# ============================================================
# 9. USB 統一
# ============================================================
def normalize_usb(text):

    if not text:
        return ""

    text = re.sub(
        r"USB\s*([0-9]+(?:\.[0-9]+)?)",
        r"USB \1",
        text,
        flags=re.IGNORECASE
    )

    return text


# ============================================================
# 10. 移除多餘符號
# ============================================================
def remove_extra_symbols(text):

    if not text:
        return ""

    text = re.sub(
        r"[【】\[\]（）()「」『』《》<>]",
        " ",
        text
    )

    text = re.sub(
        r"[,:：;；!?！？]",
        " ",
        text
    )

    return text


# ============================================================
# 11. 空白統一
# ============================================================
def normalize_spaces(text):

    if not text:
        return ""

    text = re.sub(
        r"\s+",
        " ",
        text
    )

    return text.strip()


# ============================================================
# 12. 商品名稱標準化
# ============================================================
def normalize_product_name(product_name):

    if not product_name:
        return ""

    text = product_name

    text = normalize_symbols(text)          # 符號統一
    text = remove_marketing_words(text)     # 移除行銷文字
    text = remove_quantity_words(text)      # 移除銷售數量
    text = normalize_brand_names(text)      # 品牌名稱統一
    text = remove_duplicate_brands(text)    # 移除重複品牌
    text = normalize_size_units(text)       # 尺寸單位統一
    text = normalize_common_units(text)     # 常見單位統一
    text = normalize_wifi(text)             # Wi-Fi 統一
    text = normalize_usb(text)              # USB 統一
    text = remove_extra_symbols(text)       # 移除多餘符號
    text = normalize_spaces(text)           # 空白統一

    return text