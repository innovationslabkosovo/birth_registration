from django.db import models

class Language(models.Model):
    id = models.IntegerField(primary_key=True)
    language_name = models.CharField(max_length=90, blank=True)
    new_success = models.TextField()
    new_general_error = models.TextField()
    new_pin_error = models.TextField()
    new_three_error = models.TextField()
    new_birthdetails_error = models.TextField()
    new_field_error = models.TextField()
    edit_success = models.TextField()
    edti_general_error = models.TextField()
    edit_pin_error = models.TextField()
    edit_case_error = models.TextField()
    edit_field_error = models.TextField()
    edit_missingfield_error = models.TextField()

   
    def __unicode__(self):
        return self.language_name

class Regions(models.Model):
    id = models.IntegerField(primary_key=True)
    region_name = models.CharField(max_length=90, blank=True)
    
    def __unicode__(self):
        return self.region_name

class Municipality(models.Model):
    id = models.IntegerField(primary_key=True)
    municipality_name = models.CharField(max_length=90, blank=True)
    latitude = models.FloatField(blank=True)
    longitude = models.FloatField(blank=True)
    region = models.ForeignKey(Regions)

    def __unicode__(self):
        return self.municipality_name

class Reporter(models.Model):
    id = models.IntegerField(primary_key=True)
    phone_number = models.CharField(max_length=90, blank=True)
    language = models.ForeignKey(Language)
    municipality = models.ForeignKey(Municipality)
    fullname = models.CharField(max_length=90,blank=True)

    def __unicode__(self):
        return u' %s - %s ' % (self.fullname, self.language.language_name)

class BirthPlace(models.Model):
    id = models.IntegerField(primary_key=True)
    birth_place = models.CharField(max_length=90, blank=True)
    
    def __unicode__(self):
        return self.birth_place

class Case(models.Model):
    id = models.IntegerField(primary_key=True)
    parent_name = models.CharField(max_length=90, blank=True)
    parent_surname = models.CharField(max_length=90, blank=True)
    village = models.CharField(max_length=90, blank=True)
    number_children = models.IntegerField(null=True, blank=True)
    datetime = models.DateTimeField(null=True, blank=True)
    reporter = models.ForeignKey(Reporter)
    
    class Meta:
        ordering = ["datetime"]

    def __unicode__ (self):
        return u'#%s %s %s (%s) - %s' % (str(self.id),self.parent_name, self.parent_surname,str(self.number_children),self.reporter.municipality.municipality_name)

class CaseDetails(models.Model):
    id = models.IntegerField(primary_key=True)
    case = models.ForeignKey(Case)
    birth_year = models.IntegerField(null=True, blank=True)
    gender = models.CharField(max_length=10, blank=True)
    birthplace = models.ForeignKey(BirthPlace)
    def __unicode__ (self):
        return str(self.id)

class TempCase(models.Model):
    id = models.IntegerField(primary_key=True)
    parent_name = models.CharField(max_length=90, blank=True)
    parent_surname = models.CharField(max_length=90, blank=True)
    village = models.CharField(max_length=90, blank=True)
    number_children = models.IntegerField(null=True, blank=True)
    datetime = models.DateTimeField(null=True, blank=True)
    reporter = models.ForeignKey(Reporter)
    class Meta:
        ordering = ["datetime"]

    def __unicode__ (self):
        return u'#%s %s %s (%s) - %s' % (str(self.id),self.parent_name, self.parent_surname,str(self.number_children),self.reporter.municipality.municipality_name)


class TempCaseDetails(models.Model):
    id = models.IntegerField(primary_key=True)
    case = models.ForeignKey(Case)
    birth_year = models.IntegerField(null=True, blank=True)
    gender = models.CharField(max_length=10, blank=True)
    birthplace = models.ForeignKey(BirthPlace)
    def __unicode__ (self):
        return str(self.id) 
   