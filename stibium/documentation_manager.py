from stibium import file_operations, docstring_styler


class DocumentationManager:
    def __init__(self, config):
        self.file_structure = self.get_styled_structure(self.get_file_structure())
        self.config = config
        self.file_operator = file_operations.FileOperations("config")

    def get_file_structure(self):
        return self.file_operator.read_file_structure()

    def get_styled_structure(self, file_structure):
        return docstring_styler.DocstringStyler('style').get_styled_structure(file_structure)

    def write_file_structure(self):
        self.file_operator.write_file_structure(self.file_structure)
