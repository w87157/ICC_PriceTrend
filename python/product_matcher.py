from models.standard_product import StandardProduct

# =========================================================
# 取得商品欄位
# =========================================================
def get_value(product, name):
    return getattr(product, name, None)


# =========================================================
# 比對品牌
# =========================================================
def match_brand(product1, product2):
    brand1 = get_value(product1, "brand")
    brand2 = get_value(product2, "brand")

    if not brand1 or not brand2:
        return True

    return brand1.upper() == brand2.upper()


# =========================================================
# 比對系列
# =========================================================
def match_series(product1, product2):
    series1 = get_value(product1, "series")
    series2 = get_value(product2, "series")

    if not series1 or not series2:
        return True

    return series1.upper() == series2.upper()


# =========================================================
# 比對 Model
# =========================================================
def match_model(product1, product2):
    model1 = get_value(product1, "model")
    model2 = get_value(product2, "model")

    # 兩個都有 Model
    if model1 and model2:
        return model1.upper() == model2.upper()

    # 其中一個沒有 Model
    # 暫時不因為缺少 Model 直接判定不同
    return True


# =========================================================
# 比對商品類型
# =========================================================
def match_product_type(product1, product2):
    type1 = get_value(product1, "product_type")
    type2 = get_value(product2, "product_type")

    if not type1 or not type2:
        return True

    return type1 == type2


# =========================================================
# 比對螢幕尺寸
# =========================================================
def match_screen_size(product1, product2):
    size1 = get_value(product1, "screen_size")
    size2 = get_value(product2, "screen_size")

    if size1 is None or size2 is None:
        return True

    return size1 == size2


# =========================================================
# 比對解析度
# =========================================================
def match_resolution(product1, product2):
    resolution1 = get_value(product1, "resolution")
    resolution2 = get_value(product2, "resolution")

    if not resolution1 or not resolution2:
        return True

    return resolution1.upper() == resolution2.upper()


# =========================================================
# 比對 RAM
# =========================================================
def match_ram(product1, product2):
    ram1 = get_value(product1, "ram")
    ram2 = get_value(product2, "ram")

    if ram1 is None or ram2 is None:
        return True

    return ram1 == ram2


# =========================================================
# 比對儲存容量
# =========================================================
def match_storage(product1, product2):
    storage1 = get_value(product1, "storage")
    storage2 = get_value(product2, "storage")

    if not storage1 or not storage2:
        return True

    return storage1 == storage2


# =========================================================
# 比對 Wi-Fi
# =========================================================
def match_wifi(product1, product2):
    wifi1 = get_value(product1, "wifi")
    wifi2 = get_value(product2, "wifi")

    if not wifi1 or not wifi2:
        return True

    return wifi1.upper() == wifi2.upper()


# =========================================================
# 比對 Wi-Fi 等級
# =========================================================
def match_wifi_class(product1, product2):
    wifi_class1 = get_value(product1, "wifi_class")
    wifi_class2 = get_value(product2, "wifi_class")

    if not wifi_class1 or not wifi_class2:
        return True

    return wifi_class1.upper() == wifi_class2.upper()


# =========================================================
# 比對顏色
# =========================================================
def match_color(product1, product2):
    color1 = get_value(product1, "color")
    color2 = get_value(product2, "color")

    if not color1 or not color2:
        return True

    return color1 == color2


# =========================================================
# 比對商品規格
# =========================================================
def match_specs(product1, product2):

    # 螢幕尺寸
    if not match_screen_size(product1, product2):
        return False

    # 解析度
    if not match_resolution(product1, product2):
        return False

    # RAM
    if not match_ram(product1, product2):
        return False

    # 儲存容量
    if not match_storage(product1, product2):
        return False

    # Wi-Fi
    if not match_wifi(product1, product2):
        return False

    # Wi-Fi 等級
    if not match_wifi_class(product1, product2):
        return False

    return True


# =========================================================
# 判斷兩個商品是否相同
# =========================================================
def is_same_product(product1, product2):

    if product1 is None or product2 is None:
        return False

    # ---------------------------------------------------------
    # 1. 商品類型
    # ---------------------------------------------------------

    if not match_product_type(product1, product2):
        return False

    # ---------------------------------------------------------
    # 2. 品牌
    # ---------------------------------------------------------

    if not match_brand(product1, product2):
        return False

    # ---------------------------------------------------------
    # 3. 系列
    # ---------------------------------------------------------

    if not match_series(product1, product2):
        return False

    # ---------------------------------------------------------
    # 4. Model
    # ---------------------------------------------------------

    if not match_model(product1, product2):
        return False

    # ---------------------------------------------------------
    # 5. 商品規格
    # ---------------------------------------------------------

    if not match_specs(product1, product2):
        return False

    # ---------------------------------------------------------
    # 6. 顏色
    # ---------------------------------------------------------

    if not match_color(product1, product2):
        return False

    return True


