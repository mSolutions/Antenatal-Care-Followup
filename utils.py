from datetime import date, timedelta
from rapidsms.contrib.scheduler.models import EventSchedule

# Messaging function to send message
from rapidsms.contrib.messaging.utils import send_message
import pygsm


from asterisk.manager import Manager

def get_scheduled_date(elapsed_week, last_visit_date):
    scheduled_date = last_visit_date +  timedelta(weeks = 4)
    #schedule_voice_call(scheduled_date, phone_number)
    return scheduled_date




def schedule_voice_call(scheduled_date, phone_number):
 
    #EventSchedule.objects.all().delete()
    return EventSchedule.objects.create(callback='followup.utils.voice_call_generator',
                                    months=set([scheduled_date.month]),
                                    days_of_month=set([scheduled_date.day]),
                                    hours = set([11]),
                                    minutes=set([41]),
                                    callback_kwargs = {"phone_number":phone_number})
    

def voice_call_generator(router, phone_number):
    print "*********************************************"
    print "voice call generator is executed"
    print "*********************************************"
    
    asterisk_mgr = Manager()
    asterisk_mgr_username = "andu"
    asterisk_mgr_password = "andu"
    asterisk_mgr.connect(host = '127.0.0.1', port= 5038)
    asterisk_mgr.login(asterisk_mgr_username, asterisk_mgr_password)

    channel = "SIP/alem/%s" % phone_number
    extension = "906"
    context = "outgoing"
    priority = "1"
    other_parameters = {"max_retries":"3"}

    if asterisk_mgr.connected():
        response = asterisk_mgr.originate(channel, extension, context, priority, variables = other_parameters)
        print "********** Response is  %s " % response
    else:
        print "Connection status = %s " % asterisk_mgr.connected()
        
    
##    print "*********** voice call generator *********** "
##    call_file_content = "Channel: SIP/trunkname/%s \n \
##                Application: Playback \n \
##                Data: hello-world" % phone_number
##
##    call_file_name = "/var/spool/asterisk/outgoing/%s.call" % phone_number
##    call_file = open(call_file_name, 'w')
##    call_file.write(call_file_content)
##    call_file.close()




## Modified code to send sms using pygsm

def send_text_message(mothers = None, message = None, mothers_messages = None):
	
	# mass SMS sender is used to send a message to a
	# list of mothers.
	
	success = 0
	mother_received = []
	mother_not_received = []

        # send personalized message mothers
        # mother_message is list of dictionary dictionary data type.
        # the dictioanry has "mother" and "message" keys
        
        if mothers_messages is not None:
                for mother_message in mothers_messages:
                        try:
                                connection = mother_message["mother"].default_connection
                                send_message(connection, mother_message["message"])
                                success += 1
                                mother_received.append(mother_message["mother"])
                        except Exception, e:
                                pass

                for mother_message in mothers_messages:
                        if mother_message["mother"] not in mother_received:
                                mother_not_received.append(mother_message["mother"])
        
                
        else:
                # a message to list of mothers 
                for mother in mothers:
                        try:
                                connection = mother.default_connection
                                send_message(connection, message)
                                success += 1
                                mother_received.append(mother)
                        except Exception, e:
                                pass
                                #print e
                
                mother_not_received = filter(lambda mothers: mothers not in mother_received, mothers)
                
        return (message, mother_received, mother_not_received)



    
    
    
    
    
        
