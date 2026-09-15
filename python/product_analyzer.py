import re

from models.standard_product import StandardProduct

# =========================================================
# 解析品牌
# =========================================================
BRANDS = [
    "LOGITECH",
    "TP-LINK",
    "SANDISK",
    "ASUS",
    "MSI",
    "RAZER",
    "APPLE",
    "ACER",
    "ADATA",
    "KINGSTON",
    "INTEL",
    "D-LINK",
    "SAMSUNG",
    "XIAOMI",
    "HP",
    "AMD",
    "PHILIPS",
    "TRANSCEND",
    "NVIDIA",
    "GALAX",
    "AOPEN",
    "LENOVO",
    "TEAM",
    "VIEWSONIC",
    "SONY",
    "WD",
    "LG",
    "AOC",
    "BENQ",
    "CREATIVE",
    "CODEWAY",
    "CAMEL",
    "COX",
    "CCHING",
    "AOTTO",
    "ANTIAN",
    "ADAMOUTDOOR",
    "AOLION",
    "AERIVO",
    "ADAM ELEMENTS",
    "B100",
    "BEASAF",
    "BASEMO",
]

# =========================================================
# 品牌中文名稱對照
# =========================================================
BRAND_DISPLAY_NAMES = {
    "LOGITECH": "羅技",
    "TP-LINK": "TP-Link",
    "SANDISK": "SanDisk",
    "ASUS": "華碩",
    "MSI": "微星",
    "RAZER": "雷蛇",
    "APPLE": "蘋果",
    "ACER": "宏碁",
    "ADATA": "威剛",
    "KINGSTON": "金士頓",
    "INTEL": "英特爾",
    "D-LINK": "友訊",
    "SAMSUNG": "三星",
    "XIAOMI": "小米",
    "HP": "惠普",
    "AMD": "超微",
    "PHILIPS": "飛利浦",
    "TRANSCEND": "創見",
    "NVIDIA": "輝達",
    "GALAX": "影馳",
    "AOPEN": "建碁",
    "LENOVO": "聯想",
    "TEAM": "十銓",
    "VIEWSONIC": "優派",
    "SONY": "索尼",
    "WD": "威騰",
    "LG": "樂金",
    "AOC": "AOC",
    "BENQ": "明基",
    "CREATIVE": "創新科技",
    "CODEWAY": "",
    "CAMEL": "",
    "COX": "",
    "CCHING": "",
    "AOTTO": "",
    "ANTIAN": "",
    "ADAMOUTDOOR": "",
    "AOLION": "",
    "AERIVO": "",
    "ADAM ELEMENTS": "亞果元素",
    "B100": "",
    "BEASAF": "",
    "BASEMO": "",
}

# 非商品品牌 / 零組件品牌
COMPONENT_BRANDS = {
    "NVIDIA",
    "AMD",
    "INTEL",
}


def parse_brand(name):
    name_upper = name.upper()
    candidates = []

    # 嚴格匹配
    for brand in BRANDS:
        pattern = rf"(?<![A-Z0-9]){re.escape(brand)}(?![A-Z0-9])"
        match = re.search(pattern, name_upper, re.IGNORECASE)
        if match:
            candidates.append({
                "brand": brand,
                "position": match.start(),
                "strict": True,
            })

    # 如果有嚴格匹配
    if candidates:
        product_candidates = [
            candidate
            for candidate in candidates
            if candidate["brand"] not in COMPONENT_BRANDS
        ]

        if product_candidates:
            product_candidates.sort(key=lambda x: x["position"])
            return product_candidates[0]["brand"]

        candidates.sort(key=lambda x: x["position"])
        return candidates[0]["brand"]

    # 嚴格匹配找不到 改用寬鬆匹配
    loose_candidates = []
    for brand in BRANDS:
        pattern = rf"(?<![A-Z0-9]){re.escape(brand)}"
        match = re.search(pattern, name_upper, re.IGNORECASE)
        if match:
            loose_candidates.append({"brand": brand, "position": match.start()})

    # 沒找到
    if not loose_candidates:
        return None

    # 排除 CPU / GPU 品牌
    product_candidates = [
        candidate
        for candidate in loose_candidates
        if candidate["brand"] not in COMPONENT_BRANDS
    ]

    if product_candidates:
        product_candidates.sort(key=lambda x: x["position"])
        return product_candidates[0]["brand"]

    # 只剩零組件品牌
    loose_candidates.sort(key=lambda x: x["position"])
    return loose_candidates[0]["brand"]

def get_brand_display_name(brand):
    if not brand:
        return None

    brand = str(brand).strip().upper()

    chinese_name = BRAND_DISPLAY_NAMES.get(brand)

    if chinese_name:
        return f"{brand} {chinese_name}"

    # 找不到中文名稱時，至少保留英文品牌
    return brand

# =========================================================
# 解析系列
# =========================================================
SERIES = [
    "ROG",
    "TUF",
    "FIRE LEGEND",
]


def parse_series(name):
    name_upper = name.upper()

    for series in sorted(SERIES, key=len, reverse=True):
        pattern = rf"(?<![A-Z0-9]){re.escape(series)}(?![A-Z0-9])"
        if re.search(pattern, name_upper):
            return series

    return None


