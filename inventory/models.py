from inventory.input_normalizer import input_normalize
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator
from django.db import models
from django.utils.translation import gettext_lazy as _
from pykakasi import kakasi
import requests
import urllib.parse


class Drug(models.Model):
    objects = models.Manager()

    class Price(models.TextChoices):
        LOW = "L", _("低 (<¥5000)")
        MEDIUM = "M", _("中 (~¥5000)")
        HIGH = "H", _("高 (>¥5000)")

    name = models.CharField(max_length=50, unique=True,
                            help_text="必須。医薬品一般名。例：チオクト酸静注。", verbose_name="医薬品名")
    kana = models.CharField(max_length=100, unique=True, blank=True, null=True, help_text="自動生成されます。不正確な場合は編集してください。", verbose_name="ふりがな")
    description = models.CharField(max_length=100, blank=True, null=True,
                                   help_text="コメント、注意など。", verbose_name="説明")
    package = models.CharField(max_length=50, blank=True, null=True,
                               help_text="例：500mg/錠 PTP 10錠×10。", verbose_name="包装")
    category = models.ForeignKey('Category', on_delete=models.PROTECT, blank=True, null=True, verbose_name="医薬品種類")
    price = models.CharField(max_length=2, choices=Price, default=Price.LOW, help_text="必須。", verbose_name="値段")
    unit = models.ForeignKey('Unit', on_delete=models.PROTECT, blank=True, null=True,
                             help_text="必須。最小単位優先。確信が持てない場合は、「EA」を選択してください。", verbose_name="単位")
    product_code = models.CharField(max_length=255, blank=True, null=True, verbose_name="商品コード")
    orca_id = models.CharField(max_length=50, blank=True, null=True, verbose_name="ORCA ID")
    date_created = models.DateTimeField(auto_now_add=True, verbose_name="最終更新日時")
    user = models.ForeignKey(User, on_delete=models.PROTECT, verbose_name="最終更新者")
    obsoleted = models.BooleanField(default=False, help_text="廃止された項目は、システムから削除されるわけではありませんが、一般的な操作や検索の対象からは除外されます。", verbose_name="全院で廃止する")

    class Meta:
        ordering = ("id",)

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if self.name:
            self.name = input_normalize(self.name)
            self.package = input_normalize(self.package)

            # Convert Kanji to Kana
            kks = kakasi()
            kks.setMode("J", "H")  # Kanji to Hiragana
            kks.setMode('K', 'H')  # Katanaga to Hiragana
            conv = kks.getConverter()
            self.name_pronunciation = conv.do(self.name)
        super(Drug, self).save(*args, **kwargs)


class InventoryItem(models.Model):
    objects = models.Manager()
    name = models.ForeignKey('Drug', on_delete=models.PROTECT, blank=True, null=True, verbose_name="医薬品名")
    quantity = models.IntegerField(default=0, blank=True, null=True, verbose_name="数量")
    unit = models.ForeignKey('Unit', on_delete=models.PROTECT, blank=True, null=True, verbose_name="単位")
    lot = models.CharField(max_length=200, null=True, verbose_name="製造番号")
    expire_date = models.DateField(null=True, verbose_name="使用期限")
    site = models.ForeignKey('Site', on_delete=models.PROTECT, blank=True, null=True, verbose_name="拠点")
    date_created = models.DateTimeField(auto_now_add=True, verbose_name="最終更新日時")
    user = models.ForeignKey(User, on_delete=models.PROTECT, default=0, verbose_name="最終更新者")

    class Meta:
        ordering = ("id",)

    def __str__(self):
        return f"{self.lot}"


class Transaction(models.Model):
    objects = models.Manager()

    class Type(models.TextChoices):
        INBOUND = "I", _("入庫")
        OUTBOUND = "O", _("出庫")
        TRANSFER = "T", _("拠点間移動")
        ADJUST = "A", _("在庫調整")
        CANCELLED = "C", _("キャンセル")

    class Status(models.TextChoices):
        PENDING = "P", _("未受領")
        RECEIVED = "R", _("受領済み")

    type = models.CharField(max_length=2, choices=Type, default=Type.INBOUND, verbose_name="取引タイプ")
    status = models.CharField(max_length=2, choices=Status.choices, default=Status.RECEIVED,
                              verbose_name="状態")
    name = models.ForeignKey('Drug', on_delete=models.PROTECT, blank=True, null=True, verbose_name="医薬品名")
    quantity = models.IntegerField(default=1, validators=[MinValueValidator(0)], verbose_name="数量")
    unit = models.ForeignKey('Unit', on_delete=models.PROTECT, null=True, verbose_name="単位")
    lot = models.CharField(max_length=200, null=True, verbose_name="製造番号")
    expire_date = models.DateField(null=True, verbose_name="使用期限")
    source_site = models.ForeignKey('Site', on_delete=models.PROTECT, blank=True, null=True,
                                    related_name='source_site', verbose_name="出庫元")
    dest_site = models.ForeignKey('Site', on_delete=models.PROTECT, blank=True, null=True,
                                  related_name='destination_site', verbose_name="入庫先")
    date_created = models.DateTimeField(auto_now_add=True, verbose_name="作成日時")
    user = models.ForeignKey(User, on_delete=models.PROTECT, default=0, verbose_name="作成者")
    source_inventory_adjusted = models.BooleanField(default=False)

    def reverse_source_adjustment(self):
        if self.source_inventory_adjusted:
            source_inventory_items = InventoryItem.objects.filter(
                name=self.name,
                unit=self.unit,
                lot=self.lot,
                site=self.source_site
            )

            for item in source_inventory_items:
                item.quantity += self.quantity
                item.save()

            self.source_inventory_adjusted = False
            self.save()

    class Meta:
        ordering = ("id",)

    def __str__(self):
        return f"{self.lot}"


