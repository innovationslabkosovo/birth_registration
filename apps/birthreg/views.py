# Create your views here.
from django.template import RequestContext
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.shortcuts import render_to_response, get_object_or_404
from django.views.decorators.http import require_GET, require_http_methods
from birth.models import *
from birthreg.models import *
from datetime import datetime
from django.contrib.auth.decorators import login_required
from django.db.models import Sum, Count

#require login to view page
@login_required(login_url='/rapidsms/login/')
def locations(req):
# display un-registered children cases by locations

    #retrieve municipality details aggregated cases (first period of reporting - less data)
    munic = Municipality.objects.raw("select m.id , m.municipality_name,m.latitude,m.longitude ,sum(b.number_children) as sum  from birth_caseold as b, birth_reporter as r, birth_municipality as m where b.reporter_id = r.id and r.municipality_id = m.id group by m.id")
    cases = Case.objects.raw("select b.id, concat(b.father_name,' ',b.father_surname) as fullname, b.village, b.number_children, date(b.datetime) as datetime, m.id as m_id from birth_caseold as b, birth_reporter as r, birth_municipality as m where b.reporter_id = r.id and r.municipality_id = m.id order by b.datetime desc")
    sum_cases = CaseOld.objects.aggregate(Sum("number_children"), Count("number_children"))

    #retrieve municipality details and aggregated cases (second period of reporting - including child details data )
    new_munic = Municipality.objects.raw("select  id , municipality_name ,latitude,longitude ,sum(sum1) as sum from (select m.id , m.municipality_name,m.latitude,m.longitude ,sum(b.number_children) as sum1  from birthreg_case as b, birthreg_reporter as r, birthreg_municipality as m where b.reporter_id = r.id and r.municipality_id = m.id group by m.id UNION select m.id , m.municipality_name,m.latitude,m.longitude ,sum(b.number_children) as sum1  from birth_caseold as b, birth_reporter as r, birth_municipality as m where b.reporter_id = r.id and r.municipality_id = m.id group by m.id) as munic group by id")
    new_cases = Case.objects.raw("select id,  fullname, village, number_children, datetime,time,  m_id FROM (select b.id, concat(b.parent_name,' ',b.parent_surname) as fullname, b.village, b.number_children, date(b.datetime) as datetime, time(b.datetime) as time, m.id as m_id from birthreg_case as b, birthreg_reporter as r, birthreg_municipality as m where b.reporter_id = r.id and r.municipality_id = m.id union all select b.id, concat(b.father_name,' ',b.father_surname) as fullname, b.village, b.number_children, date(b.datetime) as datetime, time(b.datetime) as time, m.id as m_id from birth_caseold as b, birth_reporter as r, birth_municipality as m where b.reporter_id = r.id and r.municipality_id = m.id  ) as cases order by datetime desc, time desc")
    new_sum_cases = Case.objects.aggregate(Sum("number_children"), Count("number_children"))
    new_case_det = CaseDetails.objects.all()

  
    for c in new_case_det:
        if c.gender == "M" or c.gender == "m" :
            c.gender = "Mashkull"
        else:
            c.gender = "Femer"

   
   #send data to html locations.file
    return render_to_response(
        "birthreg/locations.html", {       
            "munic":munic,
            "cases":cases,
            "sum_cases":sum_cases,
            "new_sum_cases":new_sum_cases,
            "new_munic":new_munic,
            "new_cases":new_cases,
            "new_case_det":new_case_det,
          
        }, context_instance=RequestContext(req)
     )

