from birthreg.models import *
from django.contrib import admin



class CaseAdmin(admin.ModelAdmin):
	verbose_name = "asd"
	fields = ["id","parent_name","parent_surname","village","number_children","datetime", "reporter"]
	#def __unicode__ (self):
        		#return "#"+str(self.id)+" - "+self.father_name+" "+self.father_surname+" ("+str(self.number_children)+") - "+self.reporter.municipality.municipality_name

class CaseDetailsAdmin(admin.ModelAdmin):
	fields = ["id","case","birth_year","gender","birthplace"]

class TemporaryCaseAdmin(admin.ModelAdmin):
	fields = ["id","parent_name","parent_surname","village","number_children","datetime", "reporter"]
	#def __unicode__ (self):
        		#return "#"+str(self.id)+" - "+self.father_name+" "+self.father_surname+" ("+str(self.number_children)+") - "+self.reporter.municipality.municipality_name

class TemporaryCaseDetailsAdmin(admin.ModelAdmin):
	fields = ["id","case","birth_year","gender","birthplace"]

class ReporterAdmin(admin.ModelAdmin):
	fields = ["id","phone_number","language","municipality","fullname"]

class MunicAdmin(admin.ModelAdmin):
	fields = ["id","municipality_name","latitude","longitude", "region"]

class RegionAdmin(admin.ModelAdmin):
	fields = ["id","region_name"]

class LangAdmin(admin.ModelAdmin):
	fields = ["id","language_name","new_success","new_general_error","new_pin_error","new_three_error","new_birthdetails_error","new_field_error","edit_success","edti_general_error","edit_pin_error","edit_case_error","edit_field_error","edit_missingfield_error"]
	


#class CaseAdmin(admin.ModelAdmin):
#	fields = ["id","father_name","father_surname","mother_name","mother_surname","telephone","village", "number_children", "reporter_id"]


admin.site.register(Case,CaseAdmin)
admin.site.register(CaseDetails,CaseDetailsAdmin)
admin.site.register(TempCase,TemporaryCaseAdmin)
admin.site.register(TempCaseDetails,TemporaryCaseDetailsAdmin)
admin.site.register(Reporter,ReporterAdmin)
admin.site.register(Municipality,MunicAdmin)
admin.site.register(Regions,RegionAdmin)
admin.site.register(Language,LangAdmin)

