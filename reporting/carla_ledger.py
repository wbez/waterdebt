import csv
from water.settings import BASE_DIR

# START CONFIGS # 
data_dir = str(BASE_DIR) + '/data/'
carla_ledger_filename = 'carla_ledger_transactions.csv' # must be a Sheet
carla_cats_filename = 'carla_ledger_cats.csv'
reports_dir = str(BASE_DIR) + '/reporting/reports/'
billing_cycle_filename = 'billing_cycle_mk.csv'
stacked_bar_filename = 'stacked_bar_mk.csv'
# END CONFIGS #

# load ledger
ledger = [x for x in csv.DictReader(open(data_dir+carla_ledger_filename))]

# load category lookups
categories = [x for x in csv.DictReader(open(data_dir+carla_cats_filename))]
category_dict = dict((cat['Description                                        '],cat['category']) for cat in categories)

type(categories)

# roll up ledger by bill date, transaction type

cycle = dict()

for entry in reversed(ledger): # reverse order to capture latest balance
    bill_date = entry['Bill Date  ']
    if bill_date not in cycle:
        cycle[bill_date] = {
            'water':0,
            'sewer':0,
            'garbage':0,
            'penalties':0,
            'taxes':0,
            'payments':0,
            'balance':0,
            }
    category = category_dict[entry['Description                                        ']]
    if entry[' Transaction Amount '] in (' $-   ','$ -   ',' -   '):
        entry_amt = 0
    else:
        try:
            entry_amt = float(entry[' Transaction Amount ']
                            .replace('$','')
                            .replace(',','')
                            .replace(')','')
                            .replace('(','-') # convert parens to negative
            )
        except Exception as e:
            print(e)
            import ipdb; ipdb.set_trace()
    cycle[bill_date][category] += entry_amt
    # balances don't accumulate
    cycle[bill_date]['balance'] = entry[' Balance       ']

# transform to billing cycle
billing_cycle = []
for bill_date in cycle:
    billing_cycle.append(
            {
            'billing_cycle_date': bill_date,
            'charges_for_that_cycle': sum([cycle[bill_date][x] for x in ['water','sewer','garbage','penalties','taxes']]), 
            'balance': cycle[bill_date]['balance'],
            'payment_amount': cycle[bill_date]['payments']
            }
    )

# write out to billing cycle
billing_cycle_outfile = open(reports_dir+billing_cycle_filename,'w')
billing_cycle_csv = csv.DictWriter(billing_cycle_outfile,billing_cycle[0].keys())
billing_cycle_csv.writeheader()
billing_cycle_csv.writerows(billing_cycle)
billing_cycle_outfile.close()


# transform to stacked bar
stacked_bar = {
        'Period': 'April 2011-March 2021', 
        'Water': 0, 
        'Sewer': 0, 
        'Garbage': 0, 
        'Penalties': 0, 
        'Taxes': 0}

for bill_date in cycle:
    stacked_bar['Water'] += cycle[bill_date]['water']
    stacked_bar['Sewer'] += cycle[bill_date]['sewer']
    stacked_bar['Garbage'] += cycle[bill_date]['garbage']
    stacked_bar['Penalties'] += cycle[bill_date]['penalties']
    stacked_bar['Taxes'] += cycle[bill_date]['taxes']

# write out to stacked_bar
stacked_bar_outfile = open(reports_dir+stacked_bar_filename,'w')
stacked_bar_csv = csv.DictWriter(stacked_bar_outfile,stacked_bar.keys())
stacked_bar_csv.writeheader()
stacked_bar_csv.writerow(stacked_bar)
stacked_bar_outfile.close()

