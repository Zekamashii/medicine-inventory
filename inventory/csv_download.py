from django.db.models import Q
from .models import Transaction


def generate_transactions_csv(writer, selected_site_id):
    # Write the header row
    writer.writerow(['ID', '取引タイプ', '医薬品名', '数量', '単位', '製造番号', '使用期限', '出庫元', '入庫先', '最終更新日時', '作成者'])

    # Filter transactions based on the selected site ID
    if selected_site_id is not None:
        transactions = Transaction.objects.filter(
            Q(source_site=selected_site_id) | Q(dest_site=selected_site_id)
        ).select_related('name', 'unit', 'source_site', 'dest_site', 'user')
    else:
        transactions = Transaction.objects.all().select_related('name', 'unit', 'source_site', 'dest_site', 'user')

    # Write each transaction row
    for transaction in transactions:
        # Get the drug name, unit, source site, destination site, and date created.
        drug_name = transaction.name.name if transaction.name else ''
        unit = transaction.unit.name if transaction.unit else ''
        source_site = transaction.source_site.name if transaction.source_site else ''
        dest_site = transaction.dest_site.name if transaction.dest_site else ''
        date_created = transaction.date_created.strftime("%Y-%m-%d %H:%M:%S") if transaction.date_created else ''

        # Get the user's last name and first name, or username if not available.
        if transaction.user:
            user = f"{transaction.user.last_name} {transaction.user.first_name}".strip() if transaction.user.last_name else transaction.user.username
        else:
            user = ''

        # Write the transaction row
        writer.writerow([
            transaction.id, transaction.get_type_display(), drug_name, transaction.quantity,
            unit, transaction.lot, transaction.expire_date, source_site,
            dest_site, date_created, user
        ])