#@transaction.commit_on_success
def visualization(req):
# visualize un-registered children using drill down High Charts

    i=0
    municipalities = []
    birthplaces = []
    male_munic = []
    female_munic =[]
    male_list ={}
    female_list ={}


    old_cases = Municipality.objects.raw("SELECT bm.id, bm.municipality_name,  sum(bc.number_children) as nchildren from birth_caseold bc INNER JOIN birth_reporter br on bc.reporter_id = br.id RIGHT OUTER JOIN birthreg_municipality bm on br.municipality_id = bm.id group by bm.id order by bm.municipality_name")
    children_by_municipality = Municipality.objects.raw("SELECT bm.id, bm.municipality_name,sum(bc.number_children), sum((select count(*) from birthreg_casedetails  where case_id = bc.id and gender = \"M\" )) as Male, sum((select count(*) from birthreg_casedetails  where case_id = bc.id and gender = \"F\"  )) as Female from  birthreg_municipality bm , birthreg_reporter as br , birthreg_case as bc where   bc.reporter_id = br.id and br.municipality_id = bm.id group by bm.municipality_name order by bm.municipality_name")
    birthplaces = BirthPlace.objects.all()
    
    # append all municipality names in a list - displayed at x-axis
    for cm in children_by_municipality:
        municipalities.append(u'%s' % (cm.municipality_name))

    for oc in old_cases:
        if oc.municipality_name not in municipalities:
            if not oc.nchildren == 0:
                municipalities.append(oc.municipality_name)

    municipalities.sort()
    
    # retrieve the sum of all cases grouped and ordered by municipality, gender, and birthplace
    male_by_birthplace = Municipality.objects.raw("SELECT bm.id,  bm.municipality_name, COUNT((SELECT COUNT(birthplace_id) FROM birthreg_casedetails WHERE birthplace_id = 1 AND case_id = bc.id AND gender=bd.gender GROUP BY gender)) AS bp1,  COUNT((SELECT COUNT(birthplace_id) FROM birthreg_casedetails WHERE birthplace_id = 2 and case_id = bc.id and gender=bd.gender GROUP BY gender)) AS bp2,  COUNT((SELECT COUNT(birthplace_id) FROM birthreg_casedetails WHERE birthplace_id = 3 and case_id = bc.id and gender=bd.gender GROUP BY gender)) AS bp3,  COUNT((SELECT COUNT(birthplace_id) FROM birthreg_casedetails WHERE birthplace_id = 4 and case_id = bc.id and gender=bd.gender GROUP BY gender)) AS bp4, COUNT((SELECT COUNT(birthplace_id) FROM birthreg_casedetails WHERE birthplace_id = 5 and case_id = bc.id and gender=bd.gender GROUP BY gender)) AS bp5, bd.gender FROM birthreg_casedetails bd INNER JOIN birthreg_case bc ON bc.id = bd.case_id INNER JOIN birthreg_reporter br ON bc.reporter_id = br.id RIGHT JOIN birthreg_municipality bm ON br.municipality_id = bm.id where bd.gender = \"M\" or bd.gender IS NULL GROUP BY bm.municipality_name, bd.gender ORDER BY bm.municipality_name")
    female_by_birthplace = Municipality.objects.raw("SELECT bm.id,  bm.municipality_name, COUNT((SELECT COUNT(birthplace_id) FROM birthreg_casedetails WHERE birthplace_id = 1 AND case_id = bc.id AND gender=bd.gender GROUP BY gender)) AS bp1,  COUNT((SELECT COUNT(birthplace_id) FROM birthreg_casedetails WHERE birthplace_id = 2 and case_id = bc.id and gender=bd.gender GROUP BY gender)) AS bp2,  COUNT((SELECT COUNT(birthplace_id) FROM birthreg_casedetails WHERE birthplace_id = 3 and case_id = bc.id and gender=bd.gender GROUP BY gender)) AS bp3,  COUNT((SELECT COUNT(birthplace_id) FROM birthreg_casedetails WHERE birthplace_id = 4 and case_id = bc.id and gender=bd.gender GROUP BY gender)) AS bp4, COUNT((SELECT COUNT(birthplace_id) FROM birthreg_casedetails WHERE birthplace_id = 5 and case_id = bc.id and gender=bd.gender GROUP BY gender)) AS bp5, bd.gender FROM birthreg_casedetails bd INNER JOIN birthreg_case bc ON bc.id = bd.case_id INNER JOIN birthreg_reporter br ON bc.reporter_id = br.id RIGHT JOIN birthreg_municipality bm ON br.municipality_id = bm.id where bd.gender = \"F\" or bd.gender IS NULL GROUP BY bm.municipality_name, bd.gender ORDER BY bm.municipality_name")
    
    #populate male list
    for mb in male_by_birthplace:
        male_list.update({mb.municipality_name:{'bp1':mb.bp1,'bp2':mb.bp2, 'bp3':mb.bp3,'bp4':mb.bp4, 'bp5':mb.bp5}})
        male_munic.append(mb.municipality_name)
    #populate female list
    for fb in female_by_birthplace:
        female_list.update({fb.municipality_name:{'bp1':fb.bp1,'bp2':fb.bp2, 'bp3':fb.bp3,'bp4':fb.bp4, 'bp5':fb.bp5}})
        female_munic.append(fb.municipality_name)

    #send data to visualization.html file
    return render_to_response(
        "birthreg/visualization.html", {
            "municipalities":municipalities,
            "male_munic":male_munic,
            "male_list":male_list,
            "female_munic":female_munic,
            "female_list":female_list,
            "old_cases":old_cases,
            "birthplaces":birthplaces
        }, context_instance=RequestContext(req)
    )
