from enum import StrEnum

import numpy as np
import requests
import dataddo

__HOST = 'https://api.dataddo.com'
__API_VERSION = 'v1.0'
__API_URL = __HOST + '/' + __API_VERSION
__ENDPOINT_PATH = '/get/'
__SOURCE_PATH = '/get/source/'
__FLOW_PATH = '/get/flow/'


class Token(str):
    def __init__(self, token: str):
        if token is None:
            raise ValueError('Token must be specified')
        if len(token) != 64:
            raise ValueError('Token must be 64 characters long')
        if not self.__is_hexadecimal(token):
            raise ValueError('Token must be hexadecimal')

    @staticmethod
    def __is_hexadecimal(s: str) -> bool:
        return all(c in '0123456789abcdefABCDEF' for c in s)


class __ObjectID(str):
    def __init__(self, token: str):
        if token is None:
            raise ValueError('Token must be specified')
        if len(token) != 24:
            raise ValueError('Token must be 24 characters long')
        if not self.__is_hexadecimal(token):
            raise ValueError('ObjectID must be hexadecimal')

    @staticmethod
    def __is_hexadecimal(s: str) -> bool:
        return all(c in '0123456789abcdefABCDEF' for c in s)


class FlowID(__ObjectID):
    pass


class SourceID(__ObjectID):
    pass


class EndpointID(__ObjectID):
    pass


class Format(StrEnum):
    CSV = 'csv'
    JSON = 'json'


class JSONFormat(StrEnum):
    ARRAY = '2d_array'
    OBJECT = 'object_list'


class CSVDelimiter(StrEnum):
    SEMICOLON = ';'
    COMMA = ','
    TAB = '\t'


class DataResponse(object):
    header: list[str]
    data: np.array
    type: list[dataddo.Type]
    columnID: list[str]
    total_rows: int

    def __init__(self, header: list[str], data: np.array, _type: list[dataddo.Type],
                 column_id: list[str], total_rows: int):
        self.header = header
        self.data = data
        self.type = _type
        self.columnID = column_id
        self.total_rows = total_rows


def get_source_data(token: Token, id: SourceID | EndpointID | FlowID,
                    format: Format = Format.JSON,
                    json_format: JSONFormat = JSONFormat.ARRAY,
                    csv_delimiter: CSVDelimiter = CSVDelimiter.COMMA) -> DataResponse:
    """
    Get data from a source

    :type id: SourceID | EndpointID | FlowID
    :param id: ID of the data source
    :param token: Dataddo API token
    :param format: Format of the data
    :type format: Format
    :param json_format: Format of the JSON data
    :type json_format: JSONFormat
    :param csv_delimiter: Delimiter of the CSV data
    :type csv_delimiter: CSVDelimiter
    :return: Data from the source
    """
    url = __build_url(id)
    url += '?format=' + str(format.value)
    if format == Format.JSON and json_format is not None:
        url += '&json_format=' + str(json_format.value)
    elif format == Format.CSV and csv_delimiter is not None:
        url += '&csv_delimiter=' + str(csv_delimiter.value)
    return __get_data(url, token)


def __get_data(url: str, token: Token) -> DataResponse:
    headers = {'Authorization': 'Bearer ' + str(token)}
    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        raise ValueError('Invalid response code: ' + str(response.status_code))
    data = response.json()
    return DataResponse(
        header=data['header'],
        data=np.array(data['data']),
        _type=data['type'],
        column_id=data['columnID'],
        total_rows=data['totalRows'],
    )


def __build_url(id: SourceID | EndpointID | FlowID) -> str:
    if type(id) is SourceID:
        return __API_URL + __SOURCE_PATH + str(id)
    elif type(id) is EndpointID:
        return __API_URL + __ENDPOINT_PATH + str(id)
    elif type(id) is FlowID:
        return __API_URL + __FLOW_PATH + str(id)
    else:
        raise ValueError('Unsupported data source id type, use SourceID, EndpointID or FlowID')
