from stibnite import constants, core_types
import importlib.util as module_loader
from functools import lru_cache
import inspect
import json
import sys
import os


class FileType:
    """This is a class that represents a python file or a leaf in a tree and contains classes and functions of the same python file.

    :param name: Name of the file
    :type name: string
    :param classes: Classes in the file
    :type classes: list of stibnite.core_types.ClassType
    :param functions: Functions in the file
    :type ofunctionsbj: list of stibnite.core_types.FunctionType
    """
    def __init__(self, name, classes, functions):
        self.name = name
        self.classes = classes
        self.functions = functions
        self.folders = None


class FolderType:
    """This is a class that represents a folder or a node in a tree and contains other files or folder in it.

    :param name: Name of the file
    :type name: string
    """
    def __init__(self, name):
        self.name = name
        self.folders = {}
        self.files = {}

    def get_element(self, name):
        """Returns the file/folder with the given name if this folder contains it.

        :param name: Name of the file/folder
        :type name: string
        :return: The file/folder with the given name
        :rtype: stibnite.file_operations.FileType or stibnite.file_operations.FolderType or None
        """
        if name in self.folders:
            return self.folders[name]
        elif name in self.files:
            return self.files[name]
        else:
            return None

    def add_folder(self, folder):
        """Appends the given folder to its folder list.

        :param folder: Folder that is going to be added
        :type folder: stibnite.file_operations.FolderType
        """
        self.folders[folder.name] = folder

    def add_file(self, file):
        """Appends the given file to its file list.

        :param file: File that is going to be added
        :type file: stibnite.file_operations.FileType
        """
        self.files[file.name] = file


def import_module(module_name, module_path):
    """Import the given module and returns an object of it.

    :param module_name: Name of the module that is going to be imported
    :type module_name: string
    :param module_path: Path of the module that is going to be imported
    :type module_path: string
    :return: A live object of the imported module
    :rtype: object
    """
    spec = module_loader.spec_from_file_location(module_name, module_path)
    module = module_loader.module_from_spec(spec)
    sys.modules[module_name] = module
    spec.loader.exec_module(module)
    return module


@lru_cache(maxsize=1)
def get_json_file(documentation_path):
    """Reads json file and returns it. This method works only ones and returns from cache for the other calls

    :param documentation_path: path of the documentation
    :type documentation_path: string
    :return: json file content
    :rtype: string
    """
    with open(f"{documentation_path}ignored_prefixes_and_names.json", "r", encoding="utf-8") as json_file:
        return json_file.read()


def is_ignored(name, documentation_path):
    """Checks if the given name has a ignored prefix or name.

    :param name: file or folder name
    :type name: string
    :param documentation_path: path of the documentation
    :type documentation_path: string
    :return: has a ignored prefix, name or not
    :rtype: bool
    """
    ignored_dict = json.loads(get_json_file(documentation_path))
    for prefix in ignored_dict["prefixes"]:
        if name[:len(prefix)] == prefix:
            return True
    if name in ignored_dict['names']:
        return True
    return False


class FileOperations:
    """Main class for File Operations

    :param package_path: path of the source package
    :type package_path: string
    :param documentation_path: path of the documentation will be create
    :type documentation_path: string
    :param documentation_name: name of the documentation will be create
    :type documentation_name: string
    :param os_name: name of the os that user is using
    :type os_name: string
    """
    def __init__(self, package_path, documentation_path, documentation_name, os_name):
        self.package_path = package_path
        self.documentation_path = documentation_path
        self.documentation_name = documentation_name
        self.os_name = os_name
        self.separator = constants.SEPARATOR_DICT[self.os_name]

    def read_file_structure(self):
        """Reads the whole package and its subpackages and returns a file structure.

        :return: a file structure of the source package
        :rtype: stibnite.file_operations.FolderType
        """
        sys.path.insert(0,  self.package_path)
        self.__create_template_ignore_file()
        return build_file_tree(self.package_path, self.documentation_path, self.separator)

    def write_file_structure(self, file_structure):
        """Writes the documentation of the whole file structure and some other necessary files to run mkdocs such as index page and yaml file.

        :param file_structure: the root of the file structure that is going to be written
        :type file_structure: stibnite.file_operations.FolderType
        """
        self.documentation_path = os.path.join(os.path.abspath(self.documentation_path), "docs")
        if not os.path.exists(self.documentation_path):
            os.mkdir(self.documentation_path)

        current_path = f"{self.documentation_path}{self.separator}{file_structure.name}"
        if not os.path.exists(current_path):
            os.mkdir(current_path)

        toc = write_file_tree(file_structure, current_path, self.documentation_path, self.separator, "", 1)

        yml_path = os.path.join(self.separator.join(self.documentation_path.split(self.separator)[:-1]), 'mkdocs.yml')
        if not os.path.isfile(yml_path):
            create_yaml_file(self.documentation_name, yml_path, toc)

        index_path = os.path.join(self.documentation_path, 'index.md')
        if not os.path.isfile(index_path):
            create_index_file(self.documentation_name, index_path, f"{self.package_path}{self.separator}")

    def __create_template_ignore_file(self):
        with open(f"{self.documentation_path}{self.separator}ignored_prefixes_and_names.json", "w", encoding="utf-8") as json_file:
            json_file.write(json.dumps(constants.IGNORE_JSON_TEMPLATE))


