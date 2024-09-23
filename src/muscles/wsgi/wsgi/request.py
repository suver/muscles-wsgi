import cgi
import urllib
from urllib.parse import urlparse, urlunparse
from operator import itemgetter

from muscles.core import Dependency
from muscles.core import EventsStorageInterface
from muscles.core import inject
import json
import sys
import email.parser
import tempfile
import os
import magic
from http.cookies import SimpleCookie
from .error_handler import ApplicationException, AttributeException


def _split_on_find(content, bound):
    point = content.find(bound)
    return content[:point], content[point + len(bound):]


class ImproperBodyPartContentException(Exception):
    pass


class NonMultipartContentTypeException(Exception):
    pass


def _header_parser(string, encoding):
    major = sys.version_info[0]
    if major == 3:
        string = string.decode(encoding)
    headers = email.parser.HeaderParser().parsestr(string).items()
    return (
        (k, v) for k, v in headers
    )


class BodyPart(object):
    """
    Часть объекта ``Response`` для хранения частей тела запроса

    """

    def __init__(self, content, encoding):
        self.encoding = encoding
        headers = {}
        # Split into header section (if any) and the content
        if b'\r\n\r\n' in content:
            first, self.content = _split_on_find(content, b'\r\n\r\n')
            if first != b'':
                headers = _header_parser(first.lstrip(), encoding)
        else:
            raise ImproperBodyPartContentException(
                'content does not contain CR-LF-CR-LF'
            )
        self.headers = headers
        self._name = None
        self._filename = None
        for k, v in self.headers:
            if k == 'Content-Disposition':
                v = v.split("; ")
                for vi in v:
                    u = vi.split("=")
                    if len(u) > 1:
                        if u[0] == 'name':
                            self._name = u[1].strip('"')
                        if u[0] == 'filename':
                            self._filename = u[1].strip('"')

    @property
    def text(self):
        """
        Контент части запроса
        :return: unicode
        """
        return self.content.decode(self.encoding)

    @property
    def name(self):
        """
        Имя раздела в unicode.
        :return: unicode
        """
        try:
            return self._name.decode(self.encoding)
        except:
            return self._name

    @property
    def filename(self):
        """
        Имя файла
        :return: unicode
        """
        try:
            return self._filename.decode(self.encoding)
        except:
            return self._filename


class FileStorage:
    """
    Хранилище файлов
    """

    def __init__(self, name, value, filename=None, mime_type=None, file_type=None, bytes_read=0):
        self._name = name
        self._value = value
        # TODO Если оставить сохранение в файл то открывается уязвимость переполнения файловой системы,
        #  лучше переделать на поток
        self.fp = tempfile.NamedTemporaryFile(prefix="tempfile_", suffix="_muscular")
        self.fp.write(self._value)
        self.fp.seek(0)
        self._filepath = self.fp.name
        self._filename = filename
        self._file_type = file_type
        if mime_type is None:
            mime = magic.Magic(mime=True)
            mime_type = mime.from_buffer(self._value)
        self._mime_type = mime_type
        self._bytes_read = bytes_read

    def __del__(self):
        try:
            self.fp.close()
        except AttributeError:
            pass

    def load(self):
        return self.fp.read()

    @property
    def name(self):
        """
        Имя файла
        :return: string
        """
        return self._name

    @property
    def filepath(self):
        """
        Путь к файлу
        :return: string
        """
        return self._filepath

    @property
    def filename(self):
        """
        Имя файла
        :return: string
        """
        return self._filename

    @property
    def file_type(self):
        """
        Тип файла
        :return: string
        """
        return self._file_type

    @property
    def bytes_read(self):
        """
        Байт файла
        :return: string
        """
        return self._bytes_read

    @property
    def value(self):
        return self._value

    def __str__(self):
        return "FileStorage(%r, %r)" % (self._mime_type, self.filename)

    def __repr__(self):
        """Возвращает строку для отображения"""
        return "FileStorage(%r, %r)" % (self._mime_type, self.filename)

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.fp.close()

    def save(self, filepath=None):
        """
        Сохраняет файл по указаному пути
        :param filepath: путь сохранения файла
        :return: None
        """
        self._filepath = os.path.abspath(filepath)
        self._filename = os.path.basename(self._filepath)
        fp = open(filepath, 'wb')
        fp.write(self.fp.read())
        self.fp.close()
        self.fp = fp


