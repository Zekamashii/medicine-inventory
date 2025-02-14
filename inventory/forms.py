from datetime import datetime, timedelta
from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm, PasswordChangeForm
from django.core.exceptions import ValidationError
from django.db.models import Q, Sum
from django.utils.translation import gettext_lazy as _
from django.core.validators import MinValueValidator
from inventory.input_normalizer import input_normalize
from inventory.models import Transaction, Drug, Unit, Site, InventoryItem, Category, UserProfile, \
    SafetyStock, DrugObsoleteBySite
import os
from dotenv import load_dotenv

load_dotenv()
ALLOWED_DOMAINS = os.getenv('ALLOWED_DOMAINS')


class UserRegisterForm(UserCreationForm):
    username = forms.CharField(max_length=150, required=True, label=_("ユーザー名"),
                               help_text=_("必須。150文字以下。文字、数字、@/./+/-/_のみ。"))
    email = forms.EmailField(label=_("メールアドレス"),
                             help_text=_("必須。特定のドメインを使用してください。"))
    first_name = forms.CharField(max_length=50, required=True, label=_("名"), help_text=_("必須。"))
    last_name = forms.CharField(max_length=50, required=False, label=_("姓"))

    class Meta:
        model = User
        fields = ['username', 'last_name', 'first_name', 'email', 'password1', 'password2']

    def clean_email(self):
        email = self.cleaned_data['email']
        domain = email.split('@')[-1]
        if domain not in ALLOWED_DOMAINS:
            raise ValidationError("特定のドメインに制限されています。")
        return email


class CreateCategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        exclude = ['user', 'obsoleted']

    def clean_name(self):
        name = input_normalize(self.cleaned_data.get('name'))
        if Category.objects.filter(name=name).exists():
            raise ValidationError(_("この名前の種類は既に存在します。"))
        return name

    def __init__(self, *args, **kwargs):
        super(CreateCategoryForm, self).__init__(*args, **kwargs)


class EditCategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        exclude = ['user']

    def clean_name(self):
        name = input_normalize(self.cleaned_data.get('name'))
        if Category.objects.filter(name=name).exclude(pk=self.instance.pk).exists():
            raise ValidationError(_("この名前の種類は既に存在します。"))
        return name

    def __init__(self, *args, **kwargs):
        super(EditCategoryForm, self).__init__(*args, **kwargs)


class CreateSiteForm(forms.ModelForm):
    class Meta:
        model = Site
        exclude = ['user', 'obsoleted', 'latitude', 'longitude']
        widgets = {
            'color': forms.TextInput(attrs={'type': 'color', 'style': 'width: 80px;'}),
        }

    def clean_name(self):
        name = input_normalize(self.cleaned_data.get('name'))
        if Site.objects.filter(name=name).exists():
            raise ValidationError(_("この名前の拠点は既に存在します。"))
        return name

    def __init__(self, *args, **kwargs):
        super(CreateSiteForm, self).__init__(*args, **kwargs)


class EditSiteForm(forms.ModelForm):
    class Meta:
        model = Site
        exclude = ['user']
        widgets = {
            'color': forms.TextInput(attrs={'type': 'color', 'style': 'width: 80px;'}),
        }

    def clean_name(self):
        name = input_normalize(self.cleaned_data.get('name'))
        if Site.objects.filter(name=name).exclude(pk=self.instance.pk).exists():
            raise ValidationError(_("この名前の拠点は既に存在します。"))
        return name

    def __init__(self, *args, **kwargs):
        super(EditSiteForm, self).__init__(*args, **kwargs)


class EditUserForm(forms.ModelForm):
    scanner_mode_enabled = forms.BooleanField(required=False,
                                              label=_("デフォルトでスキャナーモードが有効"),
                                              help_text=_(
                                                  "ログイン後にユーザーのデフォルトのスキャナーモード設定。"))

    default_site = forms.ModelChoiceField(queryset=Site.objects.filter(obsoleted=False),
                                          help_text="ログイン後にユーザーのデフォルトの拠点。",
                                          label=_("デフォルトの拠点"), required=False)

    default_sort_field = forms.ChoiceField(choices=[
        ('id', 'ID'),
        ('name', '医薬品名（50音順）'),
        ('expire_date', '残存日数'),
        ('date_created', '最終更新日時'),
        # Add other sortable fields here
    ], label=_("デフォルトの並べ替えのキー"), required=True)

    default_sort_order = forms.ChoiceField(choices=[
        ('asc', '昇順'),
        ('desc', '降順')
    ], label=_("デフォルトの並べ替え順序"), required=True)

    class Meta:
        model = UserProfile
        exclude = ['user']

    def __init__(self, *args, **kwargs):
        super(EditUserForm, self).__init__(*args, **kwargs)