# =========================================================
# 解析商品類型
# =========================================================
PRODUCT_TYPE_RULES = {
    # 配件 / 特殊類型
    "monitor_stand": [
        "螢幕增高架", "螢幕增高器", "螢幕置物架", "螢幕置物架",
        "螢幕支架", "螢幕架", "螢幕手臂", "螢幕支臂",
        "螢幕底座", "螢幕掛架", "螢幕壁掛架", "顯示器支架",
        "顯示器架", "顯示器手臂", "顯示器底座",
    ],
    "screen_protector": [
        "螢幕保護貼", "螢幕保護膜", "螢幕保護玻璃",
        "玻璃保護貼", "鋼化膜",
    ],
    "screen_cleaning": ["螢幕清潔", "螢幕清潔組", "螢幕清潔液", "螢幕擦"],
    "monitor_light": ["螢幕掛燈", "螢幕燈", "顯示器掛燈"],
    "laptop_bag": ["筆電包", "筆電袋", "電腦包", "筆記型電腦包", "筆記本電腦包"],
    "laptop_stand": ["筆電支架", "筆電架", "筆電散熱架", "筆電散熱墊", "筆電底座", "筆電立架"],
    "mouse_pad": ["滑鼠墊", "鼠墊", "電競鼠墊"],
    "keyboard_mouse_combo": ["鍵鼠組", "鍵盤滑鼠組", "鍵盤滑鼠套組", "無線鍵鼠組", "鍵盤滑鼠組合"],
    "storage_enclosure": ["硬碟外接盒", "硬碟盒", "SSD外接盒", "SSD 外接盒", "硬碟座"],
    "hdmi_switch": ["HDMI切換器", "HDMI 切換器", "影音切換器"],
    "wifi_extender": ["訊號延伸器", "WiFi放大器", "WIFI放大器", "無線訊號放大器", "無線訊號延伸器", "網路延伸器"],
    "game_wheel": ["遊戲方向盤", "賽車方向盤"],

    # 遊戲：一定要在一般 SWITCH 規則之前
    "game_console": [
        "SWITCH主機", "SWITCH 2 主機", "NINTENDO SWITCH主機",
        "NINTENDO SWITCH 2", "PS5主機", "PLAYSTATION 5",
        "XBOX主機", "XBOX SERIES X", "XBOX SERIES S",
        "PLAYSTATION PORTAL",
    ],
    "game_controller": [
        "遊戲手把", "遊戲控制器", "無線控制器", "手把",
        "搖桿", "DUALSENSE", "DUALSHOCK", "JOY-CON", "JOYCON",
        "PRO CONTROLLER", "XBOX CONTROLLER",
    ],
    "game_accessory": [
        "遊戲配件", "主機保護套", "主機保護殼", "搖桿帽",
        "遊戲收納包", "掌機收納包", "SWITCH收納包", "SWITCH保護套",
        "SWITCH保護殼", "散熱支架", "主機支架", "遊戲支架",
    ],
    "game_software": [
        "遊戲片", "遊戲軟體", "遊戲光碟",
        "SWITCH遊戲", "SWITCH 遊戲", "NS遊戲", "PS5遊戲",
        "PS4遊戲", "PLAYSTATION遊戲", "XBOX遊戲",
        "遊戲版", "亞中版",
    ],

    # 網路
    "router": ["無線路由器", "路由器", "無線分享器", "分享器"],
    "network_switch": ["網路交換器", "網路交換機", "交換器", "交換機", "NETWORK SWITCH", "網路 SWITCH"],
    "network_adapter": ["無線網路卡", "無線網卡", "網路卡", "網卡", "LAN卡"],
    "network_connector": ["RJ45接頭", "RJ45 水晶頭", "水晶頭", "網路接頭", "網路水晶頭"],

    # 儲存
    "usb_flash_drive": ["USB隨身碟", "USB 隨身碟", "隨身碟", "USB碟"],
    "memory_card": ["記憶卡", "SD卡", "SD 卡", "MICROSD", "MICRO SD"],
    "ssd": ["固態硬碟", "SSD", "固態行動碟", "行動固態硬碟"],
    "hard_drive": ["外接硬碟", "硬碟", "HDD"],

    # 電腦零組件
    "graphics_card": ["顯示卡", "顯卡", "GRAPHICS CARD"],
    "motherboard": ["主機板", "主板", "MOTHERBOARD"],
    "computer_case": ["電腦機殼", "電腦主機殼", "機殼", "PC CASE"],
    "cooling": ["CPU散熱器", "CPU 散熱器", "處理器散熱器", "水冷", "散熱器", "散熱風扇", "機殼風扇"],
    "ram": ["記憶體", "RAM", "DDR4", "DDR5"],
    "cpu": ["中央處理器", "處理器", "CPU"],

    # 輸入設備
    "mouse": ["滑鼠", "鼠標", "TRACKPAD", "觸控板"],
    "keyboard": ["機械鍵盤", "鍵盤"],

    # 電腦 / 顯示器 / 行動裝置
    "monitor": [
        "電腦螢幕", "電腦顯示器", "液晶顯示器",
        "電競螢幕", "護眼螢幕", "曲面螢幕",
        "桌上型螢幕", "可攜式螢幕",
        "顯示器", "螢幕", "MONITOR", "DISPLAY",
    ],
    "laptop": ["筆記型電腦", "筆記本電腦", "筆電", "NOTEBOOK", "LAPTOP", "MACBOOK"],
    "tablet": ["平板電腦", "平板", "IPAD", "TABLET"],
    "phone": ["智慧型手機", "手機", "SMARTPHONE"],

    # 音訊 / 影像
    "speaker": ["藍牙喇叭", "喇叭", "音箱", "SPEAKER"],
    "headphone": ["頭戴式耳機", "無線耳機", "耳機", "耳麥", "HEADPHONE"],
    "microphone": ["麥克風", "MICROPHONE"],
    "webcam": ["網路攝影機", "WEB CAM", "WEBCAM"],
    "camera": ["監視攝影機", "智慧攝影機", "安全攝影機", "嬰兒攝影機", "監視器", "攝影機"],

    # 線材 / 電源
    "cable": [
        "HDMI線", "HDMI 線", "HDMI線材", "DP線", "DP 線",
        "DISPLAYPORT線", "USB線", "USB 線", "傳輸線", "資料線",
        "充電線", "網路線", "電源線", "連接線", "訊號線",
        "印表機線", "TYPE-C線", "TYPE C線", "延長線",
    ],
    "adapter": ["轉接器", "轉接頭", "轉接線", "轉換器"],
    "hub": ["擴充集線器", "USB HUB", "集線器", "HUB"],
    "power_strip": ["延長插座", "延長線組", "電源延長線", "排插", "延長插座"],
    "charger": ["充電器", "電源供應器", "變壓器", "充電頭", "PD充電"],

    # 辦公周邊
    "card_reader": ["讀卡機", "讀卡器", "CARD READER"],
    "drawing_tablet": ["繪圖板", "數位板", "手寫板", "繪圖平板"],
    "presentation_remote": ["簡報筆", "雷射筆", "簡報器", "翻頁筆"],
    "stylus": ["觸控筆", "手寫筆", "繪圖筆", "APPLE PENCIL", "PENCIL PRO"],
    "printer": ["印表機"],

    # 其他
    "television": ["智慧電視", "液晶電視", "電視"],
    "wrist_rest": ["護腕墊", "手腕托", "腕托", "護腕"],
    "case": ["收納包", "收納盒", "保護套", "保護殼", "硬殼包"],
    "cable_management": ["束線帶", "魔鬼氈束帶", "理線帶", "理線器"],
    "computer_stand": ["主機滑板", "電腦主機架", "主機架"],
    "software": ["MICROSOFT 365", "WINDOWS 11", "WINDOWS 10", "OFFICE"],
    "receiver": ["接收器", "無線接收器"],
}


