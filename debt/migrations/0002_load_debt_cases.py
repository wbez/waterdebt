# Generated by Django 3.2.5 on 2021-07-14 20:58
from django.db import migrations
from debt.models import Property, Debt, Case
from water.settings import BASE_DIR
import agate


### START CONFIG ###
data_dir = BASE_DIR + '/data/'
metered_unmetered_path = data_dir + 'Metered.NonMeteredproperties.xlsx'
debt_data_path = data_dir + 'Administrative hearings data.xlsx'
admin_data_path = data_dir + 'FOIA Response - Utility Debt Law Firms WBEZ MIZ.xlsx'
# not sure about this dataset ... no addresses
delinquent_data_path = data_dir + 'Delinquent Accounts 2010 to Present WBEZ MIZ.xlsx'
### END CONFIG ###


def load_data(apps,schema_editor):
    """
    load each object to db separately
    then look them up for fk refs
    """
    load_property()
    load_debt()
    load_case()


def load_property():
    """
    load metered/unmetered data
    from water dept
    """
    # read excel sheets into agate tables
    metered = agate.Table.from_xlsx(metered_unmetered_path,sheet='Metered Properties')
    unmetered = agate.Table.from_xlsx(metered_unmetered_path,sheet='NonMetered')

    # metered properties are listed in their own sheet
    for meter in metered:
        meter_dict = row_to_dict(meter,metered.column_names)
        prop = Property.objects.create(full_address=meter_dict['Address'],metered=True)
        prop.save()

    # unmetered properties listed in the other sheet, different columns
    for unmeter in unmetered:
        unmeter_dict = row_to_dict(unmeter,unmeter.column_names)
        prop = Property.objects.create(full_address=meter_dict['address nonMetered'],metered=False)
        prop.save()


def load_debt():
    """
    load debt data
    from finance dept
    """
    # read excel sheets into agate tables
    debt_data_2015 = agate.Table.from_xlsx(debt_data_path,sheet='2010-2015 Detail')
    debt_data_2020 = agate.Table.from_xlsx(debt_data_path,sheet='2016-2021 Detail')
    
    # combine rows for concise code
    debt_data = debt_data_2015.rows.values() + debt_data_2020.rows.values()

    # debt 2010-2015
    for dd in debt_data:
        dd_dict = row_to_dict(dd, debt_data_2015.column_names)
        # the hard part here is water debt and finance dept addresses are prob structured differently
        prop = Property.objects.get(full_address=dd_dict['PREMADDRESS'])
        debt = Debt.objects.create(
                prop = prop,
                full_address = dd_dict['PREMADDRESS'],
                bad_debt_no = dd_dict['BDBTNUM'], 
				debt_collector = dd_dict['ACGY_NAME'],
				debt_date = dd_dict['ASSIGNED_DATE'],
				debt_amt = dd_dict['BD_AMT'],
				# penalty???
				payment = dd_dict['PYMT_AMT'],
				# balance???
				# we don't have status because delinquent acct file doesn't have full addresses
				# no_occurrences?
                )
        debt.save()


def load_case():
    """
    load case data
    from admin law
    """
    # read excel sheet into agate table
    admin_data = agate.Table.from_xlsx(admin_data_path,sheet='Hearing Info')

    # load cases
    for admin_case in admin_data:
        case_dict = row_to_dict(admin_case,admin_data.column_names)
        case = Case.objects.create(
                nov = case_dict['Nov #'],
                street_dir = case_dict['NOV Street Direction Prefix Code'],
                street_name = case_dict['NOV Street Name'],
                zip_code = case_dict['NOV Zip Code'],
                disposition = case_dict['Disposition Description'],
                admin_cost = case_dict['Admin Costs'],
                sanction_cost = case_dict['Sanction Dollars'],
                penalty = case_dict['Sanction Dollars'],
                # respondent = case_dict # TODO: read in respondent sheet
                )
        case.save()

        

def row_to_dict(row, header):
    """
    build a dict from agate header + rows
    """
    return {header[i] : row[i] for i in range(len(header))}


class Migration(migrations.Migration):

    dependencies = [
        ('debt', '0001_initial'),
    ]

    operations = [
            migrations.RunPython(load_data)
    ]