class CreateDrugMasterForm(forms.ModelForm):
    category = forms.ModelChoiceField(queryset=Category.objects.all(), required=True,
                                      label=_("医薬品種類"),
                                      help_text=_("必須。医薬品種類を選択してください。"))
    unit = forms.ModelChoiceField(queryset=Unit.objects.all(), required=True, label=_("単位"),
                                  help_text=_(
                                      "必須。最小単位優先。確信が持てない場合は、「EA」を選択してください。"),
                                  empty_label=None)
    product_code = forms.CharField(required=False, label=_("商品コード"), help_text=_(
        "国産医薬品の場合は、数字14桁です。複数のコードが存在する場合、それらをコンマ(, )で区切って表記します。例：34987350287732, 04987815020101。"))

    class Meta:
        model = Drug
        exclude = ['kana', 'orca_id', 'user', 'obsoleted']

    def clean_name(self):
        name = input_normalize(self.cleaned_data.get('name'))
        if Drug.objects.filter(name=name).exists():
            raise ValidationError(_("この名前の医薬品マスターは既に存在します。"))
        return name

    def clean_product_code(self):
        product_codes = self.cleaned_data.get('product_code', '')
        non_unique_codes = []
        if product_codes:
            codes = [code.strip() for code in product_codes.split(',')]
            for code in codes:
                query = Q(product_code__contains=code)
                if self.instance and self.instance.pk:
                    existing = Drug.objects.filter(query).exclude(pk=self.instance.pk)
                else:
                    existing = Drug.objects.filter(query)

                if existing.exists():
                    non_unique_codes.append(code)

            if non_unique_codes:
                raise ValidationError(_("次の商品コードは既に使用されています: %(codes)s"),
                                      params={'codes': ', '.join(non_unique_codes)})

        return product_codes

    def __init__(self, *args, **kwargs):
        super(CreateDrugMasterForm, self).__init__(*args, **kwargs)
        self.fields['category'].queryset = Category.objects.filter(obsoleted=False)
        if self.fields['unit'].queryset.exists():
            self.fields['unit'].initial = self.fields['unit'].queryset.first()


class EditDrugMasterForm(forms.ModelForm):
    category = forms.ModelChoiceField(queryset=Category.objects.all(), required=True,
                                      label=_("医薬品種類"),
                                      help_text=_("必須。医薬品種類を選択してください。"))
    unit = forms.ModelChoiceField(queryset=Unit.objects.all(), required=True, label=_("単位"),
                                  help_text=_(
                                      "必須。最小単位優先。確信が持てない場合は、「EA」を選択してください。"),
                                  empty_label=None)
    product_code = forms.CharField(required=False, label=_("商品コード"),
                                   help_text=_(
                                       "国産医薬品の場合は、数字14桁です。複数のコードが存在する場合、それらをコンマ(, )で区切って表記します。例：34987350287732, 04987815020101。"))

    class Meta:
        model = Drug
        exclude = ['orca_id', 'user']

    def clean(self):
        cleaned_data = super().clean()
        obsoleted = cleaned_data.get('obsoleted')

        if obsoleted:
            total_quantity = InventoryItem.objects.filter(name=self.instance).aggregate(Sum('quantity'))['quantity__sum'] or 0

            if total_quantity > 0:
                raise ValidationError(_("この医薬品には在庫があるため、廃止できません。在庫を先に処理してください。"))

        return cleaned_data


    def clean_product_code(self):
        product_codes = self.cleaned_data.get('product_code', '')
        non_unique_codes = []
        if product_codes:
            codes = [code.strip() for code in product_codes.split(',')]
            for code in codes:
                query = Q(product_code__contains=code)
                if self.instance and self.instance.pk:
                    existing = Drug.objects.filter(query).exclude(pk=self.instance.pk)
                else:
                    existing = Drug.objects.filter(query)

                if existing.exists():
                    non_unique_codes.append(code)

            if non_unique_codes:
                raise ValidationError(_("次の商品コードは既に使用されています: %(codes)s"),
                                      params={'codes': ', '.join(non_unique_codes)})

        return product_codes

    def clean_name(self):
        name = input_normalize(self.cleaned_data.get('name'))
        if Drug.objects.filter(name=name).exclude(pk=self.instance.pk).exists():
            raise ValidationError(_("この名前の医薬品マスターは既に存在します。"))
        return name

    def __init__(self, *args, **kwargs):
        super(EditDrugMasterForm, self).__init__(*args, **kwargs)
        self.fields['category'].queryset = Category.objects.filter(obsoleted=False)


