#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4


from django.template import RequestContext
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.shortcuts import render_to_response, get_object_or_404
from django.views.decorators.http import require_GET, require_http_methods
from rapidsms.utils import web_message
from rapidsms.conf import settings
from .forms import *
from .models import *
from .tables import *
from . import utils
from birth.models import *
from birthreg.models import *
from datetime import datetime
from django.contrib.auth.decorators import login_required
from django.db.models import Sum, Count



def _breadcrumbs(location=None, first_caption="Planet Earth"):
    """
    Return the breadcrumb trail leading to ``location``. To avoid the
    trail being empty when browsing the entire world, the caption of the
    first crumb is hard coded.
    """

    breadcrumbs = [(first_caption, reverse(locations))]

    if location is not None:
        for loc in location.path:
            type = ContentType.objects.get_for_model(loc)
            url = reverse(locations, args=(loc.uid,))
            breadcrumbs.append((loc, url))

    return breadcrumbs


class LocationTypeStub(object):
    """
    This is a shim class, to encapsulate the nested type/location
    structure, and keep the code out of the template. It's not useful
    anywhere else, so I haven't moved it into a template tag.
    """

    def __init__(self, type, req, loc):
        self._type = type
        self._req = req
        self._loc = loc

    def singular(self):
        return self._type._meta.verbose_name

    def plural(self):
        return self._type._meta.verbose_name_plural

    def name(self):
        return self._type._meta.module_name

    def content_type(self):
        return ContentType.objects.get_for_model(
            self._loc)

    def prefix(self):
        return self.name() + "-"

    def table(self):
        return LocationTable(
            self.locations(),
            request=self._req,
            prefix=self.prefix())

    def form(self):
        return utils.form_for_model(
            self._type)()

    def locations(self):
        if self._loc is not None:
            return self._type.objects.filter(
                parent_type=self.content_type(),
                parent_id=self._loc.pk)

        else:
            return self._type.objects.filter(
                parent_type=None)

    def is_empty(self):
        return self.locations().count() == 0

@login_required(login_url='/rapidsms/login/')
def locations(req, location_uid=None):

    view_location = None
    munic = Municipality.objects.raw("select m.id , m.municipality_name,m.latitude,m.longitude ,sum(b.number_children) as sum  from birth_caseold as b, birth_reporter as r, birth_municipality as m where b.reporter_id = r.id and r.municipality_id = m.id group by m.id")
    cases = Case.objects.raw("select b.id, concat(b.father_name,' ',b.father_surname) as fullname, b.village, b.number_children, date(b.datetime) as datetime, m.id as m_id from birth_caseold as b, birth_reporter as r, birth_municipality as m where b.reporter_id = r.id and r.municipality_id = m.id order by b.datetime desc")
    sum_cases = CaseOld.objects.aggregate(Sum("number_children"), Count("number_children"))

    new_munic = Municipality.objects.raw("select  id , municipality_name ,latitude,longitude ,sum(sum1) as sum from (select m.id , m.municipality_name,m.latitude,m.longitude ,sum(b.number_children) as sum1  from birthreg_case as b, birthreg_reporter as r, birthreg_municipality as m where b.reporter_id = r.id and r.municipality_id = m.id group by m.id UNION select m.id , m.municipality_name,m.latitude,m.longitude ,sum(b.number_children) as sum1  from birth_caseold as b, birth_reporter as r, birth_municipality as m where b.reporter_id = r.id and r.municipality_id = m.id group by m.id) as munic group by id")
    new_cases = Case.objects.raw("select id,  fullname, village, number_children, datetime,time,  m_id FROM (select b.id, concat(b.parent_name,' ',b.parent_surname) as fullname, b.village, b.number_children, date(b.datetime) as datetime, time(b.datetime) as time, m.id as m_id from birthreg_case as b, birthreg_reporter as r, birthreg_municipality as m where b.reporter_id = r.id and r.municipality_id = m.id union all select b.id, concat(b.father_name,' ',b.father_surname) as fullname, b.village, b.number_children, date(b.datetime) as datetime, time(b.datetime) as time, m.id as m_id from birth_caseold as b, birth_reporter as r, birth_municipality as m where b.reporter_id = r.id and r.municipality_id = m.id  ) as cases order by datetime desc, time desc")
    new_sum_cases = Case.objects.aggregate(Sum("number_children"), Count("number_children"))
    new_case_det = CaseDetails.objects.all()

   
    for c in new_case_det:
        if c.gender == "M" or c.gender == "m" :
            c.gender = "Mashkull"
        else:
            c.gender = "Femer"

    if location_uid is not None:
        view_location = Location.get_for_uid(
            location_uid)

    if req.method == "POST":
        model_class = utils.get_model(req.POST["type"])
        form_class = utils.form_for_model(model_class)
        model = None

        if req.POST.get("id", None):
            model = get_object_or_404(
                model_class, pk=req.POST["id"])

            if req.POST["submit"] == "Delete":
                model.delete()
                return HttpResponseRedirect(
                    reverse(view_location))

        form = form_class(instance=model, data=req.POST)

        if form.is_valid():
            model = form.save()

            if req.POST.get("parent_type", None) and req.POST.get("parent_id", None):
                parent_class = utils.get_model(req.POST["parent_type"])
                parent = get_object_or_404(parent_class, pk=req.POST["parent_id"])
                model.parent = parent
                model.save()

                return HttpResponseRedirect(
                    reverse(locations, args=(parent.uid,)))

            return HttpResponseRedirect(
                reverse(locations))

    types = [
        LocationTypeStub(type, req, view_location)
        for type in Location.subclasses()]

    return render_to_response(
        "locations/dashboard.html", {
            "breadcrumbs": _breadcrumbs(view_location),
            "location": view_location,
            "location_types": types,
            "munic":munic,
            "cases":cases,
            "sum_cases":sum_cases,
            "new_sum_cases":new_sum_cases,
            "new_munic":new_munic,
            "new_cases":new_cases,
            "new_case_det":new_case_det,
            # from rapidsms.contrib.locations.settings
            "default_latitude":  settings.MAP_DEFAULT_LATITUDE,
            "default_longitude": settings.MAP_DEFAULT_LONGITUDE,

            # if there are no locationtypes, then we should display a
            # big error, since this app is useless without them.
            "no_location_types": (len(types) == 0)
        }, context_instance=RequestContext(req)
     )

# def convertDateFormat(oldDate):
#     month = oldDate.split("-").[1]

#     return {
#         '01' : oldDate.replace("-"," "),
#     }[month]