import os
import shutil
import pytest
import platform
from subprocess import call


def test_read_file_structure():
    from stibnite import constants, utils
    from stibnite.core_types import FunctionType, ClassType
    from stibnite.file_operations import FileOperations, FolderType, FileType
    stibnite_path = utils.get_project_path()
    separator = constants.SEPARATOR_DICT[platform.system()]
    try:
        import pathlib
        print(pathlib.Path(__file__))
        with open(f"{stibnite_path}example{separator}.stibnite-ignore", "w") as f:
            f.write("__init__.py\n__pycache__/")
        os.mkdir(f"{stibnite_path}tests{separator}test-doc")
        file_operations = FileOperations(f"{stibnite_path}example",
                                         f"{stibnite_path}tests{separator}test-doc",
                                         "test_doc",
                                         platform.system())

        file_structure = file_operations.read_file_structure()
        assert isinstance(file_structure, FolderType)
        assert len(file_structure.files) == 0 and len(file_structure.folders) == 1
        assert len(file_structure.folders["src"].files) == 3 and len(file_structure.folders["src"].folders) == 1
        assert sorted(list(file_structure.folders["src"].files.keys())) == sorted(["class_and_function.py",
                                                                                   "fullsupport_docstring.py",
                                                                                   "functions.py"])
        cls_and_func = file_structure.folders["src"].files["class_and_function.py"]
        assert isinstance(cls_and_func.classes[0], ClassType) and len(cls_and_func.classes) == 1
        assert isinstance(cls_and_func.functions[0], FunctionType) and len(cls_and_func.functions) == 2
        assert cls_and_func.classes[0].name == "Shark" and cls_and_func.classes[0].functions[0].name == "be_awesome"
        assert cls_and_func.functions[0].name == "maxi"
    finally:
        os.remove(f"{stibnite_path}example{separator}.stibnite-ignore")
        shutil.rmtree(f"{stibnite_path}tests{separator}test-doc")


def test_write_file_structure():
    from stibnite import constants, utils
    from stibnite.file_operations import FileOperations
    from stibnite.docstring_styler import DocstringStyler
    stibnite_path = utils.get_project_path()
    separator = constants.SEPARATOR_DICT[platform.system()]
    try:
        with open(f"{stibnite_path}example{separator}.stibnite-ignore", "w") as f:
            f.write("__init__.py\n__pycache__/")
        os.mkdir(f"{stibnite_path}tests{separator}test-doc")
        file_operations = FileOperations(f"{stibnite_path}example",
                                         f"{stibnite_path}tests{separator}test-doc",
                                         "test_doc",
                                         platform.system())

        file_structure = file_operations.read_file_structure()

        styled_file_structure = DocstringStyler(constants.MARKDOWN,
                                                constants.RESTRUCTERED).get_styled_structure(file_structure)

        file_operations.write_file_structure(styled_file_structure)
        assert os.path.exists(f"{stibnite_path}tests{separator}test-doc")
        assert os.path.exists(f"{stibnite_path}tests{separator}test-doc{separator}mkdocs.yml")
        assert os.path.exists(f"{stibnite_path}tests{separator}test-doc{separator}docs{separator}index.md")

        os.chdir(f"{stibnite_path}tests{separator}test-doc")
        call(["mkdocs", "build", "--clean"])

    finally:
        os.remove(f"{stibnite_path}example{separator}.stibnite-ignore")
        os.chdir(f"{stibnite_path}tests")
        shutil.rmtree(f"{stibnite_path}tests{separator}test-doc")


if __name__ == '__main__':
    pytest.main()
