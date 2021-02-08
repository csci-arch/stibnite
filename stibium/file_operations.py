import os
import sys
import inspect
import importlib.util as module_loader
import constants, core_types


class FileType:
    def __init__(self, name, classes, functions):
        self.name = name
        self.classes = classes
        self.functions = functions
        self.folders = None


class FolderType:
    def __init__(self, name):
        self.name = name
        self.folders = {}
        self.files = {}

    def get_element(self, name):
        if name in self.folders:
            return self.folders[name]
        elif name in self.files:
            return self.files[name]
        else:
            return None

    def add_folder(self, folder):
        self.folders[folder.name] = folder

    def add_file(self, file):
        self.files[file.name] = file


def import_module(module_name, module_path):
    spec = module_loader.spec_from_file_location(module_name, module_path)
    module = module_loader.module_from_spec(spec)
    sys.modules[module_name] = module
    spec.loader.exec_module(module)
    return module


class FileOperations:
    @staticmethod
    def read_file_structure(package_path, os_name):
        separator = constants.separator_dict[os_name]
        return build_file_tree(package_path, separator)

    @staticmethod
    def write_file_structure(self, file_structure):
        pass


def build_file_tree(path, separator, ignored_prefix='__'):
    for path, dirs, files in os.walk(path):
        current_node = FolderType(path.split(separator)[-1])
        for directory in dirs:
            current_node.add_folder(build_file_tree(os.path.join(path, directory), separator, ignored_prefix))

        for file in files:
            if file[:2] != ignored_prefix and file.split('.')[-1] == "py":
                module = import_module(file.split('.')[0], os.path.join(path, file))

                classes = [
                    core_types.ClassType(obj)
                    for name, obj in inspect.getmembers(module, inspect.isclass)
                ]
                functions = [
                    core_types.FunctionType(obj)
                    for name, obj in inspect.getmembers(module, inspect.isfunction)
                ]

                current_node.add_file(FileType(file,
                                               functions=functions,
                                               classes=classes))
        return current_node
