import glob
import os
from stibium import constants


class FileType:
    def __init__(self, name):
        self.name = name
        self.classes = []
        self.functions = []
        self.folders = None


class FolderType:
    def __init__(self, name, parent=None):
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


class FileOperations:
    @staticmethod
    def read_file_structure(package_path, os_name):
        separator = constants.separator_dict[os_name]
        ignored_prefix = "__"
        root_path = os.path.dirname(package_path)
        root = FolderType('root')
        f_list_glob = glob.glob(f'{package_path}{separator}**', recursive=True)
        list_glob = [path for path in f_list_glob if f'{separator}{ignored_prefix}' not in path and os.path.isfile(path) and path[-3:] == ".py"]

        for element in list_glob:
            current_node = root
            path_parts = element[len(package_path) + 1:].split(separator)
            for idx in range(len(path_parts)-1):
                if current_node.get_element(path_parts[idx]) is not None:
                    current_node = current_node.get_element(path_parts[idx])
                else:
                    current_node.add_folder(FolderType(path_parts[idx]))
                    current_node = current_node.get_element(path_parts[idx])
            current_node.add_file(FileType(path_parts[-1]))

        return root

    @staticmethod
    def write_file_structure(self, file_structure):
        pass