from stibnite import DocumentationManager, constants
from subprocess import call
import webbrowser
import sys
import os


def main(argv=None):
    argv = sys.argv if argv is None else argv

    print(argv)

    DocumentationManager(argv[1], argv[2],
                         input_style=constants.RESTRUCTERED,
                         output_style=constants.MARKDOWN).write_file_structure()

    os.chdir(argv[2])

    call(["mkdocs", "build", "--clean"])

    call(["mkdocs", "serve"])

    webbrowser.open("http://127.0.0.1:8000/")


if __name__ == "__main__":
    main(sys.argv)
