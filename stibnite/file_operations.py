from stibnite import constants, core_types
import importlib.util as module_loader
import inspect
import sys
import os


class FileType:
    """This is a class that represents a python file or a leaf in a tree and contains classes and functions of the same
    python file.

    :param name: Name of the file
    :type name: string
    :param classes: Classes in the file
    :type classes: list of stibnite.core_types.ClassType
    :param functions: Functions in the file
    :type functions: list of stibnite.core_types.FunctionType
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


def is_ignored(name, ignored_file_checker):
    """Checks if the given path is ignored or not.

    :param name: file or folder name
    :type name: string
    :param ignored_file_checker: checker object for checking ignored paths
    :type ignored_file_checker: igittigitt.IgnoreParser
    :return: has a ignored prefix, name or not
    :rtype: bool
    """
    # if ignored_file_checker.match(name):
    #     print(f"{name} is ignored.")
    return ignored_file_checker.match(name)


class FileOperations:
    """Main class for File Operations

    :param package_path: path of the source package
    :type package_path: string
    :param documentation_path: path of the documentation will be create
    :type documentation_path: string
    :param documentation_name: name of the documentation will be create
    :type documentation_name: string
    """
    def __init__(self, package_path, documentation_path, documentation_name):
        self.package_path = package_path
        self.documentation_path = documentation_path
        self.documentation_name = documentation_name

    def read_file_structure(self):
        """Reads the whole package and its subpackages and returns a file structure.

        :return: a file structure of the source package
        :rtype: stibnite.file_operations.FolderType
        """
        # Reads stibnite-ignore file and creates ignored_file_checker object with given patterns
        import igittigitt
        ignored_file_checker = igittigitt.IgnoreParser()
        if os.path.exists(os.path.join(self.package_path, ".stibnite-ignore")):
            ignored_file_checker.parse_rule_files(base_dir=self.package_path, filename=".stibnite-ignore")
        # This rule helps to ignore hidden files
        ignored_file_checker.add_rule(base_path=self.package_path, pattern=".*")

        sys.path.insert(0,  self.package_path)

        return build_file_tree(self.package_path, self.documentation_path, ignored_file_checker)

    def write_file_structure(self, file_structure):
        """Writes the documentation of the whole file structure and some other necessary files to run mkdocs such as
        index page and yaml file.

        :param file_structure: the root of the file structure that is going to be written
        :type file_structure: stibnite.file_operations.FolderType
        """
        # Firstly, creates documentation path if not exists
        documentation_path_parent = self.documentation_path
        self.documentation_path = os.path.join(os.path.abspath(self.documentation_path), "docs")
        if not os.path.exists(self.documentation_path):
            os.mkdir(self.documentation_path)

        current_path = os.path.join(self.documentation_path, file_structure.name)
        if not os.path.exists(current_path):
            os.mkdir(current_path)

        # File writing section
        toc = write_file_tree(file_structure, current_path, self.documentation_path, "", 1)

        # Creates yml file which is config file for mkdocs
        yml_path = os.path.join(documentation_path_parent, "mkdocs.yml")
        if not os.path.isfile(yml_path):
            create_yaml_file(self.documentation_name, yml_path, toc)

        # Creates index file which is the main page of the documentation
        index_path = os.path.join(self.documentation_path, 'index.md')
        if not os.path.isfile(index_path):
            create_index_file(self.documentation_name, index_path, self.package_path)


def build_file_tree(package_path, documentation_path, ignored_file_checker):
    """Recursively reads and builds the file structure.

    :param package_path: the source path that is going to be read
    :type package_path: string
    :param documentation_path: the path of the folder that is going to contain outputs
    :type package_path: string
    :param ignored_file_checker: checker object for checking ignored paths
    :type ignored_file_checker: igittigitt.IgnoreParser
    :return: the root of a file tree
    :rtype: stibnite.file_operations.FolderType
    """
    # Traverses given package path recursively and creates Folder and File Tree structure with it
    for path, dirs, files in os.walk(package_path):
        current_node = FolderType(path.split(os.sep)[-1])
        for directory in dirs:
            # Checks the directory whether ignored directory or not in stibnite-ignore file
            if not is_ignored(os.path.join(path, directory, ""), ignored_file_checker):
                node_candidate = build_file_tree(os.path.join(path, directory),
                                                 documentation_path,
                                                 ignored_file_checker)
                if node_candidate is not None:
                    current_node.add_folder(node_candidate)

        for file in files:
            # Checks the file whether ignored directory or not in stibnite-ignore file
            if not is_ignored(os.path.join(path, file), ignored_file_checker) and file.split('.')[-1] == "py":
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

        if len(current_node.folders) == 0 and len(current_node.files) == 0:
            return None

        return current_node


def write_file_tree(element, current_path, output_path, toc, depth):
    """Recursively writes the documentation and creates the yaml file.

    :param element: the current folder in the file tree
    :type element: stibnite.file_operations.FolderType
    :param current_path: path of the current folder in the file tree
    :type current_path: string
    :param output_path: the path of the folder that is going to contain outputs
    :type output_path: string
    :param toc: contents of the yaml file
    :type toc: string
    :param depth: the depth of the recursive function currently in
    :type depth: int
    :return: contents of the yaml file
    :rtype: string
    """
    # Traverses our Tree structure and creates folders and files respect to it
    # Creates indented table of contents structure for using in yml file
    toc += "    " * depth + "- " + element.name + ":\n"
    if len(element.folders) > 0:
        for name, folder in element.folders.items():
            new_path = os.path.join(current_path, name)
            if not os.path.exists(new_path):
                os.mkdir(new_path)
            toc = write_file_tree(folder, new_path, output_path, toc, depth+1)
    if len(element.files) > 0:
        for name, file in element.files.items():
            if file.documentation[constants.CONTENT] != "":
                with open(os.path.join(current_path, f"{name.split('.')[0]}.{file.documentation[constants.FORMAT]}"),
                          "w",
                          encoding="utf-8") as f_p:
                    f_p.write(file.documentation[constants.CONTENT])

                toc += "    " * (depth + 1) + "- " + f"{'/'.join(current_path[len(output_path)+1:].split(os.sep))}" \
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
        with open(os.path.join(package_path, "README.md"), "r", encoding="utf-8") as fh:
            long_description = fh.read()
    except Exception as e:
        long_description = ""
    content = f"""# Welcome to {project_name}
{long_description}"""
    index_file.writelines(content)
    index_file.close()
