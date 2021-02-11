from stibium import file_operations, docstring_styler, constants
import os


class DocumentationManager:
    """
        This class includes main documentation operations
    """
    def __init__(self, source_path, output_path, os_name, style=constants.MARKDOWN, standard=constants.RESTRUCTERED):
        self.package_name = source_path.split(constants.separator_dict[os_name])[-1]
        self.package_path = os.path.abspath(source_path)
        self.documentation_name = output_path.split(constants.separator_dict[os_name])[-1]
        self.documentation_path = os.path.join(os.path.abspath(output_path), "docs")
        self.os_name = os_name
        self.style = style
        self.std = standard
        self.file_operator = file_operations.FileOperations()
        self.file_structure = self.get_styled_structure(self.get_file_structure())

    def get_file_structure(self):
        return self.file_operator.read_file_structure(self.package_path, self.os_name)

    def get_styled_structure(self, file_structure):
        return docstring_styler.DocstringStyler(self.style, self.std).get_styled_structure(file_structure)

    def write_file_structure(self):
        self.file_operator.write_file_structure(self.file_structure, self.documentation_path, self.documentation_name, self.os_name)
