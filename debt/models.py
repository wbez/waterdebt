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
    """
    only debt currently under collection by law firms
    TODO: rename Payments
    """
    prop = models.ForeignKey(Property, null=True, on_delete=models.CASCADE)
    full_address = models.CharField(max_length = 100) 
    # address parts
    numeric_address = models.IntegerField(null=True)
    street_dir = models.CharField(max_length=1, null=True)
    street_name = models.CharField(max_length=50)
    street_suffix = models.CharField(max_length=10, null=True)
    unit = models.CharField(max_length=30, null=True)
    zipcode = models.CharField(max_length=10,null=True)
    # debt stuff
    bad_debt_no = models.CharField(max_length = 50,null=True)
    debt_collector = models.CharField(max_length = 100) # TODO FK
    debt_date = models.DateField(null=True)
    debt_amt = models.IntegerField(null=True)
    penalty = models.IntegerField(null=True)
    payment = models.IntegerField(null=True)
    payment_date = models.DateField(null=True)
    payment_water = models.IntegerField(null=True)
    payment_sewer = models.IntegerField(null=True)
    payment_other = models.IntegerField(null=True)
    payment_water_tax = models.IntegerField(null=True)
    payment_sewer_tax = models.IntegerField(null=True)
    payment_refuse = models.IntegerField(null=True)
    payment_water_penalty = models.IntegerField(null=True)
    payment_sewer_penalty = models.IntegerField(null=True)
    payment_refuse_penalty = models.IntegerField(null=True)
    fee_water = models.IntegerField(null=True)
    fee_sewer = models.IntegerField(null=True)
    fee_other = models.IntegerField(null=True)
    fee_water_tax = models.IntegerField(null=True)
    fee_sewer_tax = models.IntegerField(null=True)
    fee_refuse = models.IntegerField(null=True)
    fee_water_penalty = models.IntegerField(null=True)
    fee_sewer_penalty = models.IntegerField(null=True)
    fee_refuse_penalty = models.IntegerField(null=True)
    # balance = models.IntegerField(null=True)
    # we don't have status or no/occurrences because delinquent acct file doesn't have full addresses
    #status = models.CharField(max_length=50) # TODO Choice
    # no_occurrences = models.IntegerField() # TODO what is this

    def get_prop_cands(self):
        """
        retrieve properties 
        that might match this debt 
        on address, etc.

        per Maria, don't search on units.
        what about street direction?
        """
        return Property.objects.filter(
                numeric_address=self.numeric_address,
                street_dir=self.street_dir,
                street_name=self.street_name)


    def get_prop(self):
        """
        return matching property if only 1 matches
        """
        cands = self.get_prop_cands()
        return cands[0] if len(list(cands)) == 1 else None


class Account(models.Model):
    """
    'Delinquent accounts 2010-now.xlsx'
    all delinquent accounts 2010-2021 
    -- 'the entire universe' - M.Z.
    """
    address = models.CharField(max_length=100,null=True)
    zipcode = models.CharField(max_length=5,null=True)
    status = models.CharField(max_length=1,null=True)
    metered = models.BooleanField(null=True)
    balance = models.FloatField(null=True)
    water_balance = models.FloatField(null=True)
    sewer_balance = models.FloatField(null=True)
    tax_balance = models.FloatField(null=True)
    penalty_balance = models.FloatField(null=True)
    garbage_balance = models.FloatField(null=True)
    other_balance = models.FloatField(null=True)
    no_delinquencies = models.FloatField(null=True)
    @property
    def summed_balance(self):
        return sum([
            self.water_balance,
            self.sewer_balance,
            self.tax_balance,
            self.penalty_balance,
            self.garbage_balance,
            self.other_balance])



class Case(models.Model):
    nov = models.CharField(max_length=25,null=True)
    docket_no = models.CharField(max_length=25,null=True)
    nov_issued_date = models.DateField(null=True)
    hearing_date = models.DateField(null=True)
    street_dir = models.CharField(max_length=5,null=True)
    street_name = models.CharField(max_length=50,null=True)
    zip_code = models.CharField(max_length=10,null=True)
    violation = models.CharField(max_length=250,null=True)
    disposition = models.CharField(max_length=250,null=True)
    admin_cost = models.IntegerField(null=True)
    sanction_cost = models.IntegerField(null=True)
    fine = models.IntegerField(null=True)
    respondent = models.CharField(max_length=100,null=True)
    
    # TODO: MCV Description
    # TODO: method to look up property candidates based on limited address info + debt


class ZipCode(models.Model):
    five_digit = models.CharField(max_length=5)
    total_pop = models.IntegerField(null=True)
    majority_race = models.CharField(max_length=20,null=True)


class Vacancy(models.Model):
    prop = models.ForeignKey(Property, null=True, on_delete=models.CASCADE)
    docket_no = models.CharField(max_length=10, null=True)
    violation_no = models.CharField(max_length=197, null=True)
    issue_date = models.DateField() # TODO: models.DateField
    issue_dept = models.CharField(max_length=7, null=True)
    last_hearing_date = models.CharField(max_length=20, null=True)
    property_address = models.CharField(max_length=22,null=True)
    # address parts
    numeric_address = models.IntegerField(null=True)
    street_dir = models.CharField(max_length=1, null=True)
    street_name = models.CharField(max_length=50)
    street_suffix = models.CharField(max_length=10, null=True)
    unit = models.CharField(max_length=30, null=True)
    zipcode = models.CharField(max_length=10,null=True)
    # end address parts
    violation_type = models.CharField(max_length=20, null=True)
    entity_person = models.CharField(max_length=105, null=True)
    disposition = models.CharField(max_length=100, null=True)
    fines = models.FloatField(null=True)
    admin_costs =  models.FloatField(null=True)
    interest = models.FloatField(null=True)
    collection_atty_fees = models.FloatField(null=True)
    court_cost = models.FloatField(null=True)
    original_total_due = models.FloatField(null=True)
    total_paid = models.FloatField(null=True)
    current_due = models.FloatField(null=True)

    def get_prop_cands(self):
        """
        retrieve properties 
        that might match this debt 
        on address, etc.

        per Maria, don't search on units.
        what about street direction?
        """
        return Property.objects.filter(
                numeric_address=self.numeric_address,
                street_dir=self.street_dir,
                street_name=self.street_name)


    def get_prop(self):
        """
        return matching property if only 1 matches
        """
        cands = self.get_prop_cands()
        return cands[0] if len(list(cands)) == 1 else None

"""
class Collector(models.Model):
    pass

"""