# =========================================================
# 計算商品相似度
# =========================================================
def calculate_similarity(product1, product2):

    if product1 is None or product2 is None:
        return 0

    score = 0
    total = 0

    # ---------------------------------------------------------
    # 品牌
    # ---------------------------------------------------------

    brand1 = get_value(product1, "brand")
    brand2 = get_value(product2, "brand")

    if brand1 and brand2:
        total += 1

        if brand1.upper() == brand2.upper():
            score += 1

    # ---------------------------------------------------------
    # 系列
    # ---------------------------------------------------------

    series1 = get_value(product1, "series")
    series2 = get_value(product2, "series")

    if series1 and series2:
        total += 1

        if series1.upper() == series2.upper():
            score += 1

    # ---------------------------------------------------------
    # Model
    # ---------------------------------------------------------

    model1 = get_value(product1, "model")
    model2 = get_value(product2, "model")

    if model1 and model2:
        total += 1

        if model1.upper() == model2.upper():
            score += 1

    # ---------------------------------------------------------
    # 商品類型
    # ---------------------------------------------------------

    type1 = get_value(product1, "product_type")
    type2 = get_value(product2, "product_type")

    if type1 and type2:
        total += 1

        if type1 == type2:
            score += 1

    # ---------------------------------------------------------
    # 螢幕尺寸
    # ---------------------------------------------------------

    size1 = get_value(product1, "screen_size")
    size2 = get_value(product2, "screen_size")

    if size1 is not None and size2 is not None:
        total += 1

        if size1 == size2:
            score += 1

    # ---------------------------------------------------------
    # 解析度
    # ---------------------------------------------------------

    resolution1 = get_value(product1, "resolution")
    resolution2 = get_value(product2, "resolution")

    if resolution1 and resolution2:
        total += 1

        if resolution1.upper() == resolution2.upper():
            score += 1

    # ---------------------------------------------------------
    # RAM
    # ---------------------------------------------------------

    ram1 = get_value(product1, "ram")
    ram2 = get_value(product2, "ram")

    if ram1 is not None and ram2 is not None:
        total += 1

        if ram1 == ram2:
            score += 1

    # ---------------------------------------------------------
    # 儲存容量
    # ---------------------------------------------------------

    storage1 = get_value(product1, "storage")
    storage2 = get_value(product2, "storage")

    if storage1 and storage2:
        total += 1

        if storage1 == storage2:
            score += 1

    # ---------------------------------------------------------
    # 沒有可以比較的欄位
    # ---------------------------------------------------------

    if total == 0:
        return 0

    return score / total


# =========================================================
# 商品比對
# =========================================================
def compare_products(product1, product2):

    if product1 is None or product2 is None:
        return {
            "same_product": False,
            "similarity": 0
        }

    similarity = calculate_similarity(product1, product2)

    same_product = is_same_product(product1, product2)

    return {
        "same_product": same_product,
        "similarity": similarity
    }

# =========================================================
# 建立統一商品名稱
# =========================================================
def build_standard_item_name(product):
    if product is None:
        return ""

    parts = []

    brand = get_value(product, "brand")
    series = get_value(product, "series")
    model = get_value(product, "model")

    if brand:
        parts.append(str(brand).strip())

    if series:
        parts.append(str(series).strip())

    if model:
        parts.append(str(model).strip())

    return " ".join(parts)

# =========================================================
# 將相同商品分組
# =========================================================
def group_products(products):
    groups = []

    for product in products:
        standard_product = product["standard_product"]
        matched_group = None

        # 尋找是否已有相同商品群組
        for group in groups:
            if is_same_product(
                standard_product,
                group["standard_product"]
            ):
                matched_group = group
                break

        # 找到相同商品
        if matched_group is not None:
            matched_group["products"].append(product)

        # 找不到 → 建立新的商品群組
        else:
            groups.append(
                {
                    "item_name": build_standard_item_name(
                        standard_product
                    ),
                    "standard_product": standard_product,
                    "products": [product]
                }
            )

    return groups
