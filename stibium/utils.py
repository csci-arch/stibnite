from functools import wraps

class wrappers:
    @staticmethod
    def traverse_file_structure(file_structure):
        def decorator(function):
            @wraps(function)
            def traverse(current):
                if len(current.folders)>0:
                    for folder in current.folders.keys():
                        traverse(current.get_element(folder))
                if len(current.files)>0:
                    for file in current.files.keys():
                        current[file] = function(current[file])

                return current

            return traverse

        return decorator