class FieldStorage:
    """
    Хранилище полей формы
    """

    def __init__(self, name, value):
        self._name = name
        self._value = value

    @property
    def name(self):
        """
        Название поля
        :return: string
        """
        return self._name

    @property
    def value(self):
        """
        Значение формы
        :return: string
        """
        return self._value

    def __str__(self):
        return str(self._value)

    def __repr__(self):
        """Возвращает строку для отображения"""
        return "FieldStorage(%r, %r)" % (self.name, self.value)

    def __enter__(self):
        return self


class Request:
    """
    Тело запроса к сервверу
    """

    __charset = 'utf8'
    _before_start = []

    def __init__(self,
                 protocol: str = None,
                 url: str = None,
                 method: tuple = None,
                 server: tuple = None,
                 remote_addr: tuple = None,
                 headers: dict = {},
                 body=None,
                 is_json=False,
                 is_xml=False,
                 is_form=False,
                 is_buffer=False,
                 **kwargs
                 ):
        """
        Конструктор запроса

        :param protocol: Протокол запроса
        :param url: URL запроса
        :param method: Метод запроса GET, POST, PUT, DELETE, ...
        :param server: Сервер
        :param remote_addr: Откуда поступил запрос
        :param headers: Заголовки запроса
        :param body: Тело запроса
        :param kwargs:
        """

        #: Parsed parts of the multipart response body
        self.parts = tuple()

        self._is_json = is_json
        self._is_xml = is_xml
        self._is_form = is_form
        self._is_buffer = is_buffer

        #: The method the request was made with, such as ``GET``.
        self._method = method.upper()
        #: The Protocol
        self.protocol = protocol.upper()
        #: The URL
        self.url = url
        #: The address of the server. ``(host, port)``, ``(path, None)``
        #: for unix sockets, or ``None`` if not known.
        self.server = server
        #: The headers received with the request.
        self.headers = headers
        #: The address of the client sending the request.
        self.remote_addr = remote_addr

        if isinstance(body, BaseException):
            self._exception = body
            self._body = None
        else:
            self._body = body
            self._exception = None

        o = urlparse(self.url)
        self.scheme = o.scheme
        self.netloc = o.netloc
        self.path = o.path
        self._query = o.query
        self.fragment = o.fragment
        self.username = o.username
        self.password = o.password
        self.hostname = o.hostname
        self.port = o.port

        self.route = None
        self.actor = None

        """ Запускает обработку событий инициализации запроса Request """
        events = Dependency.resolve(EventsStorageInterface)
        if events is not None and events.get('init_request') is not None:
            for func in events.get('init_request'):
                func(request=self)

    @staticmethod
    @inject(EventsStorageInterface)
    def init_request(evnetStorage: EventsStorageInterface):
        """
        Декоратор, который вешает событие инициализации запроса Request

        :return:
        """
        def decorator(func):
            evnetStorage.add('init_request', func)
        return decorator

    @staticmethod
    @inject(EventsStorageInterface)
    def before_request(evnetStorage: EventsStorageInterface):
        """
        Декоратор, который вешает событие инициализации запроса Request

        :return:
        """
        def decorator(func):
            evnetStorage.add('before_request', func)
        return decorator

    @staticmethod
    @inject(EventsStorageInterface)
    def before_response(evnetStorage: EventsStorageInterface):
        """
        Декоратор, который вешает событие инициализации запроса Request

        :return:
        """
        def decorator(func):
            evnetStorage.add('before_response', func)
        return decorator

    @property
    def prefix(self) -> bool:
        """
        Префикс к адресу
        """
        chunks = self.path.split('/')
        return chunks[1] if len(chunks) > 0 and chunks[0] == '' else None

    @property
    def method(self) -> bool:
        """
        HTTP Метод
        """
        return self._method

    @property
    def is_exception(self) -> bool:
        """
        Exception?
        """
        return self._exception is not None or isinstance(self._body, BaseException)

    @property
    def exception(self) -> any:
        """
        Exception?
        """
        if self._exception is not None:
            return self._exception
        elif isinstance(self._body, BaseException):
            return self._body
        else:
            return None

    @exception.setter
    def exception(self, value: BaseException) -> None:
        """
        Exception?
        """
        self._exception = value

    @property
    def is_post(self) -> bool:
        """
        POST?
        """
        return self._method.upper() == 'post'.upper()

    @property
    def is_get(self) -> bool:
        """
        GET?
        """
        return self._method.upper() == 'get'.upper()

    @property
    def is_put(self) -> bool:
        """
        PUT?
        """
        return self._method.upper() == 'put'.upper()

    @property
    def is_delete(self) -> bool:
        """
        DELETE?
        """
        return self._method.upper() == 'delete'.upper()

    @property
    def is_secure(self) -> bool:
        """
        ``True`` Если (HTTPS or WSS).
        """
        return self.scheme in {"https", "wss"}

    @property
    def base_url(self) -> str:
        """
        Получаем разобранный урл запроса
        :return:
        """
        return urlunparse(scheme=self.scheme, hostname=self.hostname, port=self.port, path=self.path)

    @property
    def host_url(self) -> str:
        """
        Получаем хост запроса
        :return:
        """
        return urlunparse(scheme=self.scheme, hostname=self.hostname, port=self.port)

    @property
    def host(self) -> str:
        """
        Получаем хост запроса
        """
        return urlunparse(
            scheme=self.scheme, hostname=self.hostname, port=self.port
        )

    @property
    def query(self) -> dict:
        """
        Получаем часть запроса query в формате ключ/значение
        """
        return dict(urllib.parse.parse_qsl(self._query))

    @property
    def m_query(self) -> dict:
        """
        Получаем часть запроса query в формате ключ/[значения] или ключ/значение
        """
        vals = urllib.parse.parse_qsl(self._query)
        params = {}
        if vals and isinstance(vals, list):
            for val in vals:
                if val[0] in params and not isinstance(params[val[0]], list):
                    d = [params[val[0]], val[1]]
                    del params[val[0]]
                    params[val[0]] = val[1]
                    params.update({val[0]: d})
                elif val[0] in params and isinstance(params[val[0]], list):
                    params[val[0]].append(val[1])
                else:
                    params.update({val[0]: val[1]})
        return params

    @property
    def raw_query(self) -> list:
        """
        Получаем часть запроса query в RAW формате
        """
        return urllib.parse.parse_qsl(self._query)

    @property
    def cookies(self) -> "ImmutableMultiDict[str, str]":
        """
        Печеньки запроса
        :return:
        """
        if self.headers.get("Cookie"):
            cookie = SimpleCookie()
            cookie.load(self.headers.get("Cookie"))
            return {k: v.value for k, v in cookie.items()}
        else:
            return {}

    @property
    def content_length(self) -> [int, None]:
        """
        Размер запроса
        """
        if self.headers.get("Transfer-Encoding", "") == "chunked":
            return None

        content_length = self.headers.get("Content-Length")
        if content_length is not None:
            try:
                return max(0, int(content_length))
            except (ValueError, TypeError):
                pass

        return None

    @property
    def accept_language(self) -> []:
        """
        Язык запроса
        """
        accept_language = self.headers.get("Accept-Language")

        def normalized(language):
            l = language.lower().split(';q=')
            return l[0], float(l[1]) if len(l) > 1 else float(1)

        if accept_language is not None:
            accept_language = accept_language.lower().split(',')
            try:
                languages = [normalized(language) for language in accept_language]
                languages = sorted(languages, key=itemgetter(1), reverse=True)
                return [language[0] for language in languages]
            except (ValueError, TypeError) as e:
                pass
        return None

    @property
    def accept_encoding(self) -> [str, None]:
        """
        Кодировка запроса
        """
        accept_encoding = self.headers.get("Accept-Encoding")

        def normalized(encoding):
            l = encoding.lower().split(';q=')
            return l[0], float(l[1]) if len(l) > 1 else float(1)

        if accept_encoding is not None:
            accept_encoding = accept_encoding.lower().split(',')
            try:
                encodings = [normalized(encoding) for encoding in accept_encoding]
                encodings = sorted(encodings, key=itemgetter(1), reverse=True)
                return [encoding[0] for encoding in encodings]
            except (ValueError, TypeError) as e:
                pass
        return None

    @property
    def accept(self) -> [str, None]:
        """
        Accept: text/html, application/xhtml+xml, application/xml;q=0.9, */*;q=0.8
        """
        accept = self.headers.get("Accept")

        def normalized(accept):
            l = accept.lower().split(';q=')
            return l[0], float(l[1]) if len(l) > 1 else float(1)

        if accept is not None:
            accept = accept.lower().split(',')
            try:
                accepts = [normalized(acp) for acp in accept]
                accepts = sorted(accepts, key=itemgetter(1), reverse=True)
                return [accept[0] for accept in accepts]
            except (ValueError, TypeError) as e:
                pass
        return None

    @property
    def content_type(self) -> [str, None]:
        """
        Content-Type: text/html; charset=UTF-8 => text/html
        Content-Type: multipart/form-data; boundary=something => multipart/form-data
        """
        content_type = self.headers.get("Content-Type", 'text/html; charset=UTF-8')
        if content_type is not None:
            try:
                content_type = content_type.lower().split("; ")
                return content_type[0]
            except (ValueError, TypeError):
                pass

        return None

    @property
    def boundary(self) -> [str, None]:
        """

        Content-Type: text/html; charset=UTF-8 => text/html
        Content-Type: multipart/form-data; boundary=something => multipart/form-data
        """
        boundary = self.headers.get("Content-Type")
        if boundary is not None:
            try:
                boundary = boundary.split("; ")
                if len(boundary) > 1:
                    boundary = boundary[1].split("=")
                    return boundary[1] if len(boundary) > 1 and boundary[0].lower() == 'boundary' else None
                return None
            except (ValueError, TypeError):
                pass
        return None

    @property
    def user_agent(self) -> [str, None]:
        """
        Браузер пользователя
        """
        user_agent = self.headers.get("User-Agent")
        if user_agent is not None:
            try:
                return user_agent
            except (ValueError, TypeError):
                pass

        return None

    @property
    def content_charset(self) -> [str, None]:
        """
        Content-Type: text/html; charset=UTF-8 => utf-8
        Content-Type: multipart/form-data; boundary=something => None
        """
        content_type = self.headers.get("Content-Type")
        if content_type is not None:
            try:
                content_type = content_type.lower().split("; ")
                if len(content_type) > 1:
                    charset = content_type[1].split("=")
                    return charset[1].lower() if len(charset) > 1 and charset[0] == 'charset' else None
            except (ValueError, TypeError):
                pass

        return None

    @property
    def charset(self) -> [str, None]:
        """
        Кодировка
        :return:
        """
        return self.content_charset if self.content_charset else self.__charset

    @property
    def json(self):
        """
        Разбор тела пост запроса
        :return:
        """
        return self._body if self._is_json else {}

    @property
    def xml(self):
        """
        Разбор тела пост запроса
        :return:
        """
        return self._body if self._is_xml else {}

    @property
    def is_xml(self):
        """
        Разбор тела пост запроса
        :return:
        """
        return self._is_xml

    @property
    def is_json(self):
        """
        Разбор тела пост запроса
        :return:
        """
        return self._is_json

    @property
    def body(self):
        """
        Разбор тела пост запроса
        :return:
        """
        if self._body is None:
            raise AttributeException(reason="request.body is empty")
        return self._body if not self._is_buffer else None

    @property
    def raw(self):
        """
        Разбор тела пост запроса
        :return:
        """
        try:
            return self._body
        except Exception:
            return None

    @property
    def forms(self):
        """
        Разбор формы запроса
        :return:
        """
        """
        Файлы в запросе
        :return:
        """
        if not self._is_form:
            return None
        fields = {}
        for part in self._body:
            if isinstance(self._body[part], FieldStorage):
                fields[part] = self._body[part]
            elif isinstance(self._body[part], list):
                fields[part] = []
                for el_part in self._body[part]:
                    if isinstance(el_part, FieldStorage):
                        fields[part].append(el_part)
        return fields

    @property
    def buffer(self):
        """
        Разбор формы запроса
        :return:
        """
        return self._body if self._is_buffer else None

    @property
    def files(self):
        """
        Файлы в запросе
        :return:
        """
        if not self._is_form:
            return None
        files = {}
        for part in self._body:
            if isinstance(self._body[part], FileStorage):
                files[part] = self._body[part]
        return files

    @property
    def user(self):
        return self.actor


