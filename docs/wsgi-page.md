# Страницы

Для работы со схемой роутеров нужно вызвать точку входа в схему роутеров. Для этого используется 
`from muscles.wsgi import routes`.

```python
from muscles.wsgi import routes
from muscles.wsgi import RestApi
from muscles import Context
from muscles.wsgi import WsgiStrategy

muscular = Muscular()
muscular.context = Context(WsgiStrategy)

api1 = RestApi(name="ApiV1")
api2 = RestApi(name="ApiV2")


@routes.init('/')
def http_main(request):
    ''' index.html '''
    return 'INDEX'


@routes.error_handler()
def http_error(error):
    ''' Страница вывода ошибок, сюда попадут все ошибки, которые небыли перехвачены ранее '''
    return muscular.template('template/error.jinja2', error=error)


@routes.error_handler(code=500)
def http_error_500(error):
    ''' Страница вывода ошибок с кодом 500 '''
    return muscular.template('template/error_500.jinja2', error=error)


@routes.init('/privacy/{app_name}')
def http_privacy(request, app_name=None):
    ''' Страниы  /privacy/app1 и /privacy/app2 и другие, которые начинаются с /privacy/* '''
    return muscular.template('template/privacy.jinja2', app_name=app_name, ContactMail='info@twonerds.xyz')

@api1.init('/example_api1')
def http_example(request):
    ''' API версии 1'''
    return {
        'success': True,
        'request': id(request),
        'actor': request.actor.__dict__
    }

@api2.init('/example_api2')
def http_example(request):
    ''' API версии 2'''
    return {
        'success': True
    }
```