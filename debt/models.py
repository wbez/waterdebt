from django.db import models

# Create your models here.

class Debt(models.Model):
    full_address = models.CharField(max_length = 100)
    bad_debt_no = models.CharField(max_length = 50)
    debt_collector = models.CharField(max_length = 100) # TODO FK
    debt_date = models.DateField()
    debt_amt = models.IntegerField()
    penalty = models.IntegerField()
    payment = models.IntegerField()
    metered = models.BooleanField()
    balance = models.IntegerField()
    status = models.CharField(max_length=50) # TODO Choice
    no_occurrences = models.IntegerField() # TODO what is this



class Case(models.Model):
    nov = models.CharField(max_length=25,unique=True)
    street_dir = models.CharField(max_length=5)
    street_name = models.CharField(max_length=50)
    zip_plus_four = models.IntegerField()
    disposition = models.CharField(max_length=100)
    admin_cost = models.IntegerField()
    sanction_cost = models.IntegerField()
    penalty = models.IntegerField()
    respondent = models.CharField(max_length=100)

