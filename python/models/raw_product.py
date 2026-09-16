class RawProduct:
    def __init__(
        self,
        platform,
        platform_item_id=None,
        product_name="",
        price=None,
        url="",
        image_url=None,
        category_name=None
    ):

        # =====================================================
        # 平台資料
        # =====================================================

        # 商品來自哪一個平台
        self.platform = platform

        # 平台自己的商品 ID
        self.platform_item_id = platform_item_id

        # 原始商品名稱
        self.product_name = product_name

        # 商品目前價格
        self.price = price

        # 商品網址
        self.url = url

        # 商品圖片網址
        self.image_url = image_url

        # 商品分類
        self.category_name = category_name
        

    # =========================================================
    # 轉換成 CSV 資料
    # =========================================================
    def to_dict(self):
        return {
            "platform": self.platform,
            "platform_item_id": self.platform_item_id,
            "product_name": self.product_name,
            "price": self.price,
            "url": self.url,
            "image_url": self.image_url,
            "category_name": self.category_name
        }

    # =========================================================
    # 從 CSV 資料建立 RawProduct
    # =========================================================
    @classmethod
    def from_dict(cls, data):
        price = data.get("price")

        if price is not None and price != "":
            try:
                price = float(price)
            except (ValueError, TypeError):
                price = None
        else:
            price = None

        return cls(
            platform=data.get("platform"),
            platform_item_id=data.get("platform_item_id"),
            product_name=data.get("product_name", ""),
            price=price,
            url=data.get("url", ""),
            image_url=data.get("image_url") or None,
            category_name=data.get("category_name")
        )

    # =========================================================
    # 顯示商品資料
    # =========================================================
    def __str__(self):
        return (
            f"平台：{self.platform}\n"
            f"商品 ID：{self.platform_item_id}\n"
            f"商品名稱：{self.product_name}\n"
            f"價格：{self.price}\n"
            f"網址：{self.url}\n"
            f"圖片：{self.image_url}\n"
            f"分類：{self.category_name}"
        )