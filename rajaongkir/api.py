from __future__ import unicode_literals
import requests
import json
from json.encoder import JSONEncoder

# list jenis pengiriman
JNE = 'jne'
POS = 'pos'
TIKI = 'tiki'
ALL_COURIER = 'all'


class RequestApi(object):
    """Request API"""
    json_encoder_class = JSONEncoder

    def __init__(self, endpoint):
        self.endpoint = endpoint

    def get(self, headers=None, url_parameters={}):
        return requests.get(
            self.endpoint,
            params=url_parameters,
            headers=headers
        )

    def post(self, headers=None, url_parameters={}, payload={}):
        return requests.post(
            self.endpoint,
            data=json.dumps(payload, cls=self.json_encoder_class),
            params=url_parameters,
            headers=headers
        )

    def put(self, headers=None, url_parameters={}, payload={}):
        return requests.put(
            self.endpoint,
            data=json.dumps(payload, cls=self.json_encoder_class),
            params=url_parameters,
            headers=headers
        )

    def delete(self, headers=None, url_parameters={}):
        return requests.delete(
            self.endpoint,
            params=url_parameters,
            headers=headers
        )

    def options(self, headers=None, url_parameters={}):
        return requests.options(
            self.endpoint,
            params=url_parameters,
            headers=headers
        )


class ApiErrorException(Exception):
    pass


class RajaOngkirApi(object):

    key_list = 'rajaongkir'
    endpoint = 'http://api.rajaongkir.com/starter/'

    def __init__(self, api_key):
        self.api_key = api_key

    @classmethod
    def __grab(cls, json_results):
        return json_results.get(cls.key_list)

    @staticmethod
    def __status(response_json):
        if not response_json:
            raise ApiErrorException('Response Api is None, cannot fetch the status of api')

        status = response_json.get('status')

        assert status is not None, \
            'Response Status is not Available'

        assert status.get('code') == requests.codes.ok, \
            'Response status not clear, should be any error occurred: {}'.format(status.get('description'))

    def __get(self, service_endpoint, params=None):
        req_params = {
            'headers': {
                'Accept': 'application/json',
                'key': self.api_key
            }
        }

        if params is not None:
            req_params['url_parameters'] = params

        api = RequestApi(endpoint=service_endpoint)
        response = api.get(**req_params)

        return self.__grab(response.json()) if response.status_code == requests.codes.ok else None

    @staticmethod
    def __parse(response_json):
        return response_json.get('results') if response_json is not None else None

    def provinces(self):
        # list provinsi
        provinces = self.__get('{}province'.format(self.endpoint))

        self.__status(provinces)

        return self.__parse(provinces)

    def province_by_id(self, province_id):
        # provinsi by Id
        province = self.__get('{}province'.format(self.endpoint), params={'id': province_id})

        self.__status(province)

        return self.__parse(province)

    def cities(self):
        # list kota
        cities = self.__get('{}city'.format(self.endpoint))

        self.__status(cities)

        return self.__parse(cities)

    def city_by_id(self, city_id):
        # kota by Id
        city = self.__get('{}city'.format(self.endpoint), params={'id': city_id})

        self.__status(city)

        return self.__parse(city)

    def cities_by_province(self, province_id):
        """Get specific kota by provinsi id

        """
        city = self.__get('{}city'.format(self.endpoint), params={'province': province_id})

        self.__status(city)

        return self.__parse(city)

    def city_by_province_and_city(self, province_id, city_id):
        """Get specific kota by provinsi and city id
        """
        city = self.__get('{}city'.format(self.endpoint), params={'id': city_id, 'province': province_id})

        self.__status(city)

        return self.__parse(city)

    def cost_between_city(self, source, destination, weight_in_grams=0, courier=ALL_COURIER):
        """Get cost result"""
        post_data = {
            u"origin": source,
            u"destination": destination,
            u"weight": int(weight_in_grams),
            u"courier": courier
        }

        api = RequestApi(endpoint='{}cost'.format(self.endpoint))
        response = api.post(
            headers={
                'key': self.api_key,
                'Accept': 'application/json',
                'Content-Type': 'application/json',
                'charset': 'utf8'
            },
            payload=post_data
        )

        costs = self.__grab(response.json()) if response.status_code == requests.codes.ok else None

        self.__status(costs)

        return self.__parse(costs)
