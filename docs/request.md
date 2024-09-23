# Обработка HTTP запросов


**WSGI** (Web Server Gateway Interface) - это протокол, который определяет интерфейс взаимодействия между веб-сервером 
и веб-приложением, написанным на языке Python.

WSGI позволяет разработчикам создавать веб-приложения, которые могут работать с различными веб-серверами, 
поддерживающими данный протокол. Он обеспечивает единый способ обработки HTTP-запросов и формирования HTTP-ответов, 
независимо от выбранного сервера.

Принцип работы WSGI заключается в следующем:

- Веб-сервер получает HTTP-запрос от клиента.
- Сервер вызывает функцию, которая является точкой входа для обработки запроса.
- Функция принимает два аргумента: объект запроса (request/environ) и объект ответа (response/start_response).
- Функция обрабатывает запрос, выполняет необходимые действия и формирует HTTP-ответ передавая его функции 
`start_response(status, headers)`. Тело ответа передается отдельно в бинарном виде.
- Ответ передается обратно веб-серверу, который передает его клиенту.

WSGI является стандартом для взаимодействия между веб-серверами и веб-приложениями на языке Python. Он облегчает 
разработку и развертывание веб-приложений, позволяя использовать различные серверы без изменения кода приложения.


Ниже представлено представления работы wsgi сервера

### JSON
```python
# Request
string = b'{"j": 1}'
environ = {
    'REQUEST_METHOD': 'POST',
    'REQUEST_URI': '/api/v1/test_request/1',
    'PATH_INFO': '/api/v1/test_request/1',
    'CONTENT_TYPE': 'application/json',
    'wsgi.input': io.BytesIO(string),
    'CONTENT_LENGTH': len(string),
}

# Запуск обработчика запроса
muscular.context.strategy = WsgiStrategy
app = muscular(environ, start_response)

# Ответ
for pr in app:
    assert pr == b'{"dd": "1", "json": {"j": 1}, ' \
                 b'"forms": null, "files": null, ' \
                 b'"request": {"url": "http://localhost:8080/api/v1/test_request/1"}}'
```


### Multipart
```python
# Request
from requests_toolbelt.multipart.encoder import MultipartEncoder
mp_encoder = MultipartEncoder(
    fields={
        'foo': 'bar',
        'image': (
            '6152749397.jpg', open(os.path.join(os.path.dirname(__file__), '6152749397.jpg'), 'rb'), 'image/jpg'),
    }
)
environ = {
    'REQUEST_METHOD': 'POST',
    'REQUEST_URI': '/api/v1/test_request/1',
    'PATH_INFO': '/api/v1/test_request/1',
    'CONTENT_TYPE': mp_encoder.content_type,
    'wsgi.input': io.BytesIO(mp_encoder.to_string()),
    'CONTENT_LENGTH': int(1421),
}

# Запуск обработчика запроса
muscular = Muscular()
muscular.context.strategy = WsgiStrategy
app = muscular(environ, start_response)

# Ответ
for pr in app:
    assert pr == b'{"dd": "1", "json": {}, "forms": {"foo": "bar"}, ' \
                 b'"files": {"image": "FileStorage(\'image/jpeg\', \'6152749397.jpg\')"}, ' \
                 b'"request": {"url": "http://localhost:8080/api/v1/test_request/1"}}'
```


### Form
```python
# Request
string = b'dd=1&d2=2&d2=3'
environ = {
        'REQUEST_METHOD': 'POST',
        'REQUEST_URI': '/api/v1/test_request/1',
        'PATH_INFO': '/api/v1/test_request/1',
        'CONTENT_TYPE': 'application/x-www-form-urlencoded',
        'wsgi.input': io.BytesIO(string),
        'CONTENT_LENGTH': int(14),
    }

# Запуск обработчика запроса
muscular = Muscular()
muscular.context.strategy = WsgiStrategy
app = muscular(environ, start_response)

# Ответ
for pr in app:
    assert pr == b'{"dd": "1", "json": {}, "forms": {"dd": "1", "d2": ["2", "3"]}, "files": {}, ' \
                     b'"request": {"url": "http://localhost:8080/api/v1/test_request/1"}}'
```


### Form
```python
# Request
file = os.path.join(os.path.dirname(__file__), '6152749397.jpg')
fp = open(file, 'rb')
environ = {
    'REQUEST_METHOD': 'POST',
    'REQUEST_URI': '/api/v1/test_request/1/raw',
    'PATH_INFO': '/api/v1/test_request/1/raw',
    'CONTENT_TYPE': 'image/jpeg',
    'wsgi.input': fp,
    'CONTENT_LENGTH': os.stat(file).st_size,
}

# Запуск обработчика запроса
muscular = Muscular()
muscular.context.strategy = WsgiStrategy
app = muscular(environ, start_response)

# Ответ
for pr in app:
    assert pr == b'{"dd": "1", "raw": "FileStorage(\'image/jpeg\', None)", "forms": null, ' \
                 b'"files": null, "request": {"url": "http://localhost:8080/api/v1/test_request/1/raw"}}'
```



