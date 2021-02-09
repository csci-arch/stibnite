import os
import sys
import inspect
import importlib.util as module_loader
import constants
import core_types


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
        sys.path.insert(0,  package_path)
        separator = constants.separator_dict[os_name]
        return build_file_tree(package_path, separator)

    @staticmethod
    def write_file_structure(file_structure, output_path, project_name, os_name):
        separator = constants.separator_dict[os_name]
        current_path = f"{output_path}{separator}{file_structure.name}"
        if not os.path.exists(output_path):
            os.mkdir(output_path)
            os.mkdir(current_path)
        toc = write_file_tree(file_structure, current_path, output_path, separator, "", 1)

        yml_path = os.path.join(separator.join(output_path.split(separator)[:-1]), 'mkdocs.yml')
        if not os.path.isfile(yml_path):
            create_yaml_file(project_name, yml_path, toc)

        index_path = os.path.join(output_path, 'index.md')
        if not os.path.isfile(index_path):
            create_index_file(project_name, index_path)


def build_file_tree(path, separator, ignored_prefix='__'):
    for path, dirs, files in os.walk(path):
        if len(dirs) == 0 and len(files) == 0:
            return None
        current_node = FolderType(path.split(separator)[-1])
        for directory in dirs:
            if directory[:2] != ignored_prefix:
                node_candidate = build_file_tree(os.path.join(path, directory), separator, ignored_prefix)
                if node_candidate is not None:
                    current_node.add_folder(node_candidate)

        for file in files:
            if file[:2] != ignored_prefix and file.split('.')[-1] == "py":
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
    toc += "    " * depth + "- " + element.name + ":\n"
    if len(element.folders) > 0:
        for name, folder in element.folders.items():
            new_path = f'{current_path}{separator}{name}'
            if not os.path.exists(new_path):
                os.mkdir(new_path)
            toc = write_file_tree(folder, new_path, output_path, separator, toc, depth+1)
    if len(element.files) > 0:
        for name, file in element.files.items():
            file_p = open(f"{current_path}{separator}{name.split('.')[0]}.{file.documentation[constants.FORMAT]}", "w",
                          encoding="utf-8")
            file_p.write(file.documentation[constants.CONTENT])
            file_p.close()

            toc += "    " * (depth + 1) + "- " + f"{'/'.join(current_path[len(output_path)+1:].split(separator))}" \
                                                 f"/{name.split('.')[0]}.{file.documentation[constants.FORMAT]}\n"
    return toc


def create_yaml_file(project_name, yaml_file_path, toc):
    yaml_file = open(yaml_file_path, "w", encoding="utf-8")
    content = """site_name: {}
theme:
  name: 'material'
nav:
    - Home: index.md
{}
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
    """.format(
        project_name, toc
    )
    yaml_file.writelines(content)
    yaml_file.close()


def create_index_file(project_name, index_file_path):
    index_file = open(index_file_path, "w", encoding="utf-8")
    content = """# Welcome to {0}
This website contains the documentation for the wonderful project {0}
""".format(project_name)
    index_file.writelines(content)
    index_file.close()
