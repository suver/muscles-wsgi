# WSGI (Web Server Gateway Interface)


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


## Создание API

Предварительно вам требуется в основном объекте инициировать точку схемы API

#### Пример создания точки доступа к схеме API
```python

class Muscular(metaclass=ApplicationMeta):

    # Подключаем конфигурацию
    config = Configurator(obj={
        ...
        "api": {
            "prefix": "/api",
            "default_version": "v1",
            "controllers": {
                "Test": "controllers.test",
                "TestRequest": "controllers.request",
            }
        }
    })

    # Подключаем стратегию
    context = Context(WsgiStrategy, {})

    def __init__(self):
        # Наша точка подключения схемы API
        self.api = RestApi(
            prefix='/api/v1',
            version='1.0',
            name='ApiV1',
            title='Api v1',
            description='Системный Api',
            termsOfService='http://swagger.io/terms/',
            contact_email='**@**.info',
        )
```


Для начала работы с API вам нужно получить точку доступа к схеме API. Это можно сделать двумя способами:
- Через вызов `api = Muscular().api1` 
- Через вызов конструктора с именем API `api = RestApi(name='ApiV1')`

#### Пример получения точки доступа к схеме API
```python

class Muscular(metaclass=ApplicationMeta):

    config = Configurator(obj={
        ...
        "api": {
            "prefix": "/api",
            "default_version": "v1",
            "controllers": {
                "Test": "controllers.test",
                "TestRequest": "controllers.request",
            }
        }
    })

    context = Context(WsgiStrategy, {})

    def __init__(self):
        # Наша точка подключения схемы API
        self.api1 = RestApi(
            prefix='/api/v1',
            version='1.0',
            name='ApiV1',
            title='Api v1',
            description='Системный Api',
            termsOfService='http://swagger.io/terms/',
            contact_email='**@**.info',
        )


muscular = Muscular()
api = muscular.api1
# OR
api = RestApi(name='ApiV1')
```


### Создание контроллера

Для создания контроллера достаточно повесить на класс декоратор `@muscular.api1.controller`.

#### Пример такого декоратора. Подробнее варианты аргументов описаны в Схемах.
```python
@muscular.api1.controller('/test', description='Контроллер')
class Test:
    ...
```

Для определения endpoint апи используйте декоратор `@muscular.api1.action` на методе класса. 

#### Пример такого декоратора. Подробнее варианты аргументов описаны в Схемах.
```python
    ...

    @muscular.api1.action(route="/{id}",
                          method='post',
                          request=[
                              JsonRequestBody(description='Json', model=Column("name", String, index=True))
                          ])
    def create(self):
        ...

    ...
```



