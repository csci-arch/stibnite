
class DocstringStyler:
    def __init__(self, style="x"):
        self.style = style

    def get_styled_structure(self, file_structure):
        return eval("style")(file_structure)