# 商品類型排除規則
PRODUCT_TYPE_EXCLUDE_RULES = {
    "monitor": [
        "螢幕支架", "螢幕架", "螢幕增高架", "螢幕桌",
        "螢幕掛燈", "螢幕燈", "螢幕壁掛架", "螢幕手臂",
        "螢幕支臂", "螢幕底座", "螢幕遮光罩",
        "螢幕保護貼", "螢幕保護膜", "螢幕清潔",
        "螢幕清潔組", "螢幕增高器", "螢幕置物架",
    ],
    "router": ["路由器支架", "路由器收納", "路由器掛架"],
    "keyboard": ["鍵盤膜", "鍵盤保護膜", "鍵盤清潔", "鍵盤托", "鍵盤架", "鍵鼠組", "鍵盤滑鼠組"],
    "mouse": ["滑鼠墊", "滑鼠貼", "滑鼠腳貼", "滑鼠收納", "滑鼠架", "鍵鼠組"],
    "laptop": [
        "筆電支架", "筆電架", "筆電包", "筆電內袋",
        "筆電保護套", "筆電散熱架", "筆電散熱墊",
        "電腦包", "電腦支架", "筆電底座",
    ],
    "ssd": ["SSD外接盒", "SSD 外接盒"],
    "hard_drive": ["硬碟外接盒", "硬碟盒", "硬碟座"],
    "camera": ["攝影機支架", "攝影機架", "攝影機保護套"],
    "tablet": [
        "平板皮套", "平板保護套", "平板保護殼", "平板套",
        "平板支架", "平板鍵盤", "平板觸控筆", "APPLE PENCIL",
        "觸控筆", "手寫筆", "PENCIL",
    ],
    "game_software": ["遊戲主機", "主機", "手把", "控制器", "搖桿"],
    "cable": ["電源延長線", "延長插座", "排插"],
}

# =========================================================
# 商品類型中文名稱
# =========================================================
PRODUCT_TYPE_DISPLAY_NAMES = {
    "monitor_stand": "螢幕支架",
    "screen_protector": "螢幕保護貼",
    "screen_cleaning": "螢幕清潔用品",
    "monitor_light": "螢幕掛燈",

    "laptop_bag": "筆電包",
    "laptop_stand": "筆電支架",

    "mouse_pad": "滑鼠墊",
    "keyboard_mouse_combo": "鍵鼠組",

    "storage_enclosure": "硬碟外接盒",
    "hdmi_switch": "HDMI切換器",
    "wifi_extender": "WiFi訊號延伸器",

    "game_wheel": "遊戲方向盤",
    "game_console": "遊戲主機",
    "game_controller": "遊戲控制器",
    "game_accessory": "遊戲配件",
    "game_software": "遊戲軟體",

    "router": "路由器",
    "network_switch": "網路交換器",
    "network_adapter": "網路卡",
    "network_connector": "網路接頭",

    "usb_flash_drive": "USB隨身碟",
    "memory_card": "記憶卡",
    "ssd": "固態硬碟",
    "hard_drive": "硬碟",

    "graphics_card": "顯示卡",
    "motherboard": "主機板",
    "computer_case": "電腦機殼",
    "cooling": "散熱器",
    "ram": "記憶體",
    "cpu": "處理器",

    "mouse": "滑鼠",
    "keyboard": "鍵盤",

    "monitor": "螢幕",
    "laptop": "筆記型電腦",
    "tablet": "平板電腦",
    "phone": "手機",

    "speaker": "喇叭",
    "headphone": "耳機",
    "microphone": "麥克風",
    "webcam": "網路攝影機",
    "camera": "攝影機",

    "cable": "線材",
    "adapter": "轉接器",
    "hub": "集線器",
    "power_strip": "延長插座",
    "charger": "充電器",

    "card_reader": "讀卡機",
    "drawing_tablet": "繪圖板",
    "presentation_remote": "簡報筆",
    "stylus": "觸控筆",
    "printer": "印表機",

    "television": "電視",
    "wrist_rest": "護腕墊",
    "case": "保護套",
    "cable_management": "理線用品",
    "computer_stand": "電腦主機架",
    "software": "軟體",
    "receiver": "無線接收器",
}


