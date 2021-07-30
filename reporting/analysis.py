from debt.models import Debt, Property, Case
from django.db import connection
import csv

# TODO: write a wrapper function
# that takes a SQL query string,
# executes it and returns results
# with headers as dict list

# TODO: start a reporting module
# that takes a dict list or queryset 
# and writes out a csv to reports dir

def water_debt_zips():
    """
    Q: Where is water debt located in the city?
    https://docs.google.com/document/d/1i8XCkkRE7JZtn5qecI87zmnpJUC67rrTkCXqsR76Dbc/edit#heading=h.essvytoq7u9m
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
