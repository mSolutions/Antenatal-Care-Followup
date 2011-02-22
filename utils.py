from datetime import date, timedelta
from rapidsms.contrib.scheduler.models import EventSchedule

# Messaging function to send message
from rapidsms.contrib.messaging.utils import send_message
import pygsm


from asterisk.manager import Manager

def get_scheduled_date(elapsed_week, last_visit_date, phone_number):
    scheduled_date = last_visit_date +  timedelta(weeks = 4)
    schedule_voice_call(scheduled_date, phone_number)
    return scheduled_date
    

def schedule_voice_call(scheduled_date, phone_number):
 
    #EventSchedule.objects.all().delete()
    EventSchedule.objects.create(callback='followup.utils.voice_call_generator',
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

def send_text_message(reporters = None, message = None, reporters_messages = None):
	
	# mass SMS sender is used to send a message to a
	# list of reporters.
	
	success = 0
	reporter_received = []
	reporter_not_received = []

        # send personalized message reporters
        # reporter_message is list of dictionary dictionary data type.
        # the dictioanry has "reporter" and "message" keys
        
        if reporters_messages is not None:
                for reporter_message in reporters_messages:
                        try:
                                connection = reporter_message["reporter"].default_connection
                                send_message(connection, reporter_message["message"])
                                success += 1
                                reporter_received.append(reporter_message["reporter"])
                        except Exception, e:
                                pass

                for reporter_message in reporters_messages:
                        if reporter_message["reporter"] not in reporter_received:
                                reporter_not_received.append(reporter_message["reporter"])
        
                
        else:
                # a message to list of reporters 
                for reporter in reporters:
                        try:
                                connection = reporter.default_connection
                                send_message(connection, message)
                                success += 1
                                reporter_received.append(reporter)
                        except Exception, e:
                                pass
                                #print e
                
                reporter_not_received = filter(lambda reporters: reporters not in reporter_received, reporters)
                
        return (message, reporter_received, reporter_not_received)



    
    
    
    
    
        