def _contains_any(text, keywords):
    return any(keyword.upper() in text for keyword in keywords)


def parse_product_type(name):
    if not name:
        return None

    name_upper = str(name).upper().strip()

    # 筆電主體優先於名稱中的 SSD / RAM / CPU / RTX 等規格詞
    laptop_primary_keywords = ["筆記型電腦", "筆記本電腦", "筆電", "NOTEBOOK", "LAPTOP", "MACBOOK"]
    if _contains_any(name_upper, laptop_primary_keywords):
        return "laptop"

    # Apple Pencil 配件不能因為「APPLE PENCIL」字樣直接判成 stylus
    apple_pencil_accessory_keywords = [
        "保護殼", "保護套", "保護膜", "筆尖", "替換筆尖",
        "筆套", "收納槽", "收納套", "收納盒", "配件",
        "支援 APPLE PENCIL", "適用 APPLE PENCIL", "相容 APPLE PENCIL",
    ]

    # 真正的 Apple Pencil 本體
    if "APPLE PENCIL" in name_upper:
        if not _contains_any(name_upper, apple_pencil_accessory_keywords):
            return "stylus"

    # ---------------------------------------------------------
    # 第一層：最具體商品 / 配件
    # ---------------------------------------------------------
    priority_types = [
        # 輸入 / 手寫配件
        "stylus",
        "drawing_tablet",
        # 螢幕配件
        "monitor_stand",
        "screen_protector",
        "screen_cleaning",
        "monitor_light",
        # 筆電配件
        "laptop_bag",
        "laptop_stand",
        # 滑鼠 / 鍵盤配件
        "mouse_pad",
        "keyboard_mouse_combo",
        # 儲存 / 影音特殊配件
        "storage_enclosure",
        "hdmi_switch",
        # 網路設備
        "wifi_extender",
        "network_switch",
        "network_adapter",
        "network_connector",
        # 遊戲
        "game_wheel",
        "game_console",
        "game_controller",
        "game_accessory",
        "game_software",
    ]

    for product_type in priority_types:
        if product_type == "stylus" and "APPLE PENCIL" in name_upper:
            if _contains_any(name_upper, apple_pencil_accessory_keywords):
                continue

        if _contains_any(name_upper, PRODUCT_TYPE_RULES.get(product_type, [])):
            return product_type

    # ---------------------------------------------------------
    # 第二層：SWITCH 語意判斷
    # 「SWITCH」本身不能直接當成商品類型
    # ---------------------------------------------------------
    if "SWITCH" in name_upper:
        if _contains_any(name_upper, [
            "遊戲片", "遊戲軟體", "遊戲", "瑪利歐", "MARIO",
            "寶可夢", "POKEMON", "薩爾達", "ZELDA",
            "斯普拉遁", "SPLATOON", "任天堂明星大亂鬥",
        ]):
            return "game_software"

        if _contains_any(name_upper, [
            "手把", "控制器", "JOYCON", "JOY-CON", "PRO CONTROLLER",
        ]):
            return "game_controller"

        if _contains_any(name_upper, [
            "主機", "LITE", "OLED", "SWITCH 2",
        ]) and not _contains_any(name_upper, [
            "遊戲", "遊戲片", "遊戲軟體",
        ]):
            return "game_console"

        if _contains_any(name_upper, [
            "收納", "保護套", "保護殼", "支架", "底座",
            "散熱", "搖桿帽", "配件",
        ]):
            return "game_accessory"

    # ---------------------------------------------------------
    # 第三層：排除主商品的配件
    # ---------------------------------------------------------
    excluded_types = set()

    for product_type, exclude_keywords in PRODUCT_TYPE_EXCLUDE_RULES.items():
        if _contains_any(name_upper, exclude_keywords):
            excluded_types.add(product_type)

    # ---------------------------------------------------------
    # 第四層：一般商品
    # ---------------------------------------------------------
    for product_type, keywords in PRODUCT_TYPE_RULES.items():
        if product_type in priority_types:
            continue

        if product_type in excluded_types:
            continue

        if _contains_any(name_upper, keywords):
            return product_type

    return None

def get_product_type_display_name(product_type):
    if not product_type:
        return None

    return PRODUCT_TYPE_DISPLAY_NAMES.get(
        str(product_type).strip(),
        str(product_type).strip()
    )


# =========================================================
# 解析螢幕尺寸
# =========================================================
def parse_screen_size(name):
    match = re.search(r"(\d+(?:\.\d+)?)\s*吋", name, re.IGNORECASE)
    if match:
        return float(match.group(1))
    return None


# =========================================================
# 解析解析度
# =========================================================
RESOLUTIONS = [
    "8K",
    "6K",
    "5K",
    "4K",
    "WQHD",
    "QHD",
    "UHD",
    "FHD",
    "2K",
    "HD",
]


def parse_resolution(name):
    for resolution in RESOLUTIONS:
        if re.search(
            rf"(?<![A-Z0-9]){re.escape(resolution)}(?![A-Z0-9])",
            name,
            re.IGNORECASE,
        ):
            return resolution.upper()
    return None


