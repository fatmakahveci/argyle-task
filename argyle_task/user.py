from datetime import datetime
import json


class DatetimeEncoder(json.JSONEncoder):
    def default(self, obj):
        try:
            return super().default(obj)
        except TypeError:
            return str(obj)


class User:
    def __init__(self, username, profile_response_json):
        # profile.identity
        self.username = username  # (unique) email or username

        profile = profile_response_json['profile']
        self.id = profile['identity']['uid']
        self.name = profile['profile']['name']
        self.title = profile['profile']['title']
        self.description = profile['profile']['description']
        self.country = profile['profile']['location']['country']
        self.city = profile['profile']['location']['city']
        self.time_zone = profile['profile']['location']['countryTimezone'].split(' ')[
            0]
        # profile.skills
        self.skills = []
        for s in profile_response_json['profile']['profile']['skills']:
            self.skills.append(s['name'])
        # profile.stats
        self.hourly_rate = str(profile['stats']['hourlyRate']['amount']) + \
            profile['stats']['hourlyRate']['currencyCode']
        # profile.languages
        self.languages = []
        for l in profile['languages']:
            self.languages.append(l['language']['name'])
        # profile.certificates
        self.certificates = []
        for c in profile['certificates']:
            self.certificates.append(c['certificate']['name'])
        # profile.employmentHistory
        self.employment_history = []
        for eh in profile['employmentHistory']:
            job_title = f"{eh['jobTitle']} at {eh['companyName']}, {eh['city']}, {eh['country']}, s:{eh['startDate']}, e:{eh['endDate']}"
            self.employment_history.append(job_title)
        # profile.education
        self.education = []
        for e in profile['education']:
            education = f"{e['degree']} at {e['areaOfStudy']} Department in {e['institutionName']} s:{e['dateStarted']}, e:{e['dateStarted']}"
            self.education.append(education)
        # profile.jobCategoriesV2
        self.job_categories = []
        for jc in profile['jobCategoriesV2']:
            self.job_categories.append(jc['groupName'])
        self.creation_date = datetime.strptime(
            profile_response_json['person']['creationDate'].split('.')[0], "%Y-%m-%dT%H:%M:%S")
        self.updated_on = datetime.strptime(
            profile_response_json['person']['updatedOn'].split('.')[0], "%Y-%m-%dT%H:%M:%S")

    def to_json(self) -> str:
        """_summary_

        Returns:
            str: _description_
        """
        return json.dumps(self.__dict__, cls=DatetimeEncoder)
