# Generated by Django 3.2.5 on 2021-09-29 17:47
from django.db import migrations
import agate, agateexcel
from water.settings import BASE_DIR
from debt.models import Account

### START CONFIG ###
data_dir = str(BASE_DIR) + '/data/'
accounts_data_path = data_dir + 'delinquent_accounts_2010-now.xlsx'
### END CONFIG ###



def load_data(apps,schema_editor):
    accounts_data = agate.Table.from_xlsx(accounts_data_path,sheet='delinquent accounts')
    for account in accounts_data:
        try:
            last_part = account['Premise Address'].split()[-1]
            if len(last_part) == 5:
                zipcode = last_part
            elif len(last_part) == 10:
                zipcode = last_part.split('-')[0]
            else:
                zipcode = None
            if zipcode and (not zipcode.isdigit() or len(zipcode) != 5):
                zipcode = None
            account_record = Account.objects.create(
                address = account['Premise Address'],
                zipcode = zipcode,
                status = account['Account status Indicator'],
                metered = account['Meter/NonMetered Indicator'],
                balance = account['Current Balance'],
                water_balance = account['Current Water Charges Balance'],
                sewer_balance = account['Current Sewer Charges Balance'],
                tax_balance = account['Current Tax Charges Balance'],
                penalty_balance = account['Current Penalty Charges Balance'],
                garbage_balance = account['Current Garbage Charges Balance'],
                other_balance = account['Current Other Charges Balance'],
                no_delinquencies = account['Number of occurrences of being delinquent since 2010'],
                )
            account_record.save()
            print(account_record.__dict__)
        except Exception as e:
            print(e)
            import ipdb; ipdb.set_trace()

class Migration(migrations.Migration):

    dependencies = [
        ('debt', '0004_account'),
    ]

    operations = [
            migrations.RunPython(load_data)
    ]