#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4

import csv

from django.template import RequestContext
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.db import transaction
from django.shortcuts import render_to_response, get_object_or_404
from rapidsms.forms import ContactForm
from rapidsms.models import Contact
from rapidsms.models import Connection
from rapidsms.models import Backend
from .tables import ContactTable
from .forms import BulkRegistrationForm
from birthreg.models import *
from birth.models import * 


@transaction.commit_on_success
def registration(req, pk=None):
    contact = None
    i=0
    j=0
    k=0
    males = 0
    females = 0
    none = 0
    municipalities = []
    birthplaces = []
    male_list ={}
    female_list ={}
    male_munic = []
    female_munic =[]
    old_cases = Municipality.objects.raw("SELECT bm.id, bm.municipality_name,  sum(bc.number_children) as nchildren from birth_caseold bc INNER JOIN birth_reporter br on bc.reporter_id = br.id RIGHT OUTER JOIN birthreg_municipality bm on br.municipality_id = bm.id group by bm.id order by bm.municipality_name")
    children_by_municipality = Municipality.objects.raw("SELECT bm.id, bm.municipality_name,sum(bc.number_children), sum((select count(*) from birthreg_casedetails  where case_id = bc.id and gender = \"M\" )) as Male, sum((select count(*) from birthreg_casedetails  where case_id = bc.id and gender = \"F\"  )) as Female from  birthreg_municipality bm , birthreg_reporter as br , birthreg_case as bc where   bc.reporter_id = br.id and br.municipality_id = bm.id group by bm.municipality_name order by bm.municipality_name")
    birthplaces = BirthPlace.objects.all()
    
    for cm in children_by_municipality:
        municipalities.append(u'%s' % (cm.municipality_name))
        i += 1

    for oc in old_cases:
        k+=1
        if oc.municipality_name not in municipalities:
            if not oc.nchildren == 0:
                municipalities.append(oc.municipality_name)
                j += 1
    
    len_old = j
    munic_difference = i + j - k -1

    municipalities.sort()
    male_by_birthplace = Municipality.objects.raw("SELECT bm.id,  bm.municipality_name, COUNT((SELECT COUNT(birthplace_id) FROM birthreg_casedetails WHERE birthplace_id = 1 AND case_id = bc.id AND gender=bd.gender GROUP BY gender)) AS bp1,  COUNT((SELECT COUNT(birthplace_id) FROM birthreg_casedetails WHERE birthplace_id = 2 and case_id = bc.id and gender=bd.gender GROUP BY gender)) AS bp2,  COUNT((SELECT COUNT(birthplace_id) FROM birthreg_casedetails WHERE birthplace_id = 3 and case_id = bc.id and gender=bd.gender GROUP BY gender)) AS bp3,  COUNT((SELECT COUNT(birthplace_id) FROM birthreg_casedetails WHERE birthplace_id = 4 and case_id = bc.id and gender=bd.gender GROUP BY gender)) AS bp4, COUNT((SELECT COUNT(birthplace_id) FROM birthreg_casedetails WHERE birthplace_id = 5 and case_id = bc.id and gender=bd.gender GROUP BY gender)) AS bp5, bd.gender FROM birthreg_casedetails bd INNER JOIN birthreg_case bc ON bc.id = bd.case_id INNER JOIN birthreg_reporter br ON bc.reporter_id = br.id RIGHT JOIN birthreg_municipality bm ON br.municipality_id = bm.id where bd.gender = \"M\" or bd.gender IS NULL GROUP BY bm.municipality_name, bd.gender ORDER BY bm.municipality_name")
    female_by_birthplace = Municipality.objects.raw("SELECT bm.id,  bm.municipality_name, COUNT((SELECT COUNT(birthplace_id) FROM birthreg_casedetails WHERE birthplace_id = 1 AND case_id = bc.id AND gender=bd.gender GROUP BY gender)) AS bp1,  COUNT((SELECT COUNT(birthplace_id) FROM birthreg_casedetails WHERE birthplace_id = 2 and case_id = bc.id and gender=bd.gender GROUP BY gender)) AS bp2,  COUNT((SELECT COUNT(birthplace_id) FROM birthreg_casedetails WHERE birthplace_id = 3 and case_id = bc.id and gender=bd.gender GROUP BY gender)) AS bp3,  COUNT((SELECT COUNT(birthplace_id) FROM birthreg_casedetails WHERE birthplace_id = 4 and case_id = bc.id and gender=bd.gender GROUP BY gender)) AS bp4, COUNT((SELECT COUNT(birthplace_id) FROM birthreg_casedetails WHERE birthplace_id = 5 and case_id = bc.id and gender=bd.gender GROUP BY gender)) AS bp5, bd.gender FROM birthreg_casedetails bd INNER JOIN birthreg_case bc ON bc.id = bd.case_id INNER JOIN birthreg_reporter br ON bc.reporter_id = br.id RIGHT JOIN birthreg_municipality bm ON br.municipality_id = bm.id where bd.gender = \"F\" or bd.gender IS NULL GROUP BY bm.municipality_name, bd.gender ORDER BY bm.municipality_name")
    

    i=0
   
    for mb in male_by_birthplace:
        male_list.update({mb.municipality_name:{'bp1':mb.bp1,'bp2':mb.bp2, 'bp3':mb.bp3,'bp4':mb.bp4, 'bp5':mb.bp5}})

        male_munic.append(mb.municipality_name)
        i=i+1
    i=0
    for fb in female_by_birthplace:
        female_list.update({fb.municipality_name:{'bp1':fb.bp1,'bp2':fb.bp2, 'bp3':fb.bp3,'bp4':fb.bp4, 'bp5':fb.bp5}})

        female_munic.append(fb.municipality_name)
        i=i+1


    # for cb in children_by_birthplace:
    #     if cb.gender == "M":
    #         males += 1
    #     elif cb.gender == "F":
    #         females +=1
    #     else:
    #         none +=1
    

    if pk is not None:
        contact = get_object_or_404(
            Contact, pk=pk)

    if req.method == "POST":

        
        if req.POST["submit"] == "Delete Contact":
            contact.delete()
            return HttpResponseRedirect(
                reverse(registration))

        elif "bulk" in req.FILES:
            # TODO use csv module
            #reader = csv.reader(open(req.FILES["bulk"].read(), "rb"))
            #for row in reader:
            for line in req.FILES["bulk"]:
                line_list = line.split(',')
                name = line_list[0].strip()
                backend_name = line_list[1].strip()
                identity = line_list[2].strip()

                contact = Contact(name=name)
                contact.save()
                # TODO deal with errors!
                backend = Backend.objects.get(name=backend_name)

                connection = Connection(backend=backend, identity=identity,\
                    contact=contact)
                connection.save()

            return HttpResponseRedirect(
                reverse(registration))
        else:
            contact_form = ContactForm(
                instance=contact,
                data=req.POST)

            if contact_form.is_valid():
                contact = contact_form.save()
                return HttpResponseRedirect(
                    reverse(registration))

    else:
        contact_form = ContactForm(
            instance=contact)
        bulk_form = BulkRegistrationForm()

    return render_to_response(
        "registration/dashboard.html", {
            "contacts_table": ContactTable(Contact.objects.all(), request=req),
            "contact_form": contact_form,
            "bulk_form": bulk_form,
            "contact": contact,
            "municipalities":municipalities,
            "children_by_municipality":children_by_municipality,
            "male_by_birthplace":male_by_birthplace,
            "female_by_birthplace":female_by_birthplace,
            "male_munic":male_munic,
            "male_list":male_list,
            "female_munic":female_munic,
            "female_list":female_list,
            "males":males,
            "females":females,
            "none":none,
            "old_cases":old_cases,
            "munic_difference":munic_difference,
            "len_old":len_old,
            "birthplaces":birthplaces
        }, context_instance=RequestContext(req)
    )