class RequestMaker:

    text_mime_types = [
        'text/html',
        'text/plain',
        'text/calendar',
        'application/xml',
        'application/json',
        'application/ld+json',
        'text/javascript',
        'text/javascript'
    ]

    def __init__(self, environ):
        self.environ = environ
        self._request_types = {
            'multipart/form-data': 'multipart',
            'application/x-www-form-urlencoded': 'form',
            'text/plain': 'text',
            'text/html': 'html',
            'application/javascript': 'javascript',
            'application/json': 'json',
            'application/xml': 'xml',
        }

    @property
    def request_type(self):
        if 'CONTENT_TYPE' not in self.environ and 'HTTP_ACCEPT' not in self.environ:
            return None
        for content_type in self._request_types:
            if 'CONTENT_TYPE' in self.environ and content_type in self.environ['CONTENT_TYPE']:
                return self._request_types[content_type]
            elif 'HTTP_ACCEPT' in self.environ and content_type in self.environ['HTTP_ACCEPT'].split(","):
                return self._request_types[content_type]

        return None

    @property
    def charset(self):
        charset = 'utf-8'
        try:
            content_type = self.environ.get('CONTENT_TYPE', 'text/html; charset=UTF-8')
            content_type = content_type.lower().split("; ")
            if len(content_type) > 1:
                _charset = content_type[1].split("=")
                charset = _charset[1].lower() if len(_charset) > 1 and _charset[0] == 'charset' else 'utf-8'
        except ValueError as e:
            pass
        return charset

    def make_body_from_multipart(self):
        fields = {}
        wsgi_input = cgi.FieldStorage(fp=self.environ['wsgi.input'], environ=self.environ, keep_blank_values=True)
        for name in wsgi_input.keys():
            if hasattr(wsgi_input[name], 'filename') and wsgi_input[name].filename is not None:
                wsgi_input[name].file.seek(0)
                fields[name] = FileStorage(name, wsgi_input[name].file.read(),
                                           filename=wsgi_input[name].filename,
                                           file_type=wsgi_input[name].type,
                                           bytes_read=wsgi_input[name].bytes_read,
                                           )
            else:
                wsgi_input[name].file.seek(0)
                fields[name] = FieldStorage(name, wsgi_input[name].file.read())

        return fields

    def make_body_from_buffer(self):
        try:
            length = int(self.environ.get('CONTENT_LENGTH', '0'))
        except ValueError:
            length = 0
        wsgi_input = self.environ['wsgi.input']
        if 'wsgi.file_wrapper' in self.environ:
            wsgi_input = self.environ['wsgi.file_wrapper'](wsgi_input, length)
        return wsgi_input.read(length)

    def make_body_from_raw(self):
        wsgi_input = self.make_body_from_buffer()
        mime = magic.Magic(mime=True)
        mime_type = mime.from_buffer(wsgi_input)
        if mime_type not in self.text_mime_types:
            wsgi_input = FileStorage(None, wsgi_input,
                                     filename=None,
                                     mime_type=mime_type,
                                     file_type=mime_type,
                                     bytes_read=len(wsgi_input),
                                     )
        return wsgi_input

    def make_body_from_json(self):
        wsgi_input = self.make_body_from_buffer()
        try:
            if len(wsgi_input) > 0:
                return json.loads(wsgi_input.decode(self.charset))
            else:
                return {}
        except json.JSONDecodeError as e:
            raise ApplicationException(reason="JSON DECODE ERROR", body=e)
        except UnicodeDecodeError as e:
            raise ApplicationException(reason="JSON DECODE ERROR", body=e)

    def make_body_from_form(self):
        wsgi_input = self.make_body_from_buffer()
        fields = {}
        data = urllib.parse.parse_qsl(wsgi_input.decode(self.charset))
        for _data in data:
            if fields.get(_data[0]) and isinstance(fields[_data[0]], list):
                fields[_data[0]].append(FieldStorage(_data[0], _data[1]))
            elif fields.get(_data[0]):
                fields[_data[0]] = [fields[_data[0]]]
                fields[_data[0]].append(FieldStorage(_data[0], _data[1]))
            else:
                fields[_data[0]] = FieldStorage(_data[0], _data[1])
        return fields

    def make_headers(self) -> dict:
        """
        офрмирует словарь заголовков запроса

        :return: dict
        """
        headers = {}
        headers.update({'Content-Length': self.environ.get('CONTENT_LENGTH', '0')})
        headers.update({'Content-Type': self.environ.get('CONTENT_TYPE', 'text/html; charset=UTF-8')})
        for key in self.environ:
            if 'HTTP_' == key[0:5]:
                headers.update({key[5:].title().replace('_', '-'): self.environ[key]})
            elif 'X-' == key[0:1]:
                headers.update({key.title(): self.environ[key]})
        return headers

    def make(self) -> Request:
        """
        Формируем объект Request

        :return: Request
        """
        environ = self.environ
        if self.request_type and hasattr(self, "make_body_from_%s" % self.request_type):
            try:
                method = getattr(self, "make_body_from_%s" % self.request_type)
                wsgi_input = method()
            except ApplicationException as ex:
                wsgi_input = ex
        else:
            wsgi_input = self.make_body_from_raw()
        request = Request(
            method=environ['REQUEST_METHOD'],
            protocol=environ['SERVER_PROTOCOL'],
            url="%s://%s%s" % (environ['UWSGI_ROUTER'], environ['HTTP_HOST'], environ['REQUEST_URI']),
            server=(environ['SERVER_NAME'], environ['SERVER_PORT']),
            remote_addr=(environ['REMOTE_ADDR'], environ['REMOTE_PORT']),
            headers=self.make_headers(),
            body=wsgi_input,
            is_json=self.request_type == 'json',
            is_xml=self.request_type == 'xml',
            is_form=self.request_type == 'multipart' or self.request_type == 'form',
            is_buffer=self.request_type is None
        )
        return request
