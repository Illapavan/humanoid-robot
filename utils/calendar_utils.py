import datetime
from datetime import timedelta, timezone
import os
from typing import Any, List, Optional, Union

from llama_index.readers.base import BaseReader
from llama_index.readers.schema.base import Document
from googleapiclient.discovery import build
from flask import request

SCOPES = ["https://www.googleapis.com/auth/calendar"]

class GoogleCalendarReader(BaseReader):
    
    def load_data(self, number_of_results : Optional[int] = 100, start_date : Optional[Union[str, datetime.date]] = None,) -> list[Document]:

        from googleapiclient.discovery import build

        credentials = self._get_credentials()
        service = build("calendar", "v3", credentials=credentials)

        if start_date is None:
            start_date = datetime.date.today()
        elif isinstance(start_date, str):
            start_date = datetime.date.fromisoformat(start_date)

        start_datetime = datetime.datetime.combine(start_date, datetime.time.min)
        start_datetime_utc = start_datetime.strftime("%Y-%m-%dT%H:%M:%S.%fZ")
        print("--the start time is --", start_datetime_utc)
        events_result = (
            service.events()
            .list(
                calendarId="radiusrooms@radiusagent.com",
                timeMin=start_datetime_utc,
                maxResults=number_of_results,
                singleEvents=True,
                orderBy="startTime",
            )
            .execute()
        )

        events = events_result.get("items", [])    

        results = []
        for event in events:
            if "dateTime" in event["start"]:
                start_time = event["start"]["dateTime"]
            else:
                start_time = event["start"]["date"]

            if "dateTime" in event["end"]:
                end_time = event["end"]["dateTime"]
            else:
                end_time = event["end"]["date"]

            event_string = f"Status: {event['status']}, "
            event_string += f"Summary: {event['summary']}, "
            event_string += f"Start time: {start_time}, "
            event_string += f"End time: {end_time}, "

            organizer = event.get("organizer", {})
            display_name = organizer.get("displayName", "N/A")
            email = organizer.get("email", "N/A")
            if display_name != "N/A":
                event_string += f"Organizer: {display_name} ({email})"
            else:
                event_string += f"Organizer: {email}"

            results.append(Document(event_string))

        return results

    def _get_credentials(self) -> Any:
        from google.auth.transport.requests import Request
        from google.oauth2.credentials import Credentials
        from google_auth_oauthlib.flow import InstalledAppFlow

        creds = None
        if os.path.exists("token.json"):
            creds = Credentials.from_authorized_user_file("token.json", SCOPES)
        # If there are no (valid) credentials available, let the user log in.
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    "credentials.json", SCOPES
                )
                creds = flow.run_local_server(port=3030)
            # Save the credentials for the next run
            with open("token.json", "w") as token:
                token.write(creds.to_json())

        return creds

    def getCalendarSlots(self, duration):
        events = self.getCalendarEvents()
        available_slots = []
        print("check 1")

    # Set the start and end time for the time slot range
        start_time = datetime.datetime.now(timezone.utc)
        print(start_time)
        end_time = start_time.replace(hour=20, minute=0, second=0, tzinfo=timezone.utc)  # Set the end time as 8:00 PM
        print(end_time)

        # Set the duration for the time slots (30 minutes)
        slot_duration = timedelta(minutes=duration)
        print("check 2")

        if not events:
            # if there are no events, creating slots for the whole day
            current_time = start_time
            while current_time < end_time:
                available_slots.append(
                    {
                        "start": current_time.strftime("%Y-%m-%dT%H:%M:%S%z"),
                        "end": (current_time + slot_duration).strftime("%Y-%m-%dT%H:%M:%S%z"),
                    }
                )
                current_time += slot_duration   

        else :
            events.sort(key=lambda x: x["start"].get("dateTime"))

        
            for i in range(len(events) - 1):
                current_event_end = datetime.datetime.strptime(events[i]["end"].get("dateTime"), "%Y-%m-%dT%H:%M:%S%z")
                next_event_start = datetime.datetime.strptime(events[i + 1]["start"].get("dateTime"), "%Y-%m-%dT%H:%M:%S%z")

                if next_event_start - current_event_end >= slot_duration:
                    available_slots.append(
                        {
                            "start": current_event_end,
                            "end": current_event_end + slot_duration,
                        }
                    )
            # Check if there is an available slot after the last event
            if events and "end" in events[-1]:
                last_event_end = datetime.datetime.strptime(events[-1]["end"].get("dateTime"), "%Y-%m-%dT%H:%M:%S%z")
                if end_time - last_event_end >= slot_duration:
                    # There is a gap between the last event and the end time
                    available_slots.append(
                        {
                            "start": last_event_end,
                            "end": last_event_end + slot_duration,
                        }
                    )

        slots = []
        print("check 3")
        for slot in available_slots:
            slots.append(
                {
                    "start" : self.convertISO8601ToTimestamp(slot['start']),
                    "end" : self.convertISO8601ToTimestamp(slot['end']),
                }
            )
        response = {
            "slots": slots
        }    
        # return response
        slots_string = ""
        for i, slot in enumerate(slots, start=1):
            slots_string += f"Slot {i}: {slot['start']} - {slot['end']}\n"
        slotString = slots_string.rstrip()    
        resp = {
            "response" : slotString
        }
        return resp


    def createCalendarEvent(self, data):
        credentials = self._get_credentials()
        service = build("calendar", "v3", credentials=credentials)
        data = request.get_json()
        startTime = self.convertTimestampToISO8601Format(data.get("startTime"))
        endTime = self.convertTimestampToISO8601Format(data.get("endTime"))
        description = "Connect with <> Radius Support"
        event = {
            'summary': description,
            'start': {
                'dateTime': startTime,
                'timeZone': 'Asia/Kolkata',
            },
            'end': {
                'dateTime': endTime,
                'timeZone': 'Asia/Kolkata',
            },
            'attendees': [
                {'email' : "radiussupport@radiusagent.com"},
                {'email' : data.get("email")}
            ]
        }
        event = service.events().insert(calendarId='primary', body=event).execute()
        response = {
            "response" : "event created succesfully"
        }
        return response
  



    def getCalendarEvents(self): 
        credentials = self._get_credentials()
        service = build("calendar", "v3", credentials=credentials)
        start_date = datetime.date.today()
        print(start_date)
        start_datetime = datetime.datetime.combine(start_date, datetime.time.min)
        start_datetime_utc = start_datetime.strftime("%Y-%m-%dT%H:%M:%S.%fZ")

        start_datetime = datetime.datetime.combine(start_date, datetime.time.min)
        start_datetime_utc = start_datetime.strftime("%Y-%m-%dT%H:%M:%S.%fZ")

        events_result = (
            service.events()
            .list(
                calendarId="radiusrooms@radiusagent.com",
                timeMin=start_datetime_utc,
                maxResults=50,
                singleEvents=True,
                orderBy="startTime",
            )
            .execute()
        )

        events = events_result.get("items", [])
        return events

    def convertTimestampToISO8601Format(self, timestamp):
        dt = datetime.datetime.fromtimestamp(timestamp)
        formatted_datetime = dt.strftime("%Y-%m-%dT%H:%M:%S%z")
        return formatted_datetime   

    def convertISO8601ToTimestamp(self, formatted_datetime):
        dt = datetime.datetime.strptime(str(formatted_datetime), "%Y-%m-%dT%H:%M:%S%z")
        timestamp = (dt - datetime.datetime(1970, 1, 1, tzinfo=datetime.timezone.utc)).total_seconds()
        return int(timestamp)