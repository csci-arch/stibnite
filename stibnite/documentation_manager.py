from stibnite import file_operations, docstring_styler
import os


class DocumentationManager:
    """This class handles with general documentation operations like reading,styling and writing.

    :param source_path: The path of the folder that contains source code
    :type source_path: string
    :param output_path: The path of the folder that is going to contain outputs
    :type output_path: string
    :param output_style: Name of the style that the documentation will be written in
    :type output_style: string
    :param input_style: Name of the style that the documentation is written in
    :type input_style: string
    """
    def __init__(self, source_path, output_path, output_style, input_style):
        self.package_name = os.path.abspath(source_path).split(os.sep)[-1]
        self.package_path = os.path.abspath(source_path)
        self.documentation_name = os.path.abspath(output_path).split(os.sep)[-1]
        self.documentation_path = os.path.abspath(output_path)
        self.input_style = input_style
        self.output_style = output_style
        self.file_operator = file_operations.FileOperations(self.package_path,
                                                            self.documentation_path,
                                                            self.documentation_name)
        self.file_structure = self.get_styled_structure(self.get_file_structure())

    def get_file_structure(self):
        """Reads the source code and returns a file structure which is like a file tree that contains all the
        information about the source code.

        :return: The root of the file structure
        :rtype: stibnite.file_operations.FolderType
        """
        return self.file_operator.read_file_structure()

    def get_styled_structure(self, file_structure):
        """Stylizes and creates the documentation of the source code.

        :param file_structure: The root of a file structure
        :type file_structure: stibnite.file_operations.FolderType
        :return: The same root but each documentation field in stibnite.file_operations.FileType under the
        file structure of the root is filled with stylized documentation text
        :rtype: stibnite.file_operations.FolderType
        """
        return docstring_styler.DocstringStyler(self.output_style,
                                                self.input_style).get_styled_structure(file_structure)

    def write_file_structure(self):
        """Writes the documentation and other necessary files for mkdocs.

        """
        self.file_operator.write_file_structure(self.file_structure)
