import calendar
import datetime
from django.http import JsonResponse
from inventory.models import Drug


def analyzer(scanned_data):
    product_id = None
    drug_name = None
    expire_date = None
    lot = None
    quantity = None
    error = None
    drug_id = None
    gs1_128 = False

    # Identify GS1-128 by '#' and split it
    split_data = scanned_data.split('#')
    part_one = split_data[0]
    if len(split_data) > 1:
        gs1_128 = True
        part_two = split_data[1]
        position = part_two.find("10")
        if position == 0:
            lot = part_two[position + len("10"):]

    product_id_start = part_one.find("01")
    if product_id_start == 0:
        product_id = part_one[product_id_start + 2:product_id_start + 16]

    expire_date_start = part_one.find("17", 16)
    if expire_date_start == 16:
        expire_date_str = part_one[expire_date_start + 2:expire_date_start + 8]
        year = int("20" + expire_date_str[:2])
        month = int(expire_date_str[2:4])
        day = int(expire_date_str[4:])
        if day == 0:
            day = calendar.monthrange(year, month)[1]
        expire_date = datetime.date(year, month, day)

    if gs1_128 is True:
        quantity_start = part_one.find("30", 24)
        if quantity_start == 24:
            quantity = int(part_one[quantity_start + 2:])
    elif gs1_128 is False:
        lot_start = part_one.find("10", 24)
        if lot_start == 24:
            lot = part_one[lot_start + 2:]

    try:
        drugs = Drug.objects.filter(obsoleted=False)
        drug = next((d for d in drugs if product_id in [code.strip() for code in d.product_code.split(',')]), None)
        if drug:
            drug_name = drug.name
            drug_id = drug.id
        else:
            error = "現在の商品コードに該当する医薬品は見つかりませんでした。"
    except Exception as e:
        error = str(e)

    return JsonResponse({
        'name': drug_name,
        'drug_id': drug_id,
        'product_id': product_id,
        'expire_date': expire_date,
        'lot': lot,
        'quantity': quantity,
        'error': error
    })
