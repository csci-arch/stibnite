class ClassType:
    def __init__(self, obj):
        import inspect
        self.name = obj.__name__
        self.obj = obj
        self.module = obj.__module__
        self.path = inspect.getmodule(obj).__file__
        self.doc = obj.__doc__ or ""
        self.source = inspect.getsource(obj) if obj.__doc__ is None \
            else inspect.getsource(obj).replace(obj.__doc__, '').replace('"""', '')
        try:
            self.args = inspect.signature(obj)
        except:
            self.args = ""
        self.functions = [FunctionType(obj) for name, obj in inspect.getmembers(obj, inspect.isfunction)]
        self.methods = [FunctionType(obj) for name, obj in inspect.getmembers(obj, inspect.ismethod)]


class FunctionType:
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
        self.args = inspect.signature(obj)
