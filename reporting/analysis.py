from debt.models import Debt, Property, Case, Account, ZipCode
from django.db import connection
import csv
from water.settings import BASE_DIR
import datetime


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


###############
#             #
# BIG NUMBERS #
#             # 
###############


def universe_of_accounts():
    """"
    the big number for the story:
    (per AL be conservative and take the smaller of 
    two slightly different sets of numbers the city gave us)
    get each account in the universe,
    total up current balance and itemized balances separately,
    then return the smaller of the two
    """
    
    # active accounts only
    active_accounts = Account.objects.filter(status='A')
    
    # get active accounts with current balance > 0
    positive_current_balance_accounts = active_accounts.filter(balance__gt=0)

    # get active accounts with summed balance > 0
    positive_summed_balance_accounts = []
    for account in active_accounts:
        if account.summed_balance > 0:
            positive_summed_balance_accounts.append(account)

    # get totals from both sets
    current_balance_total = sum([x.balance for x in positive_current_balance_accounts])
    summed_balance_total = sum([x.summed_balance for x in positive_summed_balance_accounts])
    print('current_balance_total',current_balance_total)
    print('summed_balance_total',summed_balance_total)

    # check which is less and return that list
    if current_balance_total < summed_balance_total:
        print('returning current balance:',current_balance_total)
        return list(positive_current_balance_accounts) 
    else:
        print('returning summed balance:',summed_balance_total)
        return positive_summed_balance_accounts


accounts = universe_of_accounts()


def debt_by_zipcode():
    """
    return zip, # debts, debt $, racial majority
    """
    # get all the zipcodes in the delinquent acct table 
    five_digits = list(set([x.zipcode for x in Account.objects.all()])) 
    
    # for some reason there are ~5-6 zipcodes in the delinquent acct file
    # that aren't in AL's zipcode file: 
    # 46325, 60170, 60635, 60666, 60699, 66041
    # noting that none of the illinois zips exist, 46325 is Indiana
    zip_digis = set([z.five_digit for z in ZipCode.objects.all()])
    missing_zips = [x for x in five_digits if x not in zip_digis] # includes zip=None 
    rows = []
    for five_digit in five_digits:
        try:
            # have to handle missing zips
            zipcodes = ZipCode.objects.filter(five_digit=five_digit)
            zipcode = zipcodes[0] if zipcodes else None
        except Exception as e:
            print(e)
            import ipdb; ipdb.set_trace()
        # get all active accounts for this zip and use current debt
        zip_debts = Account.objects.filter(zipcode=five_digit,status='A',balance__gt=0)
        # zip_debts = [x for x in Account.objects.filter(zipcode=five_digit,status='A') if x.summed_balance > 0]
        zip_props = Property.objects.filter(zipcode=five_digit)
        # get number and total amt of debts
        row = {
                'zipcode': five_digit if five_digit else 'None',
                'racial_maj': zipcode.majority_race if zipcode else 'No data',
                'total_pop': zipcode.total_pop if zipcode else 'No data',
                'no_properties': len(zip_props) if five_digit else None,
                'no_debts': len(zip_debts),
                # using total_debt_amount because it's lower than total in aggregate
                'total_debt_amt': sum([x.balance for x in zip_debts]),
                #'summed_debt_amt': sum(sum([x.summed_balance for x in zip_debts])),
                #'water_balance': sum([x.water_balance for x in zip_debts]),
                #'sewer_balance': sum([x.sewer_balance for x in zip_debts]),
                #'tax_balance': sum([x.sewer_balance for x in zip_debts]),
                #'penalty_balance': sum([x.penalty_balance for x in zip_debts]),
                #'garbage_balance': sum([x.garbage_balance for x in zip_debts]),
                #'other_balance': sum([x.other_balance for x in zip_debts]),
                #'no_metered_homes': len([x for x in zip_props if x.metered]),
                'no_metered_homes': len([x for x in zip_debts if x.metered]),
                #'no_unmetered_homes': len([x for x in zip_props if not x.metered]),
                'no_unmetered_homes': len([x for x in zip_debts if not x.metered]),
                'total_debt_metered': sum([x.balance for x in zip_debts if x.metered]),
                'total_debt_unmetered': sum([x.balance for x in zip_debts if not x.metered])
                }
        if row['no_debts']:
            #row['avg_debt'] = row['total_debt_unmetered']/len(zip_props) if len(zip_props) else None
            row['avg_debt'] = row['total_debt_unmetered']/len(zip_debts) if len(zip_debts) else None
            row['avg_metered_debt'] = row['total_debt_unmetered']/row['no_metered_homes'] if row['no_metered_homes'] else None
            row['avg_unmetered_debt'] = row['total_debt_unmetered']/row['no_unmetered_homes'] if row['no_unmetered_homes'] else None
            rows.append(row)
        row['debt_per_property'] = row['total_debt_amt'] / row['no_properties'] if row['no_properties'] else None

    sorted_rows = sorted(rows,key = lambda x: x['no_debts'], reverse = True)
    
    # write results
    outfile = open(reports_dir + 'debt_by_zipcode.csv','w')
    outcsv = csv.DictWriter(outfile,sorted_rows[0].keys())
    outcsv.writeheader()
    try:
        outcsv.writerows(sorted_rows)
    except Exception as e:
        print(e)
        import ipdb; ipdb.set_trace()
    outfile.close()



