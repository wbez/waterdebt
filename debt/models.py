from django.db import models

# Create your models here.

class Property(models.Model):
    full_address = models.CharField(max_length=200, unique=True)
    # address parts
    numeric_address = models.IntegerField()
    street_dir = models.CharField(max_length=1, null=True)
    street_name = models.CharField(max_length=50)
    street_suffix = models.CharField(max_length=10, null=True)
    unit = models.CharField(max_length=30, null=True)
    zipcode = models.CharField(max_length=10,null=True)
    # metered or unmetered water service
    metered = models.BooleanField(null=True)


class Debt(models.Model):
    prop = models.ForeignKey(Property, null=True, on_delete=models.CASCADE)
    full_address = models.CharField(max_length = 100) # TODO FK Property
    bad_debt_no = models.CharField(max_length = 50)
    debt_collector = models.CharField(max_length = 100) # TODO FK
    debt_date = models.DateField()
    debt_amt = models.IntegerField()
    penalty = models.IntegerField()
    payment = models.IntegerField()
    balance = models.IntegerField()
    # we don't have status or no/occurrences because delinquent acct file doesn't have full addresses
    #status = models.CharField(max_length=50) # TODO Choice
    # no_occurrences = models.IntegerField() # TODO what is this


class Case(models.Model):
    nov = models.CharField(max_length=25,unique=True)
    street_dir = models.CharField(max_length=5)
    street_name = models.CharField(max_length=50)
    zip_code = models.IntegerField()
    disposition = models.CharField(max_length=100)
    admin_cost = models.IntegerField()
    sanction_cost = models.IntegerField()
    penalty = models.IntegerField()
    respondent = models.CharField(max_length=100)
    
    # TODO: MCV Description
    # TODO: method to look up property candidates based on limited address info + debt

"""
class Collector(models.Model):
    pass

"""
