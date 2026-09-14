class StandardProduct:
    def __init__(
        self,
        brand=None,
        series=None,
        model=None,
        product_type=None,
        screen_size=None,
        resolution=None,
        panel=None,
        refresh_rate=None,
        response_time=None,
        ram=None,
        storage=None,
        wifi=None,
        wifi_class=None,
        usb_versions=None,
        interfaces=None,
        color=None,
        speaker=False
    ):
        # =========================================================
        # 商品基本資料
        # =========================================================

        # 品牌
        self.brand = brand

        # 商品系列
        self.series = series

        # 商品型號
        self.model = model

        # 商品類型
        self.product_type = product_type

        # =========================================================
        # 螢幕規格
        # =========================================================

        # 螢幕尺寸
        self.screen_size = screen_size

        # 解析度
        self.resolution = resolution

        # 面板類型
        self.panel = panel

        # 更新率
        self.refresh_rate = refresh_rate

        # 反應時間
        self.response_time = response_time

        # =========================================================
        # 電腦規格
        # =========================================================

        # RAM
        self.ram = ram

        # 儲存容量
        self.storage = storage

        # =========================================================
        # 網路規格
        # =========================================================

        # Wi-Fi
        self.wifi = wifi

        # Wi-Fi 等級
        self.wifi_class = wifi_class

        # =========================================================
        # 介面規格
        # =========================================================

        # USB 版本
        if usb_versions is None:
            self.usb_versions = []
        else:
            self.usb_versions = usb_versions

        # 其他介面
        if interfaces is None:
            self.interfaces = []
        else:
            self.interfaces = interfaces

        # =========================================================
        # 其他商品資訊
        # =========================================================

        # 顏色
        self.color = color

        # 是否有喇叭
        self.speaker = speaker

    def __str__(self):
        return (
            f"品牌：{self.brand}\n"
            f"系列：{self.series}\n"
            f"Model：{self.model}\n"
            f"商品類型：{self.product_type}\n"
            f"螢幕尺寸：{self.screen_size}\n"
            f"解析度：{self.resolution}\n"
            f"面板：{self.panel}\n"
            f"刷新率：{self.refresh_rate}\n"
            f"反應時間：{self.response_time}\n"
            f"RAM：{self.ram}\n"
            f"儲存容量：{self.storage}\n"
            f"Wi-Fi：{self.wifi}\n"
            f"Wi-Fi 等級：{self.wifi_class}\n"
            f"USB 版本：{self.usb_versions}\n"
            f"介面：{self.interfaces}\n"
            f"顏色：{self.color}\n"
            f"喇叭：{self.speaker}"
        )