### Общий пример подключения API
```python
from muscles import JsonResponseBody
from muscles import XmlResponseBody
from muscles import MultipartRequestBody
from muscles import PathParameter
from muscles import CookieParameter
from muscles import HeaderParameter
from muscles import QueryParameter
from muscles import JsonRequestBody
from muscles.wsgi import WsgiStrategy
from muscles.wsgi import RestApi
from muscles import Context
from muscles import ApplicationMeta
from muscles import Configurator
from muscles import Column, Numeric, List, String, Enum


class Muscular(metaclass=ApplicationMeta):
    package_paths = []
    shutup = False

    config = Configurator(obj={
        "main": {
            "BASEDIR": ".",
            "BASE_URL": "localhost: 5050",
            "SERVER_NAME": "localhost: 5050",
            "HOST": "localhost",
            "PORT": "5050",
            "ENV": "production",
            "DEBUG": False,
            "TIMEZONE": "UTC",
            "MAIN_ROUTE": "page.index",
            "SQLALCHEMY_DATABASE_URI": "SQLALCHEMY_DATABASE_URI",
            "SQLALCHEMY_TRACK_MODIFICATIONS": True,
            "SQLALCHEMY_ON": True,
            "PROJECT_ROOT": ".",
            "STATICFILES_DIRS": "static",
            "SESSION_KEY_PREFIX": "session",
            "SESSION_TYPE": "filesystem",
            "SECRET_KEY": "dhU73jslvbglsjg&20lfjsl",
        },
        "routes": {
            "prefix": '',
        },
        "api": {
            "prefix": "/api",
            "default_version": "v1",
            "controllers": {
                "Test": "controllers.test",
                "TestRequest": "controllers.request",
            }
        }
    })

    context = Context(WsgiStrategy, {})

    def __init__(self):
        self.api1 = RestApi(
            prefix='/api/v1',
            version='1.0',
            name='ApiV1',
            title='Api v1',
            description='Системный Api',
            termsOfService='http://swagger.io/terms/',
            contact_email='**@**.info',
        )

        self.init_auto_packages(self.config)
        # self.init_imports(self.config.models)
        self.init_imports(self.config.api.controllers)

    @context.before_start()
    def before_start(self_context):
        # print('>>>>>>>>>>>>before_start')
        pass

    @context.after_start()
    def after_start(self_context, result):
        # print('>>>>>>>>>>>>after_start', result)
        pass

    def run(self, *args):
        return self.context.execute(*args, shutup=self.shutup)

    def __call__(self, environ, start_response):
        self.context.set_param('environ', environ)
        self.context.set_param('start_response', start_response)
        return self.context.execute()


muscular = Muscular()


@muscular.api1.controller('/test',
                          description='Контроллер работы со списком пользователей и пользователями',
                          summary='РО'
                          )
class Test:
    """
    Controller
    """

    @muscular.api1.action(method='option')
    def option(self, request):
        return {
            "method": request.method,
            "request": {
                "url": request.url,
            }
        }

    @muscular.api1.action(method='get',
                          description='1 Контроллер работы со списком пользователей и пользователями',
                          summary='Общее описание',
                          response={
                              200: [
                                  JsonResponseBody(description='OK', model=User),
                                  XmlResponseBody(description='OK'),
                              ],
                              400: JsonResponseBody(description='Error 400'),
                              404: JsonResponseBody(description='Not Found'),
                          })
    def get(self, request):
        return {
            "method": request.method,
            "request": {
                "url": request.url,
            }
        }

    @muscular.api1.action(method='post',
                          request=[
                              JsonRequestBody(description='Json', model=User),
                              MultipartRequestBody(description='Form', model=User),
                          ],
                          response={
                              200: JsonResponseBody(description='OK'),
                              400: JsonResponseBody(description='Error 400'),
                              404: JsonResponseBody(description='Not Found'),
                          })
    def post(self, request):
        return {
            "method": request.method,
            "request": {
                "url": request.url,
                "headers": request.headers,
                "query": request.query,
                "content_type": request.content_type,
                "cookies": request.cookies,
                "is_json": request.is_json,
                "forms": request.forms,
                "files": request.files,
                "body": request.body,
            }
        }

    @muscular.api1.action(method='delete',
                          request=[
                              JsonRequestBody(description='Json', model=User),
                              MultipartRequestBody(description='Form', model=User),
                          ],
                          response={
                              200: JsonResponseBody(description='OK'),
                              400: JsonResponseBody(description='Error 400'),
                              404: JsonResponseBody(description='Not Found'),
                          })
    def delete(self, request):
        return {
            "method": request.method,
        }

    @muscular.api1.action(method='put',
                          request=[
                              JsonRequestBody(description='Json', model=User),
                              MultipartRequestBody(description='Form', model=User),
                          ],
                          response={
                              200: JsonResponseBody(description='OK'),
                              400: JsonResponseBody(description='Error 400'),
                              404: JsonResponseBody(description='Not Found'),
                          })
    def put(self, request):
        return {
            "method": request.method,
        }

    @muscular.api1.action(route="/{id}",
                          method='get',
                          parameters=[
                              HeaderParameter('Header', Numeric, required=False, description='Header'),
                              CookieParameter('csrftoken', String, required=False, description='Cookie'),
                              PathParameter('id', Numeric, required=True, description='Path ID'),
                              QueryParameter('query1', List(Enum(enum=['one', 'two'])), required=False,
                                             description='Query1'),
                              QueryParameter('query2', Enum(enum=['one', 'two']), required=False, description='Query2'),
                          ],
                          request=[
                              JsonRequestBody(description='Json', model=User),
                              MultipartRequestBody(description='Form', model=User),
                          ],
                          response={
                              200: [
                                  JsonResponseBody(description='OK', model=User),
                                  XmlResponseBody(description='OK'),
                              ],
                              400: JsonResponseBody(description='Error 400'),
                              404: JsonResponseBody(description='Not Found'),
                          })
    def show(self, request, id):
        return {
            "id": id,
            "method": request.method,
            "request": {
                "url": request.url,
            }
        }

    @muscular.api1.action(route="/{id}",
                          method='post',
                          request=[
                              JsonRequestBody(description='Json', model=Column("name", String, index=True))
                          ])
    def change(self, request, id):
        return {
            "id": id,
            "method": request.method,
            "request": {
                "url": request.url,
            }
        }

    @muscular.api1.action(route="/{id}", method='delete')
    def drop(self, request, id):
        return {
            "id": id,
            "method": request.method,
            "request": {
                "url": request.url,
            }
        }



```



Поставить endpoint restfull можно и на функцию с помощью декоратора `@api_v1.init`

#### Пример определения точки endpoint вашего API через функцию
```python
api = RestApi(name='ApiV1')

@api.init('/example_api')
def http_example(request):
    return {
        'success': True,
        'request': id(request),
        'actor': request.actor.__dict__
    }
```



### Инъекция в формирование запроса и другие события Request

Для инъекции в формирование запроса существует декоратор `@Request.init_request()`. Определенные с его помощью 
обработчики будут запускаться в момент формирования объекта Request каждый раз. Это позволяет подвесить на него общие 
для всей программы функции, в которых можно определить важные сущности будущего запроса.

#### Пример @Request.init_request()
```python
from muscles.wsgi import Request
from muscles.wsgi import RestApi

api = RestApi(name='ApiV1')

@Request.init_request()
def init_request(request):
    print("======> INIT_REQUEST FOR ALL", request)
```


Другой способ подвесить похожие обработчики, которые будет запускаться каждый раз перед использованием объекта `Request` 
до вызова точки обработки запроса, это воспользоваться `@api.before_request()`. Эти обработчики запускаются для каждого 
экземпляра эндпойнтов свои. Таким образом для разных версий апи могут быть разные обработчики.

#### Пример @api.before_request() с DI
```python
from muscles.wsgi import Request
from muscles.wsgi import RestApi
from muscles import inject
from muscles import GuestUser

api = RestApi(name='ApiV1')

@api.before_request()
@inject(UserRepositoryInterface)
def actor_loader(request, repository: UserRepositoryInterface):
    request.actor = GuestUser()
    if 'X-Api-Token' not in request.headers:
        return
    token = request.headers['X-Api-Token']
    request.actor = repository.loadByToken(token)


```

**ИМХО:** И хоть в этом примере не определен UserRepositoryInterface, все же понятно как реализовывается авторизация в 
апи по токену