class CreateInboundTransactionForm(forms.ModelForm):
    type = forms.ChoiceField(choices=Transaction.Type.choices, initial=Transaction.Type.INBOUND,
                             label=_("取引タイプ"), disabled=True)
    category = forms.ModelChoiceField(queryset=Category.objects.filter(obsoleted=False),
                                      required=False, label=_("医薬品種類フィルター"))
    name = forms.ModelChoiceField(queryset=Drug.objects.filter(obsoleted=False), required=True,
                                  label=_("医薬品名"))
    quantity = forms.IntegerField(
        required=True,
        label=_("取引数量"),
        validators=[
            MinValueValidator(limit_value=1, message=_("取引数量は 0 以上で指定してください。"))]
    )
    unit = forms.ModelChoiceField(queryset=Unit.objects.all(), required=True, label=_("単位"))
    lot = forms.CharField(max_length=200, required=True, label=_("製造番号"))
    tomorrow = (datetime.today() + timedelta(days=30)).date()
    expire_date = forms.DateField(required=True, label=_("使用期限"),
                                  widget=forms.widgets.DateInput(attrs={'type': 'date'}))
    dest_site = forms.ModelChoiceField(queryset=Site.objects.filter(obsoleted=False), required=True,
                                       label=_("入庫先"), empty_label=None,
                                       help_text=_("入庫先をご確認ください。"))

    class Meta:
        model = Transaction
        exclude = ['user']
        fields = ['type', 'category', 'name', 'quantity', 'unit', 'lot', 'expire_date', 'dest_site',
                  'user']

    def __init__(self, *args, **kwargs):
        drugs = kwargs.pop('drugs', None)
        super(CreateInboundTransactionForm, self).__init__(*args, **kwargs)
        if drugs is not None:
            self.fields['name'].queryset = drugs
        if self.fields['unit'].queryset.exists():
            self.fields['unit'].initial = self.fields['unit'].queryset.first()


class CreateOutboundTransactionForm(forms.ModelForm):
    type = forms.ChoiceField(choices=Transaction.Type.choices, initial=Transaction.Type.OUTBOUND,
                             label=_("取引タイプ"), disabled=True)
    category = forms.ModelChoiceField(queryset=Category.objects.filter(obsoleted=False),
                                      required=False,
                                      label=_("医薬品種類フィルター"))
    name = forms.ModelChoiceField(queryset=Drug.objects.filter(obsoleted=False), required=True,
                                  label=_("医薬品名"))
    quantity = forms.IntegerField(
        required=True,
        label=_("取引数量"),
        validators=[
            MinValueValidator(limit_value=1, message=_("取引数量は 0 以上で指定してください。"))]
    )
    unit = forms.ModelChoiceField(queryset=Unit.objects.all(), required=True, label=_("単位"))
    lot = forms.ModelChoiceField(queryset=InventoryItem.objects.all(), required=True,
                                 label=_("製造番号"), help_text=_("製造番号をご確認ください。"))
    expire_date = forms.DateField(required=False, widget=forms.HiddenInput())
    source_site = forms.ModelChoiceField(queryset=Site.objects.filter(obsoleted=False),
                                         required=True,
                                         label=_("出庫元"), empty_label=None,
                                         help_text=_("出庫元をご確認ください。"))

    class Meta:
        model = Transaction
        exclude = ['user']
        fields = ['type', 'category', 'name', 'quantity', 'unit', 'lot', 'source_site', 'user']

    def __init__(self, *args, **kwargs):
        drugs = kwargs.pop('drugs', None)
        lots = kwargs.pop('lots', None)
        super(CreateOutboundTransactionForm, self).__init__(*args, **kwargs)
        if drugs is not None:
            self.fields['name'].queryset = drugs
        if lots is not None:
            self.fields['lot'].queryset = lots
        initial = kwargs.get('initial', {})
        name = initial.get('name')
        site = initial.get('source_site')
        if name and site:
            self.fields['lot'].queryset = InventoryItem.objects.filter(name=name, site=site, quantity__gt=0)
        else:
            self.fields['lot'].queryset = InventoryItem.objects.filter(quantity__gt=0)
        if self.fields['unit'].queryset.exists():
            self.fields['unit'].initial = self.fields['unit'].queryset.first()
        self.fields['quantity'].initial = 1

    def save(self, commit=True):
        instance = super(CreateOutboundTransactionForm, self).save(commit=False)
        if self.cleaned_data['lot']:
            instance.expire_date = self.cleaned_data['lot'].expire_date
        if commit:
            instance.save()
        return instance


