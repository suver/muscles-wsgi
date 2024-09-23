# README: Muscular Framework #

```bash

pybabel extract --mapping-file=/apps/app/babelrc --keywords=_ --keywords=_l --keywords=t --keywords=locale --output-file=/apps/gitmodules/muscles/locales/message.pot /apps/gitmodules/muscles/src

pybabel init --domain=message --input-file=/apps/gitmodules/muscles/locales/message.pot --output-dir=/apps/gitmodules/muscles/locales --locale=en

pybabel update --domain=message --input-file=/apps/gitmodules/muscles/locales/message.pot --output-dir=/apps/gitmodules/muscles/locales --locale=en

pybabel compile --domain=message --directory=/apps/gitmodules/muscles/locales

```

### Plans ###

#### Completed ####
- cli
- http with wsgi
- http with server
- request
- response
- redirect
- header
- test for wsgi
- test for http
- test for cli
- test for redirect
- html template


#### Must ####

- route with param and alias (main.index)
- test for abort
- configuration
- auto restart
- documentation


### Routers ###

```python
from muscles.http import routes, Response

def http_main(request):
    body = '<html><head></head><body>'
    body += f'#HalloMuscularWorld'
    body += '</body></html>'
    return body


@routes.init('/init', method='GET', content_type='text/html')
def main_test1(request):
    body = '<html><head></head><body>'
    body += f'#init GET'
    body += '</body></html>'
    return body


@routes.init('/init', method='PUT', content_type='application/json')
def main_test1(request):
    return [{"init": "PUT"}]


@routes.init('/init', method='LINK', redirect='http://localhost:8080/test')
def main_test1(request):
    return [{"init": "PUT"}]


@routes.init('/init', method='DELETE', redirect=(308, '/test'))
def main_test1(request):
    return [{"init": "PUT"}]


@routes.init('/init', method='GET', content_type='application/json')
def main_test1(request):
    return {"init": "GET"}


@routes.init('/init', method='POST')
def main_test1(request):
    body = '<html><head></head><body>'
    body += f'#init POST'
    body += '</body></html>'
    return body


def http_main(request):
    body = '<html><head></head><body>'
    body += f'#HalloMuscularWorld'
    body += '</body></html>'
    # await asyncio.sleep(5)
    # time.sleep(5)
    return body


def http_main1(request):
    body = '<html><head></head><body>'
    body += f'#HalloMuscularWorld 111'
    body += '</body></html>'
    return Response(200, body=body)


def http_main2(request):
    body = '<html><head></head><body>'
    body += f'#HalloMuscularWorld 111'
    body += '</body></html>'
    headers = [('Star', 1)]
    return (body, 200, headers)


def http_main3(request):
    body = '<html><head></head><body>'
    body += f'#HalloMuscularWorld 111'
    body += '</body></html>'
    headers = [('Star', 1)]
    return (body, 404, headers)


routes.add('/', http_main, method='GET')
routes.add('/test', http_main1, method='*')
routes.add('/test2', http_main2, method='*')
routes.add('/test3', http_main3, method='*')

```
### How do I get set up? ###

* Summary of set up
* Configuration
* Dependencies
* Database configuration
* How to run tests
* Deployment instructions

### Contribution guidelines ###

* Writing tests
* Code review
* Other guidelines

### Who do I talk to? ###

* Repo owner or admin
* Other community or team contact