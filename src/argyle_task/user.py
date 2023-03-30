from datetime import datetime
from typing import Any, Dict, List, Optional
from json import dumps, JSONEncoder
from dataclasses import dataclass


@dataclass
class User:
    username: str
    profile_response_json: Dict[Any, Any]
    user_id: str
    name: Optional[str]
    title: Optional[str]
    description: Optional[str]
    country: Optional[str]
    city: Optional[str]
    time_zone: Optional[str]
    skills: Optional[List[str]]
    hourly_rate: Optional[str]
    languages: Optional[List[str]]
    certificates: Optional[List[str]]
    employment_history: Optional[List[str]]
    education: Optional[List[str]]
    job_categories: Optional[List[str]]
    creation_date: Optional[datetime]
    updated_on: Optional[datetime]

    def __init__(self, username, profile_response_json, user_id):
        self.username = username
        self.profile_response_json = profile_response_json
        self.user_id = user_id
        self._load_from_json()

    def _load_from_json(self):
        name = self.profile_response_json['profile']['profile']['name']
        title = self.profile_response_json['profile']['profile']['title']
        description = self.profile_response_json['profile']['profile']['description']
        country = self.profile_response_json['profile']['profile']['location']['country']
        city = self.profile_response_json['profile']['profile']['location']['city']
        time_zone = self.profile_response_json['profile']['profile']['location']['countryTimezone'].split(' ')[
            0]
        skills = [s['name']
                  for s in self.profile_response_json['profile']['profile']['skills']]
        hourly_rate = str(self.profile_response_json['profile']['stats']['hourlyRate']['amount']) + \
            self.profile_response_json['profile']['stats']['hourlyRate']['currencyCode']
        if not self.profile_response_json['profile']['languages'] is None:
            languages = [l['language']['name'] for l in self.profile_response_json['profile']['languages']]
        if not self.profile_response_json['profile']['certificates'] is None:
            certificates = [c['certificate']['name'] for c in self.profile_response_json['profile']['certificates']]
        if not self.profile_response_json['profile']['employmentHistory'] is None:
            employment_history = [f"{eh['jobTitle']} at {eh['companyName']}, {eh['city']}, {eh['country']}, s:{eh['startDate']}, e:{eh['endDate']}" for eh in self.profile_response_json['profile']['employmentHistory']]
        if not self.profile_response_json['profile']['education'] is None:
           education = [f"{e['degree']} at {e['areaOfStudy']} Department in {e['institutionName']} s:{e['dateStarted']}, e:{e['dateStarted']}" for e in self.profile_response_json['profile']['education']]
        if not self.profile_response_json['profile']['jobCategoriesV2'] is None:
            job_categories = [jc['groupName'] for jc in self.profile_response_json['profile']['jobCategoriesV2']]
        creation_date = datetime.strptime(self.profile_response_json['person']['creationDate'].split('.')[0], "%Y-%m-%dT%H:%M:%S")
        updated_on = datetime.strptime(self.profile_response_json['person']['updatedOn'].split('.')[0], "%Y-%m-%dT%H:%M:%S")

    def to_json(self) -> str:
        """This converts user information to json.

        Returns:
            str: user information represented as json
        """
        return dumps(self.__dict__, cls=DatetimeEncoder)


class DatetimeEncoder(JSONEncoder):
    def default(self, obj):
        try:
            return super().default(obj)
        except TypeError:
            return str(obj)
