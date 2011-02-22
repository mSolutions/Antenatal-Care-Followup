from models import *


class Scope:

        def __init__(self, location):
                self.is_global =  None
                self.location = location
                self.woreda_id = -1
                self.subcity_id = -1
                self.region_id = -1

        def __unicode__(self):
                if self.location == None:
                        return u'All'
                else:
                        return self.location.name

        def woreda(self):
                if self.is_global:
                        return Location.objects.filter(type__name = 'woreda')
                else:
                        return filter(lambda loc: loc.type.name.lower() == 'woreda',
                                      self.location.ancestors(include_self=True))

        def set_woreda(self, woreda_id):
                self.woreda_id = woreda_id
                if woreda_id == -1:
                        self.location = None
                else:
                        try:
                                self.location = Location.objects.get(id = woreda_id)
                        except Location.DoesNotExist:
                                self.location = None
        def subcity(self):
                if self.is_global:
                        return Location.objects.filter(type__name = 'Sub-city')
                else:
                        return filter(lambda loc: loc.type.name.lower() == 'sub-city',
                                      self.location.ancestors(include_self=True))

        def set_subcity(self, subcity_id):
                self.subcity_id = subcity_id
                if subcity_id == -1:
                        self.location = None
                else:
                        try:
                                self.location = Location.objects.get(id = subcity_id)
                        except Location.DoesNotExist:
                                self.location = None

        
        def region(self):
                if self.is_global:
                        return Location.objects.filter(type__name = 'Health Bureau')
                else:
                        return filter(lambda loc: loc.type.name.lower() == 'Health Bureau',
                                      self.location.ancestors(include_self=True))

        def set_region(self, region_id):
                self.region_id = region_id
                if region_id == -1:
                        self.location = None
                else:
                        try:
                                self.location = Location.objects.get(id = region_id)
                        except Location.DoesNotExist:
                                self.location = None

        def health_centers(self):
                ''' Returns the health centers within the scope location '''
                if  self.location == None:
                        return Location.objects.all()
                else:
                        health_prof_location = self.location
                        child_locations = health_prof_location.descendants(include_self = True)
                        return child_locations
                

        def health_professionals(self):
                '''Return the health professionals within the scope location '''
                if self.location == None:
                        return HealthProfessional.objects.all()
                else:
                        health_centers = self.health_centers()
                        health_profs = []
                        for health_prof in HealthProfessional.objects.all():
                                if health_prof.location in health_centers:
                                        health_profs.append(health_prof)
                        return health_profs
                                        
                                
                        

        
        def mothers(self):
                ''' Return the mothers '''
                health_centers = self.health_centers()
                health_profs = self.health_professionals()
                mothers = []
                for mother in Mother.objects.all():
                        if mother.registered_by in health_profs:
                                mothers.append(mother)
                return mothers


        def mother_history(self):
                ''' Return the rutf entries which are reported
                from location in that is in the user's scope'''
                pass

        def mother_status(self):
                ''' Return the rutf web_users who worker within the scope location '''
                pass



def define_scope(f):
        ''' Defines the scope for any webuser '''

        def _inner(request, *args, **kwargs):
                health_prof = HealthProfessional.by_user(request.user)
                scope = Scope(health_prof.location)
                if scope.is_global:
                        if request.method == 'POST' and 'woreda' in request.POST:
                                request.session['woreda'] = int(request.POST['woreda'])
                                scope.set_woreda(request.session.get('woreda',-1))
                                
                        elif request.method == 'POST' and 'sub-city' in request.POST:
                                request.session['sub-city'] = int(request.POST['sub-city'])
                                scope.set_subcity(request.session.get('sub-city',-1))
                                
                        elif request.method == 'POST' and 'region' in request.POST:
                                request.session['region'] = int(request.POST['region'])
                                scope.set_region(request.session.get('region',-1))

                return f(request, scope, *args, **kwargs)
        return _inner

