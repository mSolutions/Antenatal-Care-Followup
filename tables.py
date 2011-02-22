
from .models import *

import django_tables as tables

  

class MotherHistoryTable(tables.Table):
    #pk = tables.Column(visible=False, sortable=False)
    total_pregnancy = tables.Column(verbose_name = 'Total pregnancy')
    total_delivery = tables.Column(verbose_name = 'Total delivery')
    total_live_birth = tables.Column(verbose_name = 'Total live_birth')
    total_live_children = tables.Column(verbose_name = 'Total live children')


class MotherStatusTable(tables.Table):
    #pk = tables.Column(visible=False, sortable=False)
    hiv_status = tables.Column(verbose_name = 'HIV Status')
    blood_pressure = tables.Column(verbose_name = 'Blood Pressure')
    weight = tables.Column(verbose_name = 'Weight')
    #height = tables.Column(verbose_name = 'Height')
    other_health_cases = tables.Column(verbose_name = 'Other Cases')
    date_visited = tables.Column(verbose_name = 'Date Visited')
