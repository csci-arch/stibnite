class ClassType:
    """This is a class with a sole purpose of storing information about the classes in a python file

    :param obj: A python live object of a class that is going to be documented
    :type obj: object
    """
    def __init__(self, obj):
        import inspect
        self.name = obj.__name__
        self.obj = obj
        self.module = obj.__module__
        self.path = inspect.getmodule(obj).__file__
        self.doc = obj.__doc__ or ""
        try:
            self.source = inspect.getsource(obj) if obj.__doc__ is None \
                else inspect.getsource(obj).replace(obj.__doc__, '').replace('"""', '')
        except:
            self.source = ""
        try:
            self.args = str(inspect.signature(obj))
        except:
            self.args = ""
        self.functions = [FunctionType(obj) for name, obj in inspect.getmembers(obj, inspect.isfunction)]
        self.methods = [FunctionType(obj) for name, obj in inspect.getmembers(obj, inspect.ismethod)]


class FunctionType:
    """This is a class with a sole purpose of storing information about the functions or methods in a python file or in a python class

    :param obj: A python live object of a function or a method that is going to be documented
    :type obj: object
    """
    def __init__(self, obj):
        import inspect
        self.name = obj.__name__
        self.name_in_list = obj.__name__
        self.obj = obj
        self.module = obj.__module__
        self.path = inspect.getmodule(obj).__file__
        self.doc = obj.__doc__ or ""
        self.source = inspect.getsource(obj) if obj.__doc__ is None \
            else inspect.getsource(obj).replace(obj.__doc__, '').replace('"""', '')
        self.args = str(inspect.signature(obj))