###################
#                 #
# END BIG NUMBERS #
#                 # 
###################



def debt_by_unmetered():
    accounts = Account.objects.all()
    nonmetered_accounts = Account.objects.filter(metered=False)







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
            'metered_debt_total': metered_debt_total}


def vacancies_and_debts(delta=90):
    """
    get all properties marked vacant
    and any debts within 90 days,
    one address per row
    """
    vac_props_debts = [x for x in Property.objects.all() if x.vacancy_set.all() and x.debt_set.all()]
    interesting = set()
    outfile = open('reporting/reports/properties_marked_vacant_with_debts_less_than_90_days_later.csv','w')
    headers = ['prop_address','metered','vacancy_address','vacancy_violation_no','vacancy_issue_date','debt_address','bad_debt_no','debt_date']
    outcsv = csv.DictWriter(outfile,headers)
    outcsv.writeheader()
    for prop in vac_props_debts:
        row = {
                'prop_address': prop.full_address,
                'metered': prop.metered,
                'vacancy_violation_no': '',
                'vacancy_issue_date': '',
                'bad_debt_no': '',
                'debt_date': ''
                }
        for vac in prop.vacancy_set.all():
            row['vacancy_address'] = vac.property_address
            row['vacancy_violation_no'] += vac.violation_no + ' | '
            row['vacancy_issue_date'] += str(vac.issue_date) + ' | '

            debts = prop.debt_set.filter(debt_date__range=[vac.issue_date,vac.issue_date+datetime.timedelta(delta)])
            for debt in debts:
                row['debt_address'] = debt.full_address
                row['bad_debt_no'] += debt.bad_debt_no + ' | '
                row['debt_date'] += str(debt.debt_date) + ' | '
        if debts:
            # TODO: per household debt
            outcsv.writerow(row)

    outfile.close()


def account_balances():
    rows = []
    for account in Account.objects.all():
        row = {
                'db_id': account.id, 
                'account_address': account.address, 
                'summed_balance': sum([account.water_balance, account.sewer_balance,account.tax_balance,account.penalty_balance,account.garbage_balance,account.other_balance])
        }
        rows.append(row)
    # write to file
    outfile = open('reporting/reports/account_balances.csv','w')
    outcsv = csv.DictWriter(outfile,row.keys())
    outcsv.writeheader()
    for row in rows:
        outcsv.writerow(row)
    outfile.close()
   

def pct_debt_from_black_zipcodes(method='total'):
    mbzs = ZipCode.objects.filter(majority_race='Black')

    # straight up balances
    if method=='total':
        total_debt = sum([x.balance for x in Account.objects.filter(status='A')])
        black_zip_total_debt = 0

        for mbz in mbzs:
            for acct in Account.objects.filter(zipcode=mbz.five_digit,status='A'):
                black_zip_total_debt += acct.balance

        return black_zip_total_debt/total_debt

    # only balances over 0$
    elif method == 'actual':
        total_actual_debt = sum([x.balance for x in Account.objects.filter(status='A',balance__gt=0)])

        black_zip_total_actual_debt = 0

        for mbz in mbzs:
            for acct in Account.objects.filter(zipcode=mbz.five_digit,status='A'):
                if acct.balance > 0:
                    black_zip_total_actual_debt += acct.balance

        return black_zip_total_actual_debt / total_actual_debt

    # sum up each balance manually
    elif method == 'summed':
        summed_debt = sum([sum([x.water_balance, x.sewer_balance, x.tax_balance, x.garbage_balance, x.penalty_balance, x.other_balance]) for x in Account.objects.filter(status='A')])

        black_zip_summed_debt = 0
        for mbz in mbzs:
            for acct in Account.objects.filter(zipcode=mbz.five_digit,status='A'):
                black_zip_summed_debt += sum([acct.water_balance, acct.sewer_balance, acct.tax_balance, acct.garbage_balance, acct.penalty_balance, acct.other_balance])

        return black_zip_summed_debt/summed_debt