class CreateTransferTransactionForm(forms.ModelForm):
    type = forms.ChoiceField(choices=Transaction.Type.choices, initial=Transaction.Type.TRANSFER,
                             label=_("取引タイプ"), disabled=True)
    category = forms.ModelChoiceField(queryset=Category.objects.filter(obsoleted=False),
                                      required=False,
                                      label=_("医薬品種類フィルター"))
    name = forms.ModelChoiceField(queryset=Drug.objects.filter(obsoleted=False), required=True,
                                  label=_("医薬品名"))
    quantity = forms.IntegerField(
        required=True,
        label=_("取引数量"),
        validators=[
            MinValueValidator(limit_value=1, message=_("取引数量は 0 以上で指定してください。"))]
    )
    unit = forms.ModelChoiceField(queryset=Unit.objects.all(), required=True, label=_("単位"))
    lot = forms.ModelChoiceField(queryset=InventoryItem.objects.all(), required=True,
                                 label=_("製造番号"))
    expire_date = forms.DateField(required=False, widget=forms.HiddenInput())
    source_site = forms.ModelChoiceField(queryset=Site.objects.filter(obsoleted=False),
                                         required=True,
                                         label=_("出庫元"), empty_label=None)
    dest_site = forms.ModelChoiceField(queryset=Site.objects.filter(obsoleted=False), required=True,
                                       label=_("入庫先"), empty_label=None)

    class Meta:
        model = Transaction
        exclude = ['user']
        fields = ['type', 'category', 'name', 'quantity', 'unit', 'lot', 'source_site', 'dest_site']

    def __init__(self, *args, **kwargs):
        drugs = kwargs.pop('drugs', None)
        lots = kwargs.pop('lots', None)
        super(CreateTransferTransactionForm, self).__init__(*args, **kwargs)
        if drugs is not None:
            self.fields['name'].queryset = drugs
        if lots is not None:
            self.fields['lot'].queryset = lots
        initial = kwargs.get('initial', {})
        name = initial.get('name')
        site = initial.get('source_site')
        if name and site:
            self.fields['lot'].queryset = InventoryItem.objects.filter(name=name, site=site, quantity__gt=0)
        else:
            self.fields['lot'].queryset = InventoryItem.objects.filter(quantity__gt=0)
        if self.fields['unit'].queryset.exists():
            self.fields['unit'].initial = self.fields['unit'].queryset.first()

    def save(self, commit=True):
        instance = super(CreateTransferTransactionForm, self).save(commit=False)
        if self.cleaned_data['lot']:
            instance.expire_date = self.cleaned_data['lot'].expire_date
        if commit:
            instance.save()
        return instance


class CreateAdjustTransactionForm(forms.ModelForm):
    type = forms.ChoiceField(choices=Transaction.Type.choices, initial=Transaction.Type.ADJUST,
                             label=_("取引タイプ"), disabled=True)
    name = forms.ModelChoiceField(queryset=Drug.objects.filter(obsoleted=False), required=True,
                                  label=_("医薬品名"), disabled=True)
    expire_date = forms.DateField(required=False, widget=forms.HiddenInput())
    quantity = forms.IntegerField(
        required=True,
        label=_("実際数量"),
        validators=[
            MinValueValidator(limit_value=0, message=_("実際数量は 0 以上で指定してください。"))],
        help_text=_(
            "入力された数量は、システムに直接反映されます。正確な数量を確認して入力してください。")
    )
    unit = forms.ModelChoiceField(queryset=Unit.objects.all(), required=True, label=_("単位"),
                                  disabled=True)
    lot = forms.CharField(required=True, label=_("製造番号"), disabled=True)
    source_site = forms.ModelChoiceField(queryset=Site.objects.filter(obsoleted=False),
                                         required=True,
                                         label=_("拠点"), disabled=True)

    class Meta:
        model = Transaction
        exclude = ['user']
        fields = ['type', 'name', 'lot', 'source_site', 'quantity', 'unit', 'expire_date']


class CancelTransactionForm(forms.ModelForm):
    class Meta:
        model = Transaction
        exclude = ['user']
        fields = ['type', 'name', 'lot', 'source_site', 'dest_site', 'quantity', 'unit',
                  'expire_date']

    def __init__(self, *args, **kwargs):
        super(CancelTransactionForm, self).__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].disabled = True


class SafetyStockForm(forms.ModelForm):
    class Meta:
        model = SafetyStock
        fields = ['min_stock']
        widgets = {
            'min_stock': forms.NumberInput(attrs={'class': 'min-stock-input'}),
        }


class DrugObsoleteStatusForm(forms.ModelForm):
    class Meta:
        model = DrugObsoleteBySite
        fields = ['is_obsolete']


class CustomPasswordChangeForm(PasswordChangeForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs['class'] = 'form-control'
