# vim: ai sts=4 sw=4 ts=4 et
import rapidsms
import re
from models import *
from datetime import datetime
from rapidsms.apps.base import AppBase

class App (AppBase):

    # message pattern expected: 'mileage start number' or 'mileage stop number'
    # in order to take care of possible typos it will accept a mispelled milage
    # for the keyword: 'milage start number' or 'milage stop number'
    pattern = re.compile(r'^mile?age\s+(start|stop)\s+(\d+)', re.IGNORECASE)

    def start (self):
        """Configure your app in the start phase."""
        pass

    def parse (self, message):
        """Parse and annotate messages in the parse phase."""
        pass

    def handle (self, message):
        response = self.pattern.findall(message.text)
        if response:
            entry = response[0]
            entry_time = datetime.now()
            reporter = message.connection.identity
            mileage = int(entry[1])

            if entry[0].lower() == "start":
                # Persist entry in the database
                Mileage(
                    start_mileage=mileage,
                    start_time=entry_time,
                    reporter=reporter).save()

                # Generate a response
                message.respond("After your trip is completed, please send: MILEAGE STOP mileage_reading")
            elif entry[0].lower() == "stop":
                try:
                    # We attempt to find the latest "open" entry. An "open"
                    # entry is one that has been created using MILEAGE START
                    # but has not been "closed" with a MILEAGE STOP
                    reading = Mileage.objects.filter(completed=False,reporter=reporter).order_by('-start_time')[0]
                    if reading:
                        reading.stop_mileage = mileage
                        reading.stop_time = entry_time
                        reading.completed = True
                        reading.save()

                        # Reporting...
                        distance = reading.stop_mileage - reading.start_mileage
                        distance_string = "%d miles" % distance if distance > 1 else "%d mile" % distance
                        total_time = reading.stop_time - reading.start_time
                        # Had to do the following to prevent integer division by zero
                        total_seconds = 1 if not total_time.seconds else total_time.seconds
                        speed = (float(distance) / total_seconds) * 3600

                        days = hours = minutes = 0
                        time_string = ""

                        # While generating the time string, humanize the output a little bit
                        days = total_time.days
                        if days:
                            time_string += "%d days " % days if days > 1 else "%d day " % days
                        hours = total_time.seconds / 3600
                        if hours:
                            time_string += "%d hrs " % hours if hours > 1 else "%d hr " % hours
                        minutes = (total_time.seconds % 3600) / 60
                        if minutes:
                            time_string += "%d mins " % minutes if minutes > 1 else "%d min " % minutes
                        seconds = total_time.seconds % 60
                        time_string += "%d secs" % seconds if seconds > 1 else "%d sec" % seconds

                        # Generate response to send back
                        response = "Your trip of %s took %s. Your average speed was %dmph" % (distance_string, time_string.strip(), speed)
                        message.respond(response)
                except (Mileage.DoesNotExist, IndexError):
                    message.respond("You cannot complete a trip you didn't start :)")

            return True
        else:
            return False

    def cleanup (self, message):
        """Perform any clean up after all handlers have run in the
           cleanup phase."""
        pass

    def outgoing (self, message):
        """Handle outgoing message notifications."""
        pass

    def stop (self):
        """Perform global app cleanup when the application is stopped."""
        pass
