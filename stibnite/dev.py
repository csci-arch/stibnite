from stibnite.documentation_manager import DocumentationManager
from stibnite import constants
from subprocess import call
import webbrowser
import platform
import os

if __name__ == "__main__":
    source_path = r""
    output_path = r""

    # Be careful about input output style :)
    DocumentationManager(source_path, output_path, platform.system(),
                         input_style=constants.RESTRUCTERED,
                         output_style=constants.MARKDOWN).write_file_structure()

    os.chdir(output_path)

    call(["mkdocs", "build", "--clean"])

    call(["mkdocs", "serve"])

    webbrowser.open("http://127.0.0.1:8000/")
