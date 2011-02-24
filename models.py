from django.db import models
from locations.models import Location
from rapidsms.contrib.scheduler.models import EventSchedule
from django.contrib.auth.models import User, UserManager
from django.utils.translation import ugettext as _
from django.utils.datastructures import SortedDict
from django.db.models.signals import pre_save, post_save
from datetime import date
from utils import *
from rapidsms.models import Contact, Connection


class HealthProfessional(User):
    #name = models.CharField(max_length=30)
    #father_name = models.CharField(max_length=30)
    grandfather_name = models.CharField(max_length=30, blank=True)
    phone_number = models.CharField(max_length=15, null=True, blank=True)
    location = models.ForeignKey(Location, related_name="location assigned", null=True, blank=True)
    
    
    def __unicode__(self):
        return unicode(self.user_ptr)

    # Use UserManager to get the create_user method, etc.
    objects = UserManager()

    @classmethod
    def by_user(cls, user):
        try:
            return cls.objects.get(user_ptr=user)
        except cls.DoesNotExist:
            new_user = cls(user_ptr=user)
            new_user.save_base(raw=True)
            return new_user

    TITLE = _(u"Health Professionals")

    @property
    def title(self):
        return self.TITLE
        

    @classmethod
    def table_columns(cls):
        columns = []
        columns.append({'name': 'Full Name',})
        columns.append({'name': 'Location',})
        columns.append({'name': 'Phone Number',})
                                
        sub_columns = None
        
        return columns, sub_columns
    

    @classmethod
    def list_health_profs(cls, scope = None,location_type = None,
                         location_name = None, group = None):
            results = []

            health_profs = scope.health_professionals()
            
            if len(health_profs) == 0:
                    return results

            for health_prof in health_profs:
                    result = SortedDict()
                    result['health_prof_id'] = health_prof.id
                    result["full_name"] = "%s %s %s" % (health_prof.first_name,
                                                        health_prof.last_name, health_prof.grandfather_name)
                    if health_prof.location:
                        result['location'] = "%s %s" % (health_prof.location, health_prof.location.type)
                    result['phone_number'] = health_prof.phone_number
                    results.append(result)
            
            return results
        

class MotherConnection(Connection):
    PHONE_TYPE_CHOICES = (('Land line', 'Land line'), ('Mobile', 'Mobile'))
    phone_type = models.CharField(max_length = 10, choices = PHONE_TYPE_CHOICES, null= True, blank= True)
        
    class Meta:
        verbose_name = "Mother Connection"
		

def MotherConnection_post_save_handler(sender, **kwargs):

    instance = kwargs['instance']
    is_new_record = kwargs['created']
    phone_number = instance.identity
    mother = Mother.get_mother(phone_number)                

    if is_new_record == True:
        scheduled_date = Mother.get_scheduled_date(mother)
        event_schedule = schedule_voice_call(scheduled_date.date_scheduled, phone_number)
        
        # add reference to ScheduledDate table
        schedule = ScheduledDate.objects.filter(date_scheduled = scheduled_date.date_scheduled,
                                 mother = mother)[0]
        
        schedule.event_schedule = event_schedule
        schedule.save()
        
    else:
        # try to update the phone (if changed) 
        scheduled_date = ScheduledDate.objects.filter(mother = mother).order_by("-date_scheduled")[0]
        event_schedule = scheduled_date.event_schedule
        event_schedule.callback_kwargs['phone_number'] = phone_number
        event_schedule.save()
        
        
        
    
post_save.connect(MotherConnection_post_save_handler,
                 sender=MotherConnection)


