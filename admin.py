from django.contrib import admin
from locations.models import *
from followup.models import *

class HealthProfessionalAdmin(admin.ModelAdmin):
    list_display = ('first_name', 'last_name', 'username', 'location', 'phone_number')
    #list_filter = ['location',]

    def queryset(self, request):
        qs = super(HealthProfessionalAdmin, self).queryset(request)
        health_prof = HealthProfessional.by_user(request.user)
        health_prof_location = health_prof.location

        if health_prof_location is not None:
            child_locations = health_prof_location.descendants(include_self = True)
            qs = qs.filter(location__in = child_locations)
            return qs
        else:
            return qs


class MotherConnectionInline(admin.TabularInline):
    model = MotherConnection
    extra = 1

##class MotherStatusInline(admin.TabularInline):
##    model = MotherStatus
##    extra = 1
##    
##    def queryset(self, request):
##        qs = super(MotherStatusInline, self).queryset(request)
##        health_prof = HealthProfessional.by_user(request.user)
##        health_prof_location = health_prof.location
##        
##        if health_prof_location is not None:
##            child_locations = health_prof_location.descendants(include_self = True)
##            qs = qs.filter(mother__location__in = child_locations)
##            # and those mothers registered by the health professionsal
##            qs = qs.filter(mother__registered_by = health_prof) 
##            return qs
##        else:
##            # and those mothers registered by the health professionsal
##            qs = qs.filter(mother__registered_by = health_prof)
##            return qs


class MotherAdmin(admin.ModelAdmin):
    inlines = [MotherConnectionInline,]
    list_display = ('first_name', 'father_name', 'grandfather_name', 'location',)
    fields = ('first_name', 'father_name', 'grandfather_name',
              'birth_date', 'location','elapsed_period', 'registered_by', 'language')
    #list_filter = ['location',]


    
    def queryset(self, request):
        qs = super(MotherAdmin, self).queryset(request)
        health_prof = HealthProfessional.by_user(request.user)
        health_prof_location = health_prof.location
        
        if health_prof_location is not None:
            child_locations = health_prof_location.descendants(include_self = True)
            qs = qs.filter(location__in = child_locations)
            # and those mothers registered by the health professionsal
            qs = qs.filter(registered_by = health_prof) 
            return qs
        else:
            # and those mothers registered by the health professionsal
            qs = qs.filter(registered_by = health_prof)
            return qs


class MotherHistoryAdmin(admin.ModelAdmin):
    list_display = ('mother', 'total_pregnancy', 'total_delivery', 'total_live_children',)

    def queryset(self, request):
        qs = super(MotherHistoryAdmin, self).queryset(request)
        health_prof = HealthProfessional.by_user(request.user)
        health_prof_location = health_prof.location
        
        if health_prof_location is not None:
            child_locations = health_prof_location.descendants(include_self = True)
            qs = qs.filter(mother__location__in = child_locations)
            # and those mothers registered by the health professionsal
            qs = qs.filter(mother__registered_by = health_prof) 
            return qs
        else:
            # and those mothers registered by the health professionsal
            qs = qs.filter(mother__registered_by = health_prof)
            return qs

class MotherStatusAdmin(admin.ModelAdmin):
    list_display = ('mother', 'hiv_status', 'blood_pressure', 'weight', )

    def queryset(self, request):
        qs = super(MotherStatusAdmin, self).queryset(request)
        health_prof = HealthProfessional.by_user(request.user)
        health_prof_location = health_prof.location
        
        if health_prof_location is not None:
            child_locations = health_prof_location.descendants(include_self = True)
            qs = qs.filter(mother__location__in = child_locations)
            # and those mothers registered by the health professionsal
            qs = qs.filter(mother__registered_by = health_prof) 
            return qs
        else:
            # and those mothers registered by the health professionsal
            qs = qs.filter(mother__registered_by = health_prof)
            return qs

class ScheduledDateAdmin(admin.ModelAdmin):
    list_display = ('mother', 'date_scheduled', 'mother_has_visited',)

    def queryset(self, request):
        qs = super(ScheduledDateAdmin, self).queryset(request)
        health_prof = HealthProfessional.by_user(request.user)
        health_prof_location = health_prof.location
        
        if health_prof_location is not None:
            child_locations = health_prof_location.descendants(include_self = True)
            qs = qs.filter(mother__location__in = child_locations)
            # and those mothers registered by the health professionsal
            qs = qs.filter(mother__registered_by = health_prof) 
            return qs
        else:
            # and those mothers registered by the health professionsal
            qs = qs.filter(mother__registered_by = health_prof)
            return qs
    
    
    
admin.site.register(HealthProfessional, HealthProfessionalAdmin)
admin.site.register(Mother, MotherAdmin)
admin.site.register(MotherHistory, MotherHistoryAdmin)
admin.site.register(MotherStatus, MotherStatusAdmin)
admin.site.register(ScheduledDate, ScheduledDateAdmin)