# =========================================================
# 解析面板
# =========================================================
PANELS = [
    "OLED",
    "AMOLED",
    "IPS",
    "VA",
    "TN",
]


def parse_panel(name):
    for panel in PANELS:
        if re.search(
            rf"(?<![A-Z]){re.escape(panel)}(?![A-Z])",
            name,
            re.IGNORECASE,
        ):
            return panel
    return None


# =========================================================
# 解析刷新率
# =========================================================
def parse_refresh_rate(name):
    match = re.search(r"(\d+(?:\.\d+)?)\s*HZ", name, re.IGNORECASE)
    if match:
        return float(match.group(1))
    return None


# =========================================================
# 解析反應時間
# =========================================================
def parse_response_time(name):
    match = re.search(r"(\d+(?:\.\d+)?)\s*MS", name, re.IGNORECASE)
    if match:
        return float(match.group(1))
    return None


# =========================================================
# 解析 RAM
# =========================================================
def parse_ram(name):
    patterns = [
        r"(\d+(?:\.\d+)?)\s*GB\s*(?:RAM|DDR4|DDR5)",
        r"RAM\s*(\d+(?:\.\d+)?)\s*GB",
        r"(\d+(?:\.\d+)?)\s*GB\s*記憶體",
    ]

    for pattern in patterns:
        match = re.search(pattern, name, re.IGNORECASE)
        if match:
            return float(match.group(1))

    return None


# =========================================================
# 解析儲存容量
# =========================================================
def parse_storage(name):
    results = []
    matches = re.finditer(r"(\d+(?:\.\d+)?)\s*(GB|TB)", name, re.IGNORECASE)

    for match in matches:
        value = float(match.group(1))
        unit = match.group(2).upper()
        results.append({
            "value": value,
            "unit": unit,
        })

    return results


# =========================================================
# 解析 Wi-Fi
# =========================================================
def parse_wifi(name):
    match = re.search(r"WIFI\s*(\d+(?:E)?)", name, re.IGNORECASE)
    if match:
        return match.group(1).upper()
    return None


# =========================================================
# 解析無線網路等級
# =========================================================
def parse_wifi_class(name):
    patterns = [
        r"\bAX(\d+)\b",
        r"\bBE(\d+)\b",
        r"\bAC(\d+)\b",
        r"\bN(\d+)\b",
    ]

    for pattern in patterns:
        match = re.search(pattern, name, re.IGNORECASE)
        if match:
            return match.group(0).upper()

    return None


# =========================================================
# 解析介面
# =========================================================
INTERFACE_PATTERNS = {
    "TYPE-C": r"TYPE[\s-]*C",
    "USB": r"\bUSB\b",
    "HDMI": r"\bHDMI\b",
    "MINI HDMI": r"MINI[\s-]*HDMI",
    "MICRO HDMI": r"MICRO[\s-]*HDMI",
    "DISPLAYPORT": r"DISPLAY[\s-]*PORT",
    "VGA": r"\bVGA\b",
    "LAN": r"\bLAN\b",
}


def parse_interfaces(name):
    interfaces = []

    for interface, pattern in INTERFACE_PATTERNS.items():
        if re.search(pattern, name, re.IGNORECASE):
            interfaces.append(interface)

    return interfaces


# =========================================================
# 解析 USB 版本
# =========================================================
def parse_usb_versions(name):
    versions = []
    matches = re.finditer(r"USB\s*(\d+(?:\.\d+)?)", name, re.IGNORECASE)

    for match in matches:
        version = match.group(1)
        if version not in versions:
            versions.append(version)

    return versions


# =========================================================
# 解析顏色
# =========================================================
COLORS = [
    "黑色", "黑",
    "白色", "白",
    "銀色", "銀",
    "灰色", "灰",
    "藍色", "藍",
    "紅色", "紅",
    "綠色", "綠",
    "金色", "金",
    "粉色", "粉",
    "紫色", "紫",
]


def parse_color(text: str):
    for color in COLORS:
        if color in text:
            return color

    return None


# =========================================================
# 解析 Speaker
# =========================================================
def parse_speaker(name):
    keywords = [
        "喇叭",
        "內建喇叭",
        "內置喇叭",
        "SPEAKER",
    ]

    for keyword in keywords:
        if keyword.upper() in name.upper():
            return True

    return False


# =========================================================
# Model Parser
# =========================================================
MODEL_PATTERNS = [
    # TP-Link / D-Link Router
    r"\bRT-[A-Z0-9]+(?:-[A-Z0-9]+)*\b",
    r"\bARCHER\s*[-]?\s*[A-Z0-9]+(?:-[A-Z0-9]+)*\b",
    # Samsung / Apple 等 Part Number
    r"\bSM-[A-Z0-9]+(?:-[A-Z0-9]+)*\b",
    r"\b[A-Z0-9]{2,8}[A-Z]{2}/[A-Z]\b",
    # 一般型號：例如 27G11ZE2、AL14-36P-C0HB、G703
    r"\b[A-Z]{1,8}\d{2,}[A-Z0-9-]*\b",
    # 例如 A7、X1、C64
    r"\b[A-Z]\d{1,3}\b",
    # 例如 G300-BL、K380-MK2
    r"\b[A-Z]{1,8}\d{1,}[A-Z0-9]*(?:-[A-Z0-9]+)+\b",
]