class Category(models.Model):
    objects = models.Manager()
    name = models.CharField(max_length=50, unique=True, null=True, verbose_name="種類名")
    obsoleted = models.BooleanField(default=False, help_text="廃止された項目は、システムから削除されるわけではありませんが、一般的な操作や検索の対象からは除外されます。", verbose_name="廃止する")
    date_created = models.DateTimeField(auto_now_add=True, verbose_name="作成日時")
    user = models.ForeignKey(User, on_delete=models.PROTECT, default=0, verbose_name="作成者")

    class Meta:
        verbose_name_plural = 'Categories'
        ordering = ("id",)

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if self.name:
            self.name = input_normalize(self.name)
        super(Category, self).save(*args, **kwargs)


class Unit(models.Model):
    objects = models.Manager()
    name = models.CharField(max_length=10, unique=True, null=True, verbose_name="単位")
    date_created = models.DateTimeField(auto_now_add=True, verbose_name="作成日時")
    user = models.ForeignKey(User, on_delete=models.PROTECT, default=0, verbose_name="作成者")

    class Meta:
        ordering = ("id",)

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if self.name:
            self.name = input_normalize(self.name)
        super(Unit, self).save(*args, **kwargs)


class Site(models.Model):
    objects = models.Manager()
    name = models.CharField(max_length=100, unique=True, null=True, verbose_name="拠点名")
    address = models.CharField(max_length=255, blank=True, null=True, verbose_name="住所")
    latitude = models.DecimalField(max_digits=9, decimal_places=6, blank=True, null=True, help_text="自動追加", verbose_name="緯度")
    longitude = models.DecimalField(max_digits=9, decimal_places=6, blank=True, null=True, help_text="自動追加", verbose_name="経度")
    color = models.CharField(max_length=20, blank=True, null=True, help_text="16進数カラーコード。例：#3B4252。", verbose_name="テーマ色")
    obsoleted = models.BooleanField(default=False, help_text="廃止された項目は、システムから削除されるわけではありませんが、一般的な操作や検索の対象からは除外されます。", verbose_name="廃止する")
    date_created = models.DateTimeField(auto_now_add=True, verbose_name="作成日時")
    user = models.ForeignKey(User, on_delete=models.PROTECT, default=0, verbose_name="作成者")

    class Meta:
        ordering = ("id",)

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if self.name:
            self.name = input_normalize(self.name)
            self.address = input_normalize(self.address)

            if self.address and (self.latitude is None or self.longitude is None):
                base_url = "https://msearch.gsi.go.jp/address-search/AddressSearch?q="
                encoded_address = urllib.parse.quote(self.address)
                full_url = base_url + encoded_address

                response = requests.get(full_url)
                results = response.json()

                if results:
                    longitude, latitude = results[0]["geometry"]["coordinates"]
                    self.longitude = longitude
                    self.latitude = latitude

        super(Site, self).save(*args, **kwargs)


class UserProfile(models.Model):
    objects = models.Manager()
    user = models.OneToOneField(User, on_delete=models.PROTECT)
    scanner_mode_enabled = models.BooleanField(default=True, verbose_name="デフォルトでスキャナーモードが有効")
    default_site = models.ForeignKey('Site', on_delete=models.PROTECT, blank=True, null=True, help_text="ログイン後にユーザーのデフォルトの拠点。", verbose_name="デフォルトの拠点")
    default_sort_field = models.CharField(max_length=255, default='date_created',
                                          verbose_name="デフォルトの並べ替えのキー")
    default_sort_order = models.CharField(max_length=4,
                                          choices=[('asc', '昇順'), ('desc', '降順')],
                                          default='desc', verbose_name="デフォルトの並べ替え順序")

    class Meta:
        ordering = ("id",)


class SafetyStock(models.Model):
    objects = models.Manager()
    drug = models.ForeignKey('Drug', on_delete=models.PROTECT, verbose_name="医薬品名")
    site = models.ForeignKey('Site', on_delete=models.PROTECT, verbose_name="拠点")
    min_stock = models.IntegerField(default=1, validators=[MinValueValidator(0)], verbose_name="安全在庫数（定数）")

    class Meta:
        unique_together = ('drug', 'site')
        ordering = ("drug", "site")


class InventoryInspection(models.Model):
    objects = models.Manager()
    site = models.ForeignKey('Site', on_delete=models.PROTECT, null=True, verbose_name="拠点")
    data = models.JSONField(blank=True, null=True, verbose_name="確認データ")
    inventory_adjusted = models.BooleanField(default=False, verbose_name="在庫調整済み")
    date_created = models.DateTimeField(auto_now_add=True, verbose_name="確認日時")
    user = models.ForeignKey(User, on_delete=models.PROTECT, verbose_name="確認者")

    class Meta:
        ordering = ("id",)


class DrugObsoleteBySite(models.Model):
    objects = models.Manager()
    drug = models.ForeignKey(Drug, on_delete=models.PROTECT, related_name='obsolete_status')
    site = models.ForeignKey(Site, on_delete=models.PROTECT)
    is_obsolete = models.BooleanField(default=False, verbose_name="廃止する")

    class Meta:
        unique_together = ('drug', 'site')
        ordering = ("drug", "site")
        verbose_name = "Drug Obsolete Status by Site"
        verbose_name_plural = "Drug Obsolete Statuses by Site"
