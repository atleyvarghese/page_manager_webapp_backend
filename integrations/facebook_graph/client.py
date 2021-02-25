import json
import urllib

import requests
from django.conf import settings


class FacebookGraphAPIClient(object):
    BASE_URL = 'https://graph.facebook.com'

    USER_DETAILS = '/v8.0/me'
    USER_ACCOUNTS = 'accounts'
    OAUTH_TOKEN = 'oauth/access_token'

    DEFAULT_FIELDS = [
        'id',
        'email',
        'first_name',
        'last_name', ]
    TIMEOUT = 5

    def __init__(self, user=None):
        self.user = user

    def make_api_request(self, url, method="GET", data=dict(), headers=dict(), params=dict(),
                         return_json_response=True):
        url = "{}/{}".format(self.BASE_URL, url)
        if method == "GET":
            response = requests.get(url, params=params, headers=headers, timeout=self.TIMEOUT)
        else:
            response = requests.post(url, data=data, headers=headers, timeout=self.TIMEOUT)
        if return_json_response:
            json_data = json.loads(response.text)
            return json_data
        else:
            return response

    def get_user_details(self, access_token):
        params = {
            'access_token': access_token,
            'fields': ','.join(self.DEFAULT_FIELDS),
        }
        return self.make_api_request(url=self.USER_DETAILS, params=params)

    def get_user_accounts(self):
        facebook_profile = self.user.facebook_profile
        facebook_account_id = facebook_profile.facebook_account_id
        primary_access_token = facebook_profile.primary_access_token
        if facebook_profile.oauth_access_token:
            oauth_access_token = facebook_profile.oauth_access_token
        else:
            oauth_access_token = self.get_oauth_access_token(primary_access_token)['access_token']
            facebook_profile.oauth_access_token = oauth_access_token
            facebook_profile.save()
        url = "/{}/{}".format(facebook_account_id, self.USER_ACCOUNTS)
        params = {
            'access_token': oauth_access_token,
        }
        response = self.make_api_request(url=url, params=params, return_json_response=False)
        if response.status_code == 400:
            facebook_profile = self.get_and_update_oauth_access_token(facebook_profile)
            params['access_token'] = facebook_profile.oauth_access_token
            response = self.make_api_request(url=url, params=params, return_json_response=False)
        json_data = json.loads(response.text)
        return json_data

    def get_oauth_access_token(self, primary_access_token):
        params = {
            'grant_type': 'fb_exchange_token',
            'client_id': settings.FACEBOOK_APP_ID,
            'client_secret': settings.FACEBOOK_APP_SECRET,
            'fb_exchange_token': primary_access_token,
        }
        return self.make_api_request(url=self.OAUTH_TOKEN, params=params)

    def get_page_details(self, page_id):
        url = "v8.0/{}/".format(page_id)
        params = {
            "fields": 'name,phone,about,emails,website',
            "access_token": self.user.facebook_profile.primary_access_token
        }
        result = self.make_api_request(url, params=params)
        return result

    def update_page_details(self, page_id, data):
        if data.get('emails'):
            data['emails'] = [data['emails'], ]
        encoded_data = urllib.parse.urlencode(data)
        url = '{}?{}&access_token={}'.format(page_id, encoded_data, self.get_long_lived_page_token(page_id))
        return self.make_api_request(url, method='POST', return_json_response=False)

    def get_and_update_oauth_access_token(self, facebook_profile):
        oauth_access_token = self.get_oauth_access_token(facebook_profile.primary_access_token)['access_token']
        facebook_profile.oauth_access_token = oauth_access_token
        facebook_profile.save()
        return facebook_profile

    def get_long_lived_page_token(self, page_id):
        params = {
            "fields": 'access_token',
            "access_token": self.user.facebook_profile.primary_access_token
        }
        url = page_id
        return self.make_api_request(url, params=params)['access_token']
