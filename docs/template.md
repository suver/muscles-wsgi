# Шаблонизатор jinja2



```python
import os
from muscles.wsgi import routes
from muscles import Configurator
from muscles import Context
from muscles import ApplicationMeta
from muscles.wsgi import WsgiStrategy
from muscles.wsgi import Template
from muscles.wsgi import TemplateLoader

class Muscular(metaclass=ApplicationMeta):
    
    ...
    
    package_paths = ['modules']

    config_file = 'config/configuration.yaml'

    config = Configurator(file=config_file, basedir=os.getcwd())
    
    # Подключаем шаблонизатор JINJA
    template = Template(
        loader=TemplateLoader(config, package_paths=package_paths)
    )
    
    ...

muscular = Muscular()
muscular.context = Context(WsgiStrategy)

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
    return muscular.template('template/privacy.jinja2', app_name=app_name, ContactMail='my@mail.xyz')
```

Подробнее про JINJA можете почитать на соответсвующих ресурсах.