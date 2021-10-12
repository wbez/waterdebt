from debt.models import Debt, Property, Case, Account, ZipCode
from django.db import connection
import csv
from water.settings import BASE_DIR

# TODO: write a wrapper function
# that takes a SQL query string,
# executes it and returns results
# with headers as dict list

# TODO: start a reporting module
# that takes a dict list or queryset 
# and writes out a csv to reports dir

### START CONFIG ###
reports_dir = str(BASE_DIR) + '/reporting/reports/'
### END CONFIG ###


def debt_by_zipcode():
    """
    return zip, # debts, debt $, racial majority
    """
    # most/all chicago zips start with 606
    chi_zips = ZipCode.objects.filter(five_digit__startswith='606')
    rows = []
    for chi_zip in chi_zips:
        # get all active accounts for this zip
        zip_debts = Account.objects.filter(zipcode=chi_zip.five_digit,status='A')
        # get number and total amt of debts
        row = {
                'zipcode': chi_zip.five_digit,
                'racial_maj': chi_zip.majority_race,
                'no_debts': len(zip_debts),
                'total_debt_amt': sum([x.balance for x in zip_debts]),
                'summed_debt_amt': sum([sum([x.water_balance,x.sewer_balance,x.tax_balance,x.penalty_balance,x.garbage_balance,x.other_balance]    ) for x in zip_debts]),
                'water_balance': sum([x.water_balance for x in zip_debts]),
                'sewer_balance': sum([x.sewer_balance for x in zip_debts]),
                'tax_balance': sum([x.sewer_balance for x in zip_debts]),
                'penalty_balance': sum([x.penalty_balance for x in zip_debts]),
                'garbage_balance': sum([x.garbage_balance for x in zip_debts]),
                'other_balance': sum([x.other_balance for x in zip_debts])
                }
        rows.append(row)
    
    # write results
    outfile = open(reports_dir + 'debt_by_zipcode.csv','w')
    outcsv = csv.DictWriter(outfile,rows[0].keys())
    outcsv.writeheader()
    outcsv.writerows(rows)
    outfile.close()






def water_debt_zips():
    """
    Q: Where is water debt located in the city?
    https://docs.google.com/document/d/1i8XCkkRE7JZtn5qecI87zmnpJUC67rrTkCXqsR76Dbc/edit#heading=h.essvytoq7u9m
    NOTE: queries Debt records
    """
    with connection.cursor() as cursor:
        cursor.execute(
                """
                select substr(debt_property.zipcode,0,6) zip, count(distinct bad_debt_no) c 
                from debt_debt 
                join debt_property 
                on debt_debt.prop_id = debt_property.id 
                group by zip 
                order by c desc;
                """)
        rows = cursor.fetchall()
        return rows


def metered_unmetered_debt():
    """
    Q: Who owes more homeowners with unmetered or metered properties?
    https://docs.google.com/document/d/1i8XCkkRE7JZtn5qecI87zmnpJUC67rrTkCXqsR76Dbc/edit#heading=h.oq7h5jp37ud4
    """
    # TODO: sanity check there aren't multiple debt amts per bad debt no
    
    metered = Property.objects.filter(metered=True)
    unmetered = Property.objects.filter(metered=False)
    
    # {bad_debt_no: [debt_amt, debt_amt ...]}
    metered_debts = {} 
    unmetered_debts = {}

    for prop in metered:
        for debt in prop.debt_set.all():
            if debt.bad_debt_no not in metered_debts:
                metered_debts[debt.bad_debt_no] = []
            metered_debts[debt.bad_debt_no].append(debt.debt_amt)
            # test
            if len(set(metered_debts[debt.bad_debt_no])) > 1:
                # unexpected
                return "multiple debt amounts for bad debt no " + str(debt.bad_debt_no)
    
    for prop in unmetered:
        for debt in prop.debt_set.all():
            if debt.bad_debt_no not in unmetered_debts:
                unmetered_debts[debt.bad_debt_no] = []
            unmetered_debts[debt.bad_debt_no].append(debt.debt_amt)
            # test
            if len(set(unmetered_debts[debt.bad_debt_no])) > 1:
                # unexpected
                return "multiple debt amounts for bad debt no " + str(debt.bad_debt_no)
    
    metered_debt_total = 0
    unmetered_debt_total = 0

    for md in metered_debts:
        # we only want to add one debt amount, if any exist
        metered_debt_total += metered_debts[md][0] if metered_debts[md] else 0
    
    for ud in unmetered_debts:
        unmetered_debt_total += unmetered_debts[ud][0] if unmetered_debts[md] else 0

    return {
            'metered_debt_total': metered_debt_total,
            'unmetered_debt_total': unmetered_debt_total
            }


if __name__ == "__main__":
    pass
