from stibium import DocumentationManager
from subprocess import call
import webbrowser
import platform
import os

if __name__ == "__main__":
    source_path = r""
    output_path = r""

    DocumentationManager(source_path, output_path, platform.system()).write_file_structure()

    os.chdir(output_path)

    call(["mkdocs", "build", "--clean"])

    call(["mkdocs", "serve"])

    webbrowser.open("http://127.0.0.1:8000/")
