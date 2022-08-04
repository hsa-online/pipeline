import typing

from core.defaults import Defaults
from core.cls_property import classproperty

class HelpStrings:
    @classproperty
    def addr_rest(cls) -> str:
        return f'Address for REST calls. For example {Defaults.ADDR_REST}'

    @classproperty
    def addr_service(cls) -> str:
        return f'Address for service calls in cluster. For example {Defaults.ADDR_SERVICE}'

    @classproperty
    def addr_worker(cls) -> str:
        return f'Address for computation calls in cluster. For example {Defaults.ADDR_WORKER}'

    @classproperty
    def help(cls) -> str:
        return 'Show this help message and exit.'
