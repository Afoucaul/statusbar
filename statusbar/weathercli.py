import logging
import os
import urllib

import geocoder
import requests


LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.INFO)


API_URL = "api.openweathermap.org"


def current_coordinates():
    try:
        lat, lon = geocoder.ip('me').latlng
        return {'lat': lat, 'lon': lon}

    except TypeError:
        return None


class Session(requests.Session):
    def __init__(self, api_key):
        super().__init__()
        self.api_key = api_key

    @classmethod
    def from_env(cls):
        return cls(os.getenv('OPENWEATHERMAP_API_KEY'))

    def get(self, endpoint, options):
        query = urllib.parse.urlencode({
            **options,
            'appid': self.api_key
        })
        url = urllib.parse.urlunparse((
            'https',
            API_URL,
            "/data/2.5/{}".format(endpoint),
            '',
            query,
            ''
        ))
        LOGGER.info('[GET] %s', url)

        return super().get(url)

    def weather(self, lon=None, lat=None, units='metric'):
        options = {'units': units}

        if lon is not None and lat is not None:
            options.update({
                'lon': lon,
                'lat': lat,
            })

        return self.get('weather', options)


if __name__ == '__main__':
    session = Session(API_URL, API_KEY)
