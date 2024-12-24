import requests
import base64
from datetime import datetime, timedelta

class TokenData:
    _url = 'https://homolog-alfredo.aiqfome.com/alfredo'
    _username = ''
    _password = ''
    _useragent = ''
    _clientauth = ''
    _clientid = ''
    _clientsecret = ''
    _token = None

    def _get_auth(self):
        if self._token:
            return f'Bearer {self._token}'
        else:
            auth = base64.b64encode(f'{self._clientid}:{self._clientsecret}'.encode()).decode()
            return f'Basic {auth}'
        
    def set_token(self, token):
        self._token = token

    def delete_token(self):
        self._token = None

class Request(TokenData):
    _path: str
    error: bool

    def _post(self, headers, data = None):
        try:
            self._response = requests.post(self._url + self._path, headers = headers, json = data)
        except:
            self.error = True
            return {
                'code': 404,
                'message': 'Falha na comunicacao com o servidor'
            }
        return self._valid_response()
    
    def _get(self, headers):
        try:
            self._response = requests.get(self._url + self._path, headers = headers)
        except:
            self.error = True
            return {
                'code': 404,
                'message': 'Falha na comunicacao com o servidor'
            }
        return self._valid_response()

    def _valid_response(self):
        if self._response.status_code == 200:
            self.error = False
            return self._response.json()
        else:
            self.error = True
            try:
                return {
                    'code': self._response.status_code,
                    'message': self._response.json()['data']['message']
                }
            except:
                return {
                    'code': self._response.status_code,
                    'message': 'Nao foi possivel completar a requisicao'
                }

    def _set_path(self, path):
        self._path = path

class API(Request):
    _headers: dict
    _data: dict

    def _auth(self, refresh_token = None):
        self._headers = {
            'Authorization': self._get_auth(),
            'Content-Type': 'application/json',
            'Aiq-User-Agent': self._useragent,
            'aiq-client-authorization': self._clientauth
        }
        if refresh_token:
            self._set_path('/auth/token/refresh')
            self._headers['RefreshToken'] = refresh_token
            return self._post(self._headers)
        else:
            self._set_path('/auth/token')
            self._data = {
                'username': self._username,
                'password': self._password
            }
            return self._post(self._headers, self._data)
    
    def _execute(self, method, body = None):
        self._headers = {
            'Authorization': self._get_auth(),
            'Content-Type': 'application/json',
            'Aiq-User-Agent': self._useragent,
            'aiq-client-authorization': self._clientauth
        }
        if method == 'get':
            return self._get(self._headers)
        else:
            return self._post(self._headers, body)

class Aiq:

    def __init__(self):
        self.api = API()
        self.error = False

    def new(self):
        self._get_token()

    def set_data(self, data: dict):
        self._data = data
        self._valid_token()
    
    def get_data(self):
        return self._data

    def _valid_token(self):
        expires_in = datetime.strptime(self._data.get('token-start-date'), '%Y-%m-%d %H:%M:%S.%f') + timedelta(seconds = self._data.get('expires_in'))
        refresh_expires_in = datetime.strptime(self._data.get('token-start-date'), '%Y-%m-%d %H:%M:%S.%f') + timedelta(seconds = self._data.get('refresh_expires_in'))
        if datetime.now() > expires_in and datetime.now() < refresh_expires_in:
            self._refresh_token()
        if datetime.now() > refresh_expires_in:
            self._get_token()

    def _get_token(self):
        self.api.delete_token()
        self.response = self.api._auth()
        self._valid_data()

    def _refresh_token(self):
        self.api.delete_token()
        self.response = self.api._auth(self._data.get('refresh_token'))
        self._valid_data()

    def _valid_data(self):
        if self.api.error:
            self.error = True
        else:
            self.error = False
            self._data: dict = self.response.get('data')
            self._data['token-start-date'] = str(datetime.now())

    def get_orders(self, start, end):
        self.api.set_token(self._data.get('access_token'))
        self.api._set_path(f'/orders/search?filter[date_start]={start}&filter[date_end]={end}')
        self.response = self.api._execute(method = 'get')
        if not self.api.error:
            data = []
            for order in self.response.get('data'):
                order_id = order['order_id']
                self.api._set_path(f'/orders/{order_id}')
                data.append(self.api._execute(method = 'get').get('data'))
            self.response = {'data': data}
        return self.response
    
    def new_order(self, body):
        self.api.set_token(self._data.get('access_token'))
        self.api._set_path('/new-order')
        self.response = self.api._execute(method = 'post', body = body)
        return self.response