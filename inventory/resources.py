from django.contrib.auth.models import User
from import_export import resources, fields
from import_export.widgets import ForeignKeyWidget
from .models import Drug, Category, Unit


class DrugMasterResource(resources.ModelResource):
    category = fields.Field(
        column_name='category',
        attribute='category',
        widget=ForeignKeyWidget(Category, 'name'))

    unit = fields.Field(
        column_name='unit',
        attribute='unit',
        widget=ForeignKeyWidget(Unit, 'name'))

    user = fields.Field(
        column_name='user_id',
        attribute='user',
        widget=ForeignKeyWidget(User, 'id'))  # Assuming you're importing user IDs

    class Meta:
        model = Drug
        skip_unchanged = True
        report_skipped = True
        import_id_fields = ['name']  # 'name' as a unique identifier
        fields = ('name', 'description', 'package', 'category', 'price', 'unit', 'product_code', 'orca_id')
        export_order = ('name', 'description', 'package', 'category', 'price', 'unit', 'product_code', 'orca_id')

    def before_import_row(self, row, **kwargs):
        row['user_id'] = row.get('user', 1)
