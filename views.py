from locations.models import *
from models import *
from scope import *
from utils import * 
from django.contrib.auth.decorators import login_required, permission_required

from django.shortcuts import render_to_response, redirect
from django.template import RequestContext
from tables import *
from django.core.paginator import Paginator, InvalidPage, EmptyPage

from django.utils.translation import ugettext as _
from datetime import date

@login_required
@define_scope
def index(request, scope):
    mothers = scope.mothers()
    health_centers = scope.health_centers()
    health_professionals = scope.health_professionals()
    schedules = ScheduledDate.objects.filter(mother__in = mothers,
                                             mother_has_visited = False)
    
    # list today's schedules
    today_schedules = filter(lambda schedules:
                             schedules.date_scheduled == date.today(),
                             schedules)
    # this weeks's schedules
    

    # mother's who missed schedules
    missed_schedules = filter(lambda schedules:
                             schedules.date_scheduled < date.today(),
                             schedules)
    
    # mothers who don't respond to voice call
    
    
    return render_to_response('index.html',
                              {'mothers': mothers,
                               'total_mothers': len(mothers),
                               'total_centers': len(health_centers),
                               'total_hps': len(health_professionals),
                               'health_centers': health_centers,
                               'health_professionals': health_professionals,},
                              context_instance=RequestContext(request))


@login_required
@define_scope
def send_sms(request, scope, mother_id = None):
        not_received = False
        mothers_not_received = []
        not_received_mother_id = []
        sms_text = ""

        if request.method == "POST":
                sms_text = request.POST['text_message'].replace('\n', '')
                #phone_numbers = request.POST['phone_number_list'].split(";")
                recipients = []
                mothers = scope.mothers()
                for mother in mothers:
                        if request.POST.has_key("mother-id-" + str(mother.pk)):
                                recipients.append(mother)

                # create a temporary connection object for the phone number lists
                (message, mother_received, mother_not_received) = send_text_message(recipients, sms_text)

                if len(mother_not_received) != 0:
                        # some mothers don't receive the message
                        not_received = True
                        mothers_not_received = mother_not_received
                        not_received_mother_id = [mother.id for mother in mother_not_received]
   
        columns, sub_columns = Mother.table_columns()
        rows = []
        results = Mother.list_mothers(scope = scope)
        
        for result in results:
                row = {}
                row['mother_id'] = mother_id = result.pop('mother_id')
                # filter mothers with phone number
                mother = Mother.objects.get(id = mother_id)
                if not_received:
                        
                        if mother.phone_number is not None and mother.id in not_received_mother_id:
                                row['cells'] = []
                                row['complete'] = False
                                for value in result.values():
                                        row['cells'].append({'value':value})
                                rows.append(row)
                else:
                        if mother.phone_number is not None:
                                row['cells'] = []
                                row['complete'] = True
                                for value in result.values():
                                        row['cells'].append({'value':value})
                                rows.append(row)

        aocolumns_js = "{ \"sType\": \"html\" },"
        for col in columns[1:]:
                if not 'colspan' in col:
                        aocolumns_js += "{ \"asSorting\": [ \"desc\", \"asc\" ], " \
                                    "\"bSearchable\": true },"
        aocolumns_js = aocolumns_js[:-1]

        webuser_location = scope.location
     
        
        return render_to_response('send_sms.html',
                                  {'columns':columns,
                                   'sub_columns':sub_columns,
                                   'rows':rows,
                                   'aocolumns_js':aocolumns_js,
                                   'not_received':not_received,
                                   'mothers_not_received':mothers_not_received,
                                   'sms_text':sms_text},
                                   context_instance=RequestContext(request))
    

@login_required
@define_scope
def mothers(request, scope):


    # web user location
    health_prof = HealthProfessional.by_user(request.user)
    health_prof_location = health_prof.location
                     
    columns, sub_columns = Mother.table_columns()
    rows = []
    results = Mother.list_mothers(scope = scope)
    
    for result in results:
        row = {}
        row['cells'] = []

        row['complete'] = True
        
        row['cells'].append({'value':result.pop("full_name"),'link': '/mother/%d' % result.pop("mother_id")})
        for value in result.values():
                        row['cells'].append({'value':value})
        rows.append(row)
      

    aocolumns_js = "{ \"sType\": \"html\" },"
    for col in columns[1:]:
            if not 'colspan' in col:
                    aocolumns_js += "{ \"asSorting\": [ \"desc\", \"asc\" ], " \
                                "\"bSearchable\": true },"
    aocolumns_js = aocolumns_js[:-1]
            
     
    
    return render_to_response('mothers.html',
                              {'columns':columns,
                               'sub_columns':sub_columns,
                               'rows':rows,
                               'aocolumns_js':aocolumns_js,},
                              context_instance=RequestContext(request))


