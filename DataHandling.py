import requests
import icalendar
import os
import json

class DataHandling:
    def __init__(self, calURL=None, userID=None, requestInfo=None):
        self.calURL = calURL
        self.requestInfo = requestInfo
        self.userID = userID

        self.dict = {}

        if self.userID != None:
            self.userPath = f"User Data/{userID}/ICS"
        if requestInfo != None:
            self.request_data()

    def write_users_url(self):
        os.makedirs(self.userPath, exist_ok=True)
        with open(f"{self.userPath}/data.json", "w+") as f:
            json.dump({"url": self.calURL}, f)

     # downloads ical from api, don't overuse
    def write_users_ical(self):
        request = requests.get(self.calURL)
        if f'{request.content}' != "b''":
            calendar = icalendar.Calendar.from_ical(request.content)
            os.makedirs(self.userPath, exist_ok=True)
            f = open(os.path.join(self.userPath, 'schedule.ical'), 'wb')
            f.write(calendar.to_ical())
            f.close()
            return True
        else:
            return False

    def request_data(self):
        if "url" in self.requestInfo:
            with open(f"{self.userPath}/data.json", "r") as f:
                self.calURL = json.load(f)["url"]

        if "ical" in self.requestInfo:

            # downloads ical from api, don't overuse
            self.write_users_ical()

        if "schedule" in self.requestInfo:
            if os.path.isfile(f'{self.userPath}/schedule.ical') is False:
                 self.write_users_ical()
            f = open(f'{self.userPath}/schedule.ical', 'rb')
            calendar = icalendar.Calendar.from_ical(f.read())
            self.scheduleShifts = {}
            for event in calendar.walk('VEVENT'):
                self.scheduleShifts[str(event.decoded("dtstart"))[5:10]] = {
                "Start": f'{event.decoded("dtstart")}'[11:16],
                "End": f'{event.decoded("dtend")}'[11:16],
                "Location": f'{event.get("description")}',
                "Description": f'{event.get("location")}'
                }

def return_meridian(time: str):
    hours, minutes = time.split(":")
    hours = int(hours)
    if hours >= 12:
        meridian = "PM"
        hours -= 12
    else:
        meridian = "AM"
    return f'{hours}:{minutes} {meridian}'
