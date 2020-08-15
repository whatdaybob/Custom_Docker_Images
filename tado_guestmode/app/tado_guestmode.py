import time
import requests
import json
import os
import yaml
from utils import checkconfig  # NOQA

CONFIGPATH = os.environ['CONFIGPATH']


class TadoAPI():

    access_token = None
    access_token_expiration = None
    guest_device = None

    def __init__(self):
        """Set up app with config"""
        checkconfig()
        with open(
            CONFIGPATH,
            "r"
        ) as ymlfile:
            cfg = yaml.load(
                ymlfile,
                Loader=yaml.BaseLoader
            )

        self.host = "https://auth.tado.com/oauth/token"
        self.username = cfg['tado']['user']
        self.password = cfg['tado']['pass']
        self.secret = cfg['tado']['secret']
        self.api_calls = 0
        self.apiurl = 'https://my.tado.com/api'
        self.mobileurl = 'https://my.tado.com/mobile'
        self.mobileversion = '1.9'
        # self.session = requests.Session()

        try:
            self.access_token = self.getAccessToken()
            if self.access_token is None:
                raise Exception("Request for access token failed.")
        except Exception as e:
            print(e)
        else:
            self.access_token_expiration = time.time() + 599

        try:
            self.params = {'Authorization': 'Bearer ' + self.access_token}
            if self.params is None:
                raise Exception("Can't set Authorisation string")
        except Exception as e:
            print(e)
        else:
            pass

        try:
            self.home_id = self.getHomeId()
            if self.home_id is None:
                raise Exception("Couldn't obtain Home Id.")
        except Exception as e:
            print(e)
        else:
            pass

        try:
            self.home_latitude, self.home_longitude = self.getHome()
            if self.home_latitude is None:
                raise Exception("Couldn't obtain Coordinates.")
        except Exception as e:
            print(e)
        else:
            pass

        try:
            self.guest_device = self.getMobileDevices()
            if self.guest_device is None:
                raise Exception("Couldn't find a device named 'guest' with type of 'tado-connect'.")
        except Exception as e:
            print(e)
        else:
            pass

    def getAccessToken(self):
        try:
            token_body = {
                'client_id': 'tado-web-app',
                'grant_type': 'password',
                'scope': 'home.user',
                'username': self.username,
                'password': self.password,
                'client_secret': self.secret
            }
            request = requests.post(self.host, data=token_body)
            request.raise_for_status()
        except Exception as e:
            print(e)
            return None
        else:
            return request.json()['access_token']

    def getHomeId(self):
        try:
            request = requests.get('{0}/v1/me'.format(self.apiurl), headers=self.params, timeout=10)
            request.raise_for_status()
        except Exception as e:
            print(e)
            return None
        else:
            return request.json()['homeId']

    def getHome(self):
        geolocation = requests.get('{0}/v2/homes/{1}'.format(self.apiurl, self.home_id), headers=self.params, timeout=10)
        return geolocation.json()['geolocation']['latitude'], geolocation.json()['geolocation']['longitude']

    def getMobileDevices(self):
        devices = requests.get('{0}/v2/homes/{1}/mobileDevices'.format(self.apiurl, self.home_id), headers=self.params, timeout=10).json()
        try:
            for device in devices:
                if device['name'] == 'Guest':
                    guest_id = device['id']
                    return guest_id
        except Exception as e:
            print(e)
        else:
            guest_id = 0
            return guest_id

    class Decorators():
        @staticmethod
        def refreshToken(decorated):
            def wrapper(api, *args, **kwargs):
                if time.time() > api.access_token_expiration:
                    api.getAccessToken()
                return decorated(api, *args, **kwargs)

            return wrapper

    @Decorators.refreshToken
    def deleteGuest(self):
        """
            Remove guest device from tado.
        """
        try:
            if self.guest_device == 0:
                raise Exception("No guest device to delete.")
        except Exception as error:
            return False, error.args[0]
        else:
            requests.delete('{0}/v2/homes/{1}/mobileDevices/{2}'.format(self.apiurl, self.home_id, self.guest_device), headers=self.params, timeout=10)
            self.guest_device = self.getMobileDevices()
            return True, "Guest device removed."

    @Decorators.refreshToken
    def addGuest(self):
        try:
            if self.guest_device == 0:
                insert = requests.get('{0}/{1}/createAppUser?username={2}&password={3}&nickname={4}&geoTrackingEnabled=false&deviceName={5}&devicePlatform={5}&deviceUuid={5}&deviceOsVer={6}&appVersion={6}'.format(self.mobileurl, self.mobileversion, self.username, self.password, 'Guest', 'tado-connect', '0.1')).json()
                if insert['success'] is False:
                    raise Exception(insert['message'])
                self.guest_device = self.getMobileDevices()
                return True, "Guest device added"
        except Exception as error:
            return False, error.args[0]
        else:
            return False, "Guest device already exists."

    @Decorators.refreshToken
    def getGuestTracking(self):
        if self.guest_device > 0:
            trackingurl = '{0}/v2/homes/{1}/mobileDevices/{2}/settings'.format(self.apiurl, self.home_id, self.guest_device)
            status = requests.get(trackingurl, headers=self.params, timeout=10).json()['geoTrackingEnabled']
            return True, "Status checked.", status
        else:
            return False, "No guest device to check.", False

    @Decorators.refreshToken
    def updateGuestTracking(self, wanted):
        if self.guest_device > 0:
            trackingurl = '{0}/v2/homes/{1}/mobileDevices/{2}/settings'.format(self.apiurl, self.home_id, self.guest_device)
            status = requests.get(trackingurl, headers=self.params, timeout=10).json()['geoTrackingEnabled']
            if status == wanted:
                return True, "Guest device geoTracking already set to wanted status.", status
            else:
                headers = {
                    'Authorization': 'Bearer ' + self.access_token,
                    'Content-Type': 'application/json;charset=UTF-8',
                }
                data = {"geoTrackingEnabled": wanted}
                requests.put(trackingurl, headers=headers, data=json.dumps(data))
                return True, "Guest device geoTracking changed.", wanted
        else:
            return False, "No guest device to update Guest device geoTracking.", False

    @Decorators.refreshToken
    def updateGuestLocation(self):
        """
            Set guest device location to the home location
        """
        if self.guest_device > 0:
            deviceurl = '{0}/v2/homes/{1}/mobileDevices/{2}/geolocationFix'.format(self.apiurl, self.home_id, self.guest_device)
            locationFix = {"accuracy": 10, "timestamp": "2019-10-29T21:03:21.001Z", "geolocation": {"longitude": self.home_longitude, "latitude": self.home_latitude}}
            headers = {
                'Authorization': 'Bearer ' + self.access_token,
                'Content-Type': 'application/json;charset=UTF-8',
            }
            requests.put(deviceurl, headers=headers, data=json.dumps(locationFix))
            return True, "Guest device added to home"
        else:
            return False, "No guest device to update"