@login_required
@define_scope
def mother(request, scope, mother_id):
    ''' Displays mother's detial information '''

    # web user location
    health_prof = HealthProfessional.by_user(request.user)
    health_prof_location = health_prof.location
    mother = Mother.objects.get(id=mother_id)

    mother_histories = MotherHistory.objects.filter(mother = mother)
    mother_statuses = MotherStatus.objects.filter(mother = mother).order_by("-date_visited")

    history_all = []
    for mother_history in mother_histories:
            history = SortedDict()
            history['total_pregnancy'] = mother_history.total_pregnancy
            history['total_delivery'] = mother_history.total_delivery
            history['total_live_birth'] = mother_history.total_live_birth
            history['total_live_children'] = mother_history.total_live_children
            history_all.append(history)

    status_all = []
    for mother_status in mother_statuses:
            status = SortedDict()
            status['hiv_status'] = mother_status.hiv_status
            status['blood_pressure'] = mother_status.blood_pressure
            status['weight'] = mother_status.weight
            #status['height'] = mother_status.height
            status['other_health_cases'] = mother_status.other_health_cases
            status['date_visited'] = mother_status.date_visited
            status_all.append(status)
            
    # Mother History Table ---------------------- 
    history_table = MotherHistoryTable(history_all, order_by=request.GET.get('sort'))
    history_rows = history_table.rows
    history_paginator = Paginator(history_rows, 10)
    try:
            history_page = int(request.GET.get('page', '1'))
    except ValueError:
            history_page = 1
    try:
          history_rows =  history_paginator.page(history_page)
    except (InvalidPage, EmptyPage):
          history_rows = history_paginator.page(history_paginator.num_pages)


    # Mother status Table ----------------------
    status_table = MotherStatusTable(status_all, order_by=request.GET.get('sort'))
    status_rows = status_table.rows
    status_paginator = Paginator(status_rows, 10)
    try:
            status_page = int(request.GET.get('page', '1'))
    except ValueError:
            status_page = 1
    try:
          status_rows =  status_paginator.page(status_page)
    except (InvalidPage, EmptyPage):
          status_rows = status_paginator.page(status_paginator.num_pages)
            


    mother_detail = {'mother': mother, 'history_table':history_table , 'history_rows':history_rows,
                     'status_table': status_table, 'status_rows':status_rows
                     }
        


    return render_to_response('mother.html',mother_detail,context_instance=RequestContext(request))


@login_required
@define_scope
def health_centers(request, scope):


    # web user location
    health_prof = HealthProfessional.by_user(request.user)
    health_prof_location = health_prof.location
                     
    rows = []

    TITLE = _(u"Health Centers")

    columns, sub_columns, results = list_health_centers(scope)

       
    for result in results:
        row = {}
        row['cells'] = []

        row['complete'] = True
        
        row['cells'].append({'value':result.pop("health_center_name"),'link': '/mother/%d' % result.pop("health_center_id")})
        for value in result.values():
                        row['cells'].append({'value':value})
        rows.append(row)
      

    aocolumns_js = "{ \"sType\": \"html\" },"
    for col in columns[1:]:
            if not 'colspan' in col:
                    aocolumns_js += "{ \"asSorting\": [ \"desc\", \"asc\" ], " \
                                "\"bSearchable\": true },"
    aocolumns_js = aocolumns_js[:-1]
            
     
    
    return render_to_response('health_centers.html',
                              {'columns':columns,
                               'sub_columns':sub_columns,
                               'rows':rows,
                               'aocolumns_js':aocolumns_js,},
                              context_instance=RequestContext(request))


@login_required
@define_scope
def health_profs(request, scope):


    # web user location
    health_prof = HealthProfessional.by_user(request.user)
    health_prof_location = health_prof.location
                     
    columns, sub_columns = HealthProfessional.table_columns()
    rows = []
    results = HealthProfessional.list_health_profs(scope = scope) 
    
    for result in results:
        row = {}
        row['cells'] = []

        row['complete'] = True
        
        row['cells'].append({'value':result.pop("full_name"),'link': '/health_prof/%d' % result.pop("health_prof_id")})
        for value in result.values():
                        row['cells'].append({'value':value})
        rows.append(row)
      

    aocolumns_js = "{ \"sType\": \"html\" },"
    for col in columns[1:]:
            if not 'colspan' in col:
                    aocolumns_js += "{ \"asSorting\": [ \"desc\", \"asc\" ], " \
                                "\"bSearchable\": true },"
    aocolumns_js = aocolumns_js[:-1]
            
     
    
    return render_to_response('health_profs.html',
                              {'columns':columns,
                               'sub_columns':sub_columns,
                               'rows':rows,
                               'aocolumns_js':aocolumns_js,},
                              context_instance=RequestContext(request))







# used to list health centers 
def list_health_centers(scope):
    columns = []
    columns.append({'name': 'Name',})
    columns.append({'name': 'Health Professionals',})
    sub_columns = None

    results = []
    health_centers = scope.health_centers()
    health_profs = scope.health_professionals()
            
    if len(health_centers) <> 0:
        for health_center in health_centers:
            result = SortedDict()
            result['health_center_id'] = health_center.id
            result['health_center_name'] = "%s %s" % (health_center.name, health_center.type)
            health_prof =filter(lambda health_profs: health_profs.location == health_center, health_profs)
            prof_names = ["%s %s" % (prof.first_name, prof.last_name) for prof in health_prof]
            prof_name = ", ".join(prof_names)
            result["prof_full_name"] = prof_name
            results.append(result)

    print "****************** health centers **********"
    print health_centers

    return (columns, sub_columns, results)