# 明確不是 Model 的規格
INVALID_MODEL_TOKENS = {
    # Resolution
    "HD", "FHD", "2K", "QHD", "WQHD", "UHD", "4K", "5K", "6K", "8K",
    # HDR
    "HDR", "HDR10", "HDR10+", "HDR400", "HDR600", "HDR1000",
    # Panel
    "IPS", "VA", "TN", "OLED", "AMOLED",
    # Network
    "WIFI", "WIFI4", "WIFI5", "WIFI6", "WIFI6E", "WIFI7",
    # Interface
    "USB", "USB2", "USB3", "USB3.0", "USB3.1", "USB3.2",
    "HDMI", "VGA", "LAN", "TYPE-C", "USB-TYPE-C",
    # Memory
    "DDR3", "DDR4", "DDR5",
    # Storage / SD speed class
    "U1", "U3", "V10", "V30", "V60", "V90", "A1", "A2",
    # CPU
    "I3", "I5", "I7", "I9", "RYZEN3", "RYZEN5", "RYZEN7", "RYZEN9",
    # GPU
    "RTX", "GTX", "RX",
}

# 出現時通常不是 Model
INVALID_MODEL_WORDS = {
    "GAMING", "MONITOR", "DISPLAY", "MOUSE", "KEYBOARD",
    "LAPTOP", "TABLET", "PHONE", "ROUTER", "WIRELESS", "BLUETOOTH",
    # 行銷名稱
    "PRO", "ULTRA", "MAX", "MINI", "PLUS",
    # 顏色
    "BLACK", "WHITE", "SILVER", "GRAY", "GREY",
    # 活動 / 系列標記，不應單獨成為 Model
    "X24",
    # 規格
    "AC1200", "AC1300", "AC1350", "AC1500", "AC1750", "AC1900",
    "AC2100", "AC2200", "AC2300", "AC2400", "AC2600", "AC3000",
    "AC4000", "AC5000",
    "AX1200", "AX1500", "AX1800", "AX3000", "AX3600", "AX4200",
    "AX5400", "AX6000", "AX6600", "AX7800", "AX11000",
    "BE3600", "BE5000", "BE6500", "BE7200", "BE9300", "BE10000",
}


# 取得 Model 候選
def get_model_candidates(name):
    candidates = []

    # ---------------------------------------------------------
    # 先抓「完整產品系列 / 型號」
    # 這些候選優先於後面的短型號，避免：
    # Galaxy Tab S10 FE -> S10
    # G502 X PLUS -> G502
    # ---------------------------------------------------------
    full_patterns = [
        # Samsung Galaxy Tab
        r"\bGALAXY\s+TAB\s+[A-Z0-9]+(?:\s+(?:FE|LITE|PLUS|ULTRA|PRO|ACTIVE|SE|5G|WIFI))*(?![A-Z0-9])",
        # Logitech G 系列，例如 G502 X PLUS / G502 HERO
        r"\bG\d{3,4}(?:\s+(?:X|HERO|LIGHTSPEED|WIRELESS|PLUS|SE|PRO))+(?:\s+(?:PLUS|SE|PRO))?",
        # 常見完整型號：字母 + 數字 + 後綴
        r"\b[A-Z]{1,8}\d{2,}[A-Z0-9]*(?:-[A-Z0-9]+)+\b",
        # 27G11ZE2 / 22CL1Q / 16PM1Q
        r"\b\d{2}[A-Z]\d+[A-Z0-9-]*\b",
        # MSI MAG 完整型號，例如 MAG 255F、MAG 272PF、MAG 272UP QD-OLED
        r"\bMAG\s+\d{3,4}[A-Z0-9]*(?:\s+(?:QD-OLED|OLED|PLUS|MAX|CURVED))?\b",
        # Samsung / Apple Part Number
        r"\bSM-[A-Z0-9]+(?:-[A-Z0-9]+)*\b",
        r"\b[A-Z0-9]{2,8}[A-Z]{2}/[A-Z]\b",
        # TP-Link / Router
        r"\bRT-[A-Z0-9]+(?:-[A-Z0-9]+)*\b",
        r"\bARCHER\s*[-]?\s*[A-Z0-9]+(?:-[A-Z0-9]+)*\b",
    ]

    for pattern in full_patterns:
        for match in re.findall(pattern, name, re.IGNORECASE):
            model = match.strip().upper()
            if not model:
                continue

            # 規格不能當 Model
            if re.fullmatch(r"(AC|AX|BE)\d{3,5}", model):
                continue
            if re.fullmatch(r"(U[13]|V(10|30|60|90)|A[12])", model):
                continue
            if re.fullmatch(r"(USB|HDMI|DP|VGA)\d*(\.\d+)?", model):
                continue
            if re.fullmatch(r"\d+(?:\.\d+)?(MB|GB|TB|HZ|MS|W)", model):
                continue
            if re.fullmatch(r"\d+(?:MB/S|GB/S)", model):
                continue

            candidates.append(model)

    # ---------------------------------------------------------
    # 再抓原有 MODEL_PATTERNS
    # ---------------------------------------------------------
    for pattern in MODEL_PATTERNS:
        matches = re.findall(pattern, name)
        for match in matches:
            if isinstance(match, tuple):
                match = match[0]

            model = match.strip().upper()
            if not model:
                continue

            if re.fullmatch(r"(AC|AX|BE)\d{3,5}", model):
                continue
            if re.fullmatch(r"(U[13]|V(10|30|60|90)|A[12])", model):
                continue
            if re.fullmatch(r"(USB|HDMI|DP|VGA)\d*(\.\d+)?", model):
                continue
            if re.fullmatch(r"\d+(?:\.\d+)?(MB|GB|TB|HZ|MS|W)", model):
                continue
            if re.fullmatch(r"\d+(?:MB/S|GB/S)", model):
                continue

            candidates.append(model)

    # 去重並保留較完整候選
    return list(dict.fromkeys(candidates))