def build_file_tree(package_path, documentation_path, separator):
    """Recursively reads and builds the file structure.

    :param package_path: the source path that is going to be read
    :type package_path: string
    :param documentation_path: the path of the folder that is going to contain outputs
    :type package_path: string
    :param separator: seperator of the file system of the os
    :type separator: string
    :return: the root of a file tree
    :rtype: stibnite.file_operations.FolderType
    """
    for path, dirs, files in os.walk(package_path):
        if len(dirs) == 0 and len(files) == 0:
            return None
        current_node = FolderType(path.split(separator)[-1])
        for directory in dirs:
            if not is_ignored(directory, f"{documentation_path}{separator}"):
                node_candidate = build_file_tree(os.path.join(path, directory), documentation_path, separator)
                if node_candidate is not None:
                    current_node.add_folder(node_candidate)

        for file in files:
            if not is_ignored(file, f"{documentation_path}{separator}") and file.split('.')[-1] == "py":
                module = import_module(file.split('.')[0], os.path.join(path, file))

                classes = [
                    core_types.ClassType(obj)
                    for name, obj in inspect.getmembers(module, inspect.isclass)
                    if obj.__module__ == module.__name__
                ]
                functions = [
                    core_types.FunctionType(obj)
                    for name, obj in inspect.getmembers(module, inspect.isfunction)
                    if obj.__module__ == module.__name__
                ]

                current_node.add_file(FileType(file,
                                               functions=functions,
                                               classes=classes))
        return current_node


def write_file_tree(element, current_path, output_path, separator, toc, depth):
    """Recursively writes the documentation and creates the yaml file.

    :param element: the current folder in the file tree
    :type element: stibnite.file_operations.FolderType
    :param current_path: path of the current folder in the file tree
    :type current_path: string
    :param output_path: the path of the folder that is going to contain outputs
    :type output_path: string
    :param separator: seperator of the file system of the os
    :type separator: string
    :param toc: contents of the yaml file
    :type toc: string
    :param depth: the depth of the recursive function currently in
    :type depth: int
    :return: contents of the yaml file
    :rtype: string
    """
    toc += "    " * depth + "- " + element.name + ":\n"
    if len(element.folders) > 0:
        for name, folder in element.folders.items():
            new_path = f'{current_path}{separator}{name}'
            if not os.path.exists(new_path):
                os.mkdir(new_path)
            toc = write_file_tree(folder, new_path, output_path, separator, toc, depth+1)
    if len(element.files) > 0:
        for name, file in element.files.items():
            if file.documentation[constants.CONTENT] != "":
                file_p = open(f"{current_path}{separator}{name.split('.')[0]}.{file.documentation[constants.FORMAT]}", "w",
                              encoding="utf-8")
                file_p.write(file.documentation[constants.CONTENT])
                file_p.close()

                toc += "    " * (depth + 1) + "- " + f"{'/'.join(current_path[len(output_path)+1:].split(separator))}" \
                                                     f"/{name.split('.')[0]}.{file.documentation[constants.FORMAT]}\n"
    return toc


def create_yaml_file(project_name, yaml_file_path, toc):
    """Creates and writes the yaml file.

    :param project_name: name of the project
    :type project_name: string
    :param yaml_file_path: the path of the yaml file that is going to be written at
    :type yaml_file_path: string
    :param toc: contents of the yaml file
    :type toc: string
    """
    yaml_file = open(yaml_file_path, "w", encoding="utf-8")
    content = f"""site_name: {project_name}
theme:
  name: 'material'
  palette:
    primary: indigo
  features:
    - navigation.tabs
  icon:
    repo: fontawesome/brands/git-alt
repo_name: csci-arch/stibnite
repo_url: https://github.com/csci-arch/stibnite
nav:
    - Home: index.md
{toc}
markdown_extensions:
    - toc:
        toc_depth: 3
        permalink: True
    - extra
    - smarty
    - codehilite
    - admonition
    - pymdownx.details
    - pymdownx.superfences
    - pymdownx.emoji
    - pymdownx.inlinehilite
    - pymdownx.magiclink
    """
    yaml_file.writelines(content)
    yaml_file.close()


def create_index_file(project_name, index_file_path, package_path):
    """Creates and writes the index file.

    :param project_name: Name of the project
    :type project_name: string
    :param index_file_path: The path of the index file that is going to be written at
    :type index_file_path: string
    :param package_path: path of the source package
    :type package_path: string
    """
    index_file = open(index_file_path, "w", encoding="utf-8")
    try:
        with open(f"{package_path}README.md", "r", encoding="utf-8") as fh:
            long_description = fh.read()
    except:
        long_description = ""
    content = f"""# Welcome to {project_name}
{long_description}"""
    index_file.writelines(content)
    index_file.close()
