class RawProduct:
    def __init__(
        self,
        platform,
        platform_item_id=None,
        product_name="",
        price=None,
        url="",
        image_url=None,
        category_name=None,
        raw_data=None
    ):

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

        # 保留其他原始資料
        self.raw_data = raw_data if raw_data is not None else {}


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