# =========================================================
# 商品識別：規格型 Token 判斷
# =========================================================
def is_specification_token(model):
    model = model.upper().strip()

    # 速度
    if re.fullmatch(r"\d+(?:MB/S|GB/S)", model):
        return True

    # 網路等級
    if re.fullmatch(r"(AC|AX|BE)\d{3,5}", model):
        return True

    # 記憶卡速度等級
    if re.fullmatch(r"(U[13]|V(10|30|60|90)|A[12])", model):
        return True

    # 容量
    if re.fullmatch(r"\d+(?:\.\d+)?(GB|TB)", model):
        return True

    # 螢幕 / 電源規格
    if re.fullmatch(r"\d+(?:\.\d+)?(HZ|MS|W)", model):
        return True

    return False


# 判斷是否為規格
def is_invalid_model(model):
    model = model.upper().strip()

    if is_specification_token(model):
        return True

    if model in INVALID_MODEL_TOKENS or model in INVALID_MODEL_WORDS:
        return True

    # HDR 類
    if re.fullmatch(r"HDR\d*\+?", model):
        return True

    # WiFi 類
    if re.fullmatch(r"WIFI\d*", model):
        return True

    # DDR 類
    if re.fullmatch(r"DDR[345]", model):
        return True

    # V10 / V30 / V60 / V90
    if re.fullmatch(r"V(10|30|60|90)", model):
        return True

    # A1 / A2
    if re.fullmatch(r"A[12]", model):
        return True

    # CPU：N4500、N100、N200、I5-14450HX 等
    if re.fullmatch(r"(N|J)\d{2,5}", model):
        return True

    if re.fullmatch(r"I[3579]-?\d{4,6}[A-Z]*", model):
        return True

    # Ryzen 5 / Ryzen 7 類
    if re.fullmatch(r"RYZEN[3579]", model):
        return True

    return False


def score_model(model, name, product_type=None, brand=None):
    model_upper = model.upper()
    name_upper = name.upper()
    score = 0

    # 1. 基本條件
    if any(c.isdigit() for c in model):
        score += 2

    if any(c.isalpha() for c in model) and any(c.isdigit() for c in model):
        score += 3

    if "-" in model:
        score += 2

    if "/" in model:
        score += 4

    # 2. 明確排除
    if is_invalid_model(model):
        score -= 100

    # 3. Router
    if product_type == "router":
        if re.fullmatch(r"RT-[A-Z0-9-]+", model_upper):
            score += 20

        if re.fullmatch(r"ARCHER[- ]?[A-Z0-9-]+", model_upper):
            score += 20

        # C64 / AX12 / BE5500 等
        if re.fullmatch(r"[A-Z]{1,4}\d{1,5}", model_upper):
            score += 8

        # AC1200 / AX1500 是 WiFi 等級，不是 Model
        if re.fullmatch(r"(AC|AX|BE)\d{3,5}", model_upper):
            score -= 30

    # 4. Laptop
    elif product_type == "laptop":
        # Acer AL14-36P-C0HB
        if re.fullmatch(r"[A-Z]{2,6}\d{2,}[A-Z0-9-]*", model_upper):
            score += 15

        # 排除 Intel CPU
        if re.fullmatch(r"(I[3579]|N|J)\d{2,6}[A-Z]*", model_upper):
            score -= 40

        # RTX / GTX
        if re.fullmatch(r"(RTX|GTX|RX)\d{3,5}[A-Z]*", model_upper):
            score -= 40

    # 5. Monitor
    elif product_type == "monitor":
        # 例如 27G11ZE2
        if re.fullmatch(r"\d{2}[A-Z]\d+[A-Z0-9]*", model_upper):
            score += 15

        # 一般 AOC / ASUS / MSI 型號
        if re.fullmatch(r"[A-Z]{1,8}\d{2,}[A-Z0-9-]*", model_upper):
            score += 10

        # HDR / resolution 不應該成為 Model
        if model_upper.startswith("HDR"):
            score -= 50

    # 6. Storage
    elif product_type in {"ssd", "hard_drive", "usb_flash_drive", "memory_card"}:
        # 優先有品牌前綴的 Model
        if re.fullmatch(r"[A-Z]{1,8}\d{2,}[A-Z0-9-]*", model_upper):
            score += 8

        # V30 / U3 / A1 等速度規格
        if re.fullmatch(r"(U[13]|V(10|30|60|90)|A[12])", model_upper):
            score -= 50

    # 7. Mouse
    elif product_type == "mouse":
        # Logitech G703 / G502 / M720
        if re.fullmatch(r"[A-Z]{1,5}\d{2,}[A-Z0-9-]*", model_upper):
            score += 12

    # 8. Keyboard
    elif product_type == "keyboard":
        if re.fullmatch(r"[A-Z]{1,8}\d{2,}[A-Z0-9-]*", model_upper):
            score += 12

    # 9. Apple
    if brand == "APPLE":
        # Apple A16 / M2 / M3 等不是產品 Model
        if re.fullmatch(r"[AM]\d{1,2}", model_upper):
            score -= 20

        # Apple Part Number
        if re.fullmatch(r"[A-Z0-9]{2,8}[A-Z]{2}/[A-Z]", model_upper):
            score += 20

    # 10. Samsung
    if brand == "SAMSUNG":
        # SM-X230、SM-S928B
        if model_upper.startswith("SM-"):
            score += 25

    # 11. 出現位置
    position = name_upper.find(model_upper)
    if position >= 0:
        # Model 越早出現，通常越有價值
        name_length = max(len(name_upper), 1)
        ratio = position / name_length

        if ratio < 0.30:
            score += 5
        elif ratio < 0.50:
            score += 2

    # 12. 太短的候選降低分數
    if len(model_upper) <= 2:
        score -= 5

    return score