class Mother(Contact):
    first_name = models.CharField(max_length=30)
    father_name = models.CharField(max_length=30)
    grandfather_name = models.CharField(max_length=30, blank=True)
    birth_date = models.DateField()
    location = models.ForeignKey(Location, related_name="address lived", null=True, blank=True)
    #phone_number = models.CharField(max_length=15, null=True, blank=True)
    elapsed_period = models.IntegerField(help_text= "Initial elapsed pregnancy period in weeks")
    date_registered = models.DateTimeField(auto_now_add= True)
    registered_by = models.ForeignKey(HealthProfessional, related_name="HealthProfessional", null=True, blank=True)

    def __unicode__(self):
        return "%s %s" % (self.first_name, self.father_name)

    def _get_phone_number(self):
        return self.default_connection.identity

    phone_number = property(_get_phone_number)

    @classmethod
    def get_mother(self, phone_number):
        mothers = Mother.objects.all()
        mother = filter(lambda mothers: mothers.default_connection and
                        mothers.default_connection.identity == phone_number,  mothers)[0]
        return mother

   
    @classmethod
    def get_scheduled_date(self, mother):
        scheduled_date = ScheduledDate.objects.filter(mother = mother).order_by("-date_scheduled")[0]
        return scheduled_date
        

    TITLE = _(u"Mothers")

    @property
    def title(self):
        return self.TITLE
        

    @classmethod
    def table_columns(cls):
        columns = []
        columns.append({'name': 'Full Name',})
        columns.append({'name': 'Birth Date (Age)',})
        columns.append({'name': 'Elapsed Period',})
        columns.append({'name': 'Location',})
        columns.append({'name': 'Phone Number',})
        columns.append({'name': 'Registered By',})
        columns.append({'name': 'Registered Date',})
                        
        sub_columns = None
        
        return columns, sub_columns
    

    @classmethod
    def list_mothers(cls, scope = None,location_type = None,
                         location_name = None, group = None):
            results = []

            mothers = scope.mothers()
            
            if len(mothers) == 0:
                    return results

            for mother in mothers:
                    result = SortedDict()
                    result['mother_id'] = mother.id
                    result["full_name"] = "%s %s %s" % (mother.name,mother.father_name, mother.grandfather_name)
                    result['birthdate'] = mother.birth_date
                    result['elapsed_period'] = mother.elapsed_period
                    result['location'] = mother.location
                    result['phone_number'] = mother.phone_number
                    result['registered_by'] = mother.registered_by
                    result['registered_date'] = mother.date_registered
                    results.append(result)
            
            return results


def Mother_pre_save_handler(sender, **kwargs):

    instance = kwargs['instance']

pre_save.connect(Mother_pre_save_handler,
                 sender=Mother)


def Mother_post_save_handler(sender, **kwargs):
    instance = kwargs['instance']
    is_new_record = kwargs['created']
    if is_new_record == True:
        elapsed_week = instance.elapsed_period
        today = date.today()
        scheduled_date = get_scheduled_date(elapsed_week, today)
        schedule = ScheduledDate(date_scheduled = scheduled_date,
                                 mother = instance)
        schedule.save()
    
post_save.connect(Mother_post_save_handler,
                 sender=Mother)

            

class MotherHistory(models.Model):
    total_pregnancy = models.IntegerField(help_text= "Total number of pregnancy including current")
    total_delivery = models.IntegerField(help_text= "Total number of deliveries including this and still birth")
    total_live_birth = models.IntegerField(help_text= "Total number of live birth")
    total_live_children = models.IntegerField(help_text= "Total number of children at present")
    mother = models.ForeignKey(Mother)

    class Meta:
        verbose_name = "Mother History"
        verbose_name_plural = "Mother Histories"
        
    
class MotherStatus(models.Model):
    HIV_STAUS_CHOICES = (('Positive', 'Positive'), ('Negative', 'Negative'))
    hiv_status = models.CharField(max_length = 10, choices = HIV_STAUS_CHOICES, null= True, blank= True)
    blood_pressure = models.CharField(max_length = 20, null= True, blank= True)
    weight = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True, help_text="Weight in Kilo-gram (kg)")
    height = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True, help_text="Height in meter (m)")
    other_health_cases = models.TextField(help_text="Any other health case can be added",blank= True, null = True)
    mother = models.ForeignKey(Mother)
    date_visited = models.DateTimeField(auto_now_add= True)

    class Meta:
        verbose_name = "Mother Status"
        verbose_name_plural = "Mother Status"


def MotherStatus_post_save_handler(sender, **kwargs):
    instance = kwargs['instance']
    is_new_record = kwargs['created']
    today = date.today()
    is_registered_today = instance.mother.date_registered.date() == today
    
    if is_new_record == True and is_registered_today != True:
        phone_number = instance.mother.default_connection.identity
        elapsed_week = instance.mother.elapsed_period
        scheduled_date = get_scheduled_date(elapsed_week, today)
        event_schedule = schedule_voice_call(scheduled_date, phone_number)
        
        schedule = ScheduledDate(date_scheduled = scheduled_date,
                                 event_schedule = event_schedule,
                                 mother = instance.mother)
        schedule.save()

    
post_save.connect(MotherStatus_post_save_handler,
                 sender=MotherStatus)


class ScheduledDate(models.Model):
    date_scheduled = models.DateField()
    event_schedule = models.ForeignKey(EventSchedule, null=True, blank = True)
    mother = models.ForeignKey(Mother)
    mother_has_visited = models.BooleanField()
    
