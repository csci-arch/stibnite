from subprocess import call
import shutil
import pytest
import os


def test_read_file_structure():
    from stibnite import utils
    from stibnite.core_types import FunctionType, ClassType
    from stibnite.file_operations import FileOperations, FolderType
    stibnite_path = utils.get_project_path()
    try:
        with open(os.path.join(stibnite_path, "example", ".stibnite-ignore"), "w") as f:
            f.write("__init__.py\n__pycache__/\nsrc/subfolder2/subfolder3/\nbuild/")

        os.mkdir(os.path.join(stibnite_path, "tests", "test-doc"))

        file_operations = FileOperations(os.path.join(stibnite_path, "example"),
                                         os.path.join(stibnite_path, "tests", "test-doc"),
                                         "test_doc",)

        file_structure = file_operations.read_file_structure()
        assert isinstance(file_structure, FolderType) and file_structure.name == "example"
        assert len(file_structure.files) == 0 and len(file_structure.folders) == 1
        assert len(file_structure.folders["src"].files) == 4 and len(file_structure.folders["src"].folders) == 1
        assert sorted(list(file_structure.folders["src"].files.keys())) == sorted(["class_and_function.py",
                                                                                   "fullsupport_docstring.py",
                                                                                   "functions.py",
                                                                                   "xyz_build.py"])
        assert list(file_structure.folders["src"].folders.keys()) == ["subfolder"]
        cls_and_func = file_structure.folders["src"].files["class_and_function.py"]
        assert isinstance(cls_and_func.classes[0], ClassType) and len(cls_and_func.classes) == 1
        assert isinstance(cls_and_func.functions[0], FunctionType) and len(cls_and_func.functions) == 2
        assert cls_and_func.classes[0].name == "Shark" and cls_and_func.classes[0].functions[0].name == "be_awesome"
        assert cls_and_func.functions[0].name == "maxi"
    finally:
        os.remove(os.path.join(stibnite_path, "example", ".stibnite-ignore"))
        shutil.rmtree(os.path.join(stibnite_path, "tests", "test-doc"))


def test_write_file_structure():
    from stibnite import constants, utils
    from stibnite.file_operations import FileOperations
    from stibnite.docstring_styler import DocstringStyler
    stibnite_path = utils.get_project_path()
    try:
        with open(os.path.join(stibnite_path, "example", ".stibnite-ignore"), "w") as f:
            f.write("__init__.py\n__pycache__/\nsrc/subfolder2/subfolder3/\nbuild/")

        os.mkdir(os.path.join(stibnite_path, "tests", "test-doc"))

        file_operations = FileOperations(os.path.join(stibnite_path, "example"),
                                         os.path.join(stibnite_path, "tests", "test-doc"),
                                         "test_doc")

        file_structure = file_operations.read_file_structure()

        styled_file_structure = DocstringStyler(constants.MARKDOWN,
                                                constants.MARKDOWN).get_styled_structure(file_structure)

        file_operations.write_file_structure(styled_file_structure)

        assert os.path.exists(os.path.join(stibnite_path, "tests", "test-doc"))
        assert os.path.exists(os.path.join(stibnite_path, "tests", "test-doc", "docs"))
        assert os.path.exists(os.path.join(stibnite_path, "tests", "test-doc", "mkdocs.yml"))
        assert os.path.exists(os.path.join(stibnite_path, "tests", "test-doc", "docs", "example"))
        assert os.path.exists(os.path.join(stibnite_path, "tests", "test-doc", "docs", "index.md"))
        assert os.path.exists(os.path.join(stibnite_path, "tests", "test-doc", "docs", "example", "src"))
        assert os.path.exists(os.path.join(stibnite_path, "tests", "test-doc", "docs", "example", "src", "subfolder"))
        assert os.path.exists(os.path.join(stibnite_path, "tests", "test-doc", "docs", "example", "src",
                                           "xyz_build.md"))
        assert os.path.exists(os.path.join(stibnite_path, "tests", "test-doc", "docs", "example", "src",
                                           "class_and_function.md"))
        assert os.path.exists(os.path.join(stibnite_path, "tests", "test-doc", "docs", "example", "src",
                                           "fullsupport_docstring.md"))
        assert os.path.exists(os.path.join(stibnite_path, "tests", "test-doc", "docs", "example", "src",
                                           "functions.md"))
        assert os.path.exists(os.path.join(stibnite_path, "tests", "test-doc", "docs", "example", "src", "subfolder",
                                           "functions.md"))

        os.chdir(os.path.join(stibnite_path, "tests", "test-doc"))
        call(["mkdocs", "build", "--clean"])

    finally:
        os.remove(os.path.join(stibnite_path, "example", ".stibnite-ignore"))
        os.chdir(os.path.join(stibnite_path, "tests"))
        shutil.rmtree(os.path.join(stibnite_path, "tests", "test-doc"))


if __name__ == '__main__':
    pytest.main()