def parse_model(name, product_type=None, brand=None):
    if not name:
        return None

    name = name.upper().strip()
    candidates = get_model_candidates(name)

    # Apple Pencil：把產品線名稱保留為可比對特徵
    if brand == "APPLE":
        apple_matches = re.findall(
            r"(APPLE\s+PENCIL(?:\s+PRO|\s+\d(?:ST|ND|RD|TH)?\s+GENERATION)?)",
            name,
            re.IGNORECASE,
        )
        for match in apple_matches:
            candidates.append(match.strip().upper())

    # Samsung Galaxy Tab：避免只抓到 S10 / S9 等過短片段
    samsung_tab = re.search(
        r"(GALAXY\s+TAB\s+[A-Z0-9]+(?:\s+(?:FE|LITE|PLUS|ULTRA|PRO|ACTIVE|SE|5G|WIFI))*(?![A-Z0-9]))",
        name,
        re.IGNORECASE,
    )
    if samsung_tab:
        candidates.append(samsung_tab.group(1).strip().upper())

    candidates = list(dict.fromkeys(candidates))

    if not candidates:
        return None

    scored_candidates = []

    for model in candidates:
        if is_invalid_model(model):
            continue

        score = score_model(model, name, product_type, brand)
        scored_candidates.append((model, score))

    if not scored_candidates:
        return None

    # 完整產品系列優先。
    def candidate_priority(item):
        model_value, score_value = item
        specificity_bonus = 0

        if "GALAXY TAB" in model_value:
            specificity_bonus += 30

        if re.search(r"\bG\d{3,4}\s+(?:X|HERO|LIGHTSPEED|WIRELESS|PLUS|SE|PRO)", model_value):
            specificity_bonus += 25

        # MSI MAG 完整型號優先於 X24 等短標記
        if re.search(r"\bMAG\s+\d{3,4}[A-Z0-9]*", model_value):
            specificity_bonus += 30

        # 含有空白的完整系列通常比單一短 token 更具辨識力
        if " " in model_value:
            specificity_bonus += min(len(model_value), 20)

        return (score_value + specificity_bonus, len(model_value))

    scored_candidates.sort(key=candidate_priority, reverse=True)
    return scored_candidates[0][0]


# =========================================================
# Monitor Parser
# =========================================================
def parse_monitor_specs(name):
    return {
        "screen_size": parse_screen_size(name),
        "resolution": parse_resolution(name),
        "panel": parse_panel(name),
        "refresh_rate": parse_refresh_rate(name),
        "response_time": parse_response_time(name),
        "interfaces": parse_interfaces(name),
        "speaker": parse_speaker(name),
        "color": parse_color(name),
    }


# =========================================================
# Router Parser
# =========================================================
def parse_router_specs(name):
    return {
        "wifi": parse_wifi(name),
        "wifi_class": parse_wifi_class(name),
        "interfaces": parse_interfaces(name),
    }


# =========================================================
# Storage Parser
# =========================================================
def parse_storage_specs(name):
    return {
        "storage": parse_storage(name),
        "usb_versions": parse_usb_versions(name),
        "interfaces": parse_interfaces(name),
    }


# =========================================================
# 建立 StandardProduct
# =========================================================
def parse_product(name):
    if not name:
        return None

    name = str(name).strip()

    # ---------------------------------------------------------
    # 分析商品基本資料
    # ---------------------------------------------------------
    brand = parse_brand(name)
    series = parse_series(name)
    product_type = parse_product_type(name)
    model = parse_model(name, product_type, brand)

    # ---------------------------------------------------------
    # 建立商品規格
    # ---------------------------------------------------------
    screen_size = None
    resolution = None
    panel = None
    refresh_rate = None
    response_time = None

    ram = parse_ram(name)
    storage = []

    wifi = None
    wifi_class = None

    usb_versions = []
    interfaces = []

    color = parse_color(name)
    speaker = False

    # Monitor
    if product_type == "monitor":
        specs = parse_monitor_specs(name)
        screen_size = specs["screen_size"]
        resolution = specs["resolution"]
        panel = specs["panel"]
        refresh_rate = specs["refresh_rate"]
        response_time = specs["response_time"]
        interfaces = specs["interfaces"]
        speaker = specs["speaker"]

    # Router
    elif product_type == "router":
        specs = parse_router_specs(name)
        wifi = specs["wifi"]
        wifi_class = specs["wifi_class"]
        interfaces = specs["interfaces"]

    # Storage
    elif product_type in ["usb_flash_drive", "memory_card", "ssd", "hard_drive"]:
        specs = parse_storage_specs(name)
        storage = specs["storage"]
        usb_versions = specs["usb_versions"]
        interfaces = specs["interfaces"]

    # 其他商品
    else:
        storage = parse_storage(name)
        usb_versions = parse_usb_versions(name)
        interfaces = parse_interfaces(name)

    # ---------------------------------------------------------
    # 建立 StandardProduct
    # ---------------------------------------------------------
    return StandardProduct(
        brand=brand,
        series=series,
        model=model,
        product_type=product_type,
        screen_size=screen_size,
        resolution=resolution,
        panel=panel,
        refresh_rate=refresh_rate,
        response_time=response_time,
        ram=ram,
        storage=storage,
        wifi=wifi,
        wifi_class=wifi_class,
        usb_versions=usb_versions,
        interfaces=interfaces,
        color=color,
        speaker=speaker,
    )