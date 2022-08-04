# The code below is "proudly stolen" from here: 
#   https://stackoverflow.com/questions/5189699/how-to-make-a-class-property 
# Current solution looks good as at the time of this writing the situation 
#   with double decorators (@classmethod + @property) is not obvious.
#   More on these decorators is here: 
#     https://stackoverflow.com/questions/128573/using-property-on-classmethods/64738850#64738850

class ClassPropertyDescriptor(object):

    def __init__(self, fget, fset=None):
        self.fget = fget
        self.fset = fset

    def __get__(self, obj, klass=None):
        if klass is None:
            klass = type(obj)
        return self.fget.__get__(obj, klass)()

    def __set__(self, obj, value):
        if not self.fset:
            raise AttributeError("can't set attribute")
        type_ = type(obj)
        return self.fset.__get__(obj, type_)(value)

    def setter(self, func):
        if not isinstance(func, (classmethod, staticmethod)):
            func = classmethod(func)
        self.fset = func
        return self

def classproperty(func):
    if not isinstance(func, (classmethod, staticmethod)):
        func = classmethod(func)

    return ClassPropertyDescriptor(func)
