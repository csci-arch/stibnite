import pytest
import platform
import inspect
import copy


def test_docstringparser_parse_docstring():
    from stibnite.docstring_styler import DocstringParser
    from stibnite import constants

    parser = DocstringParser("NOT_A_REAL_STYLE")

    with pytest.raises(AttributeError):
        parser.parse_docstring("asd")

    valid_styles = [constants.RESTRUCTERED]
    valid_example = ["""Example rest"""]
    try:
        for i in range(len(valid_styles)):
            parser = DocstringParser(valid_styles[i])
            parser.parse_docstring(valid_example[i])
    except Exception as e:
        pytest.fail(f"Unexpected error : {str(e)}")


def test_docstringparser_parse_rest():
    from stibnite.docstring_styler import DocstringParser
    from stibnite import constants

    case1 = """Example one line
    """

    case2 = """
    Example one line below

    """

    case3 = """Example without param

    """

    case4 = """Example with param

    :param x: example text for param x
    :type x: sometype
    """

    case5 = """Example without param type test

    :param x: example text for param x
    """

    case6 = """Example with param without empty line 
    :param x: example text for param x
    :type x: sometype
    """

    case7 = """Example with return

    :param x: example text for param x
    :type x: sometype
    :return: description of return
    """

    case8 = """Example with return and return type

    :param x: example text for param x
    :type x: sometype
    :return: description of return
    :rtype: some return type
    """

    case9 = """Example with multi
    text param

    :param x: example multi text
    for param x
    :type x: sometype
    """

    parser = DocstringParser(constants.RESTRUCTERED)

    exp_case1, params_case1 = parser.parse_docstring(case1)
    exp_case2, params_case2 = parser.parse_docstring(case2)
    exp_case3, params_case3 = parser.parse_docstring(case3)
    exp_case4, params_case4 = parser.parse_docstring(case4)
    exp_case5, params_case5 = parser.parse_docstring(case5)
    exp_case6, params_case6 = parser.parse_docstring(case6)
    exp_case7, params_case7 = parser.parse_docstring(case7)
    exp_case8, params_case8 = parser.parse_docstring(case8)
    exp_case9, params_case9 = parser.parse_docstring(case9)

    assert " ".join(exp_case1.split()) == "Example one line"
    assert " ".join(exp_case2.split()) == "Example one line below"
    assert " ".join(exp_case3.split()) == "Example without param"
    assert " ".join(exp_case4.split()) == "Example with param"
    assert " ".join(exp_case5.split()) == "Example without param type test"
    assert " ".join(exp_case6.split()) == "Example with param without empty line"
    assert " ".join(exp_case7.split()) == "Example with return"
    assert " ".join(exp_case8.split()) == "Example with return and return type"
    assert " ".join(exp_case9.split()) == "Example with multi text param"

    assert len(params_case1) == 1
    assert params_case1[0][constants.NAME] == constants.RETURN
    assert params_case1[0][constants.EXPLANATION] is None
    assert params_case1[0][constants.TYPE] is None

    assert len(params_case2) == 1
    assert params_case2[0][constants.NAME] == constants.RETURN
    assert params_case2[0][constants.EXPLANATION] is None
    assert params_case3[0][constants.TYPE] is None

    assert len(params_case3) == 1
    assert params_case3[0][constants.NAME] == constants.RETURN
    assert params_case3[0][constants.EXPLANATION] is None
    assert params_case3[0][constants.TYPE] is None

    assert len(params_case4) == 2
    assert params_case4[0][constants.NAME] == constants.RETURN
    assert params_case4[0][constants.EXPLANATION] is None
    assert params_case4[0][constants.TYPE] is None
    assert params_case4[1][constants.NAME] == "x"
    assert " ".join(params_case4[1][constants.EXPLANATION].split()) == "example text for param x"
    assert " ".join(params_case4[1][constants.TYPE].split()) == "sometype"

    assert len(params_case5) == 2
    assert params_case5[0][constants.NAME] == constants.RETURN
    assert params_case5[0][constants.EXPLANATION] is None
    assert params_case5[0][constants.TYPE] is None
    assert params_case5[1][constants.NAME] == "x"
    assert " ".join(params_case5[1][constants.EXPLANATION].split()) == "example text for param x"
    assert params_case5[1][constants.TYPE] is None

    assert len(params_case6) == 2
    assert params_case6[0][constants.NAME] == constants.RETURN
    assert params_case6[0][constants.EXPLANATION] is None
    assert params_case6[0][constants.TYPE] is None
    assert params_case6[1][constants.NAME] == "x"
    assert " ".join(params_case6[1][constants.EXPLANATION].split()) == "example text for param x"
    assert " ".join(params_case6[1][constants.TYPE].split()) == "sometype"

    assert len(params_case7) == 2
    assert params_case7[0][constants.NAME] == constants.RETURN
    assert " ".join(params_case7[0][constants.EXPLANATION].split()) == "description of return"
    assert params_case7[0][constants.TYPE] is None
    assert params_case7[1][constants.NAME] == "x"
    assert " ".join(params_case7[1][constants.EXPLANATION].split()) == "example text for param x"
    assert " ".join(params_case7[1][constants.TYPE].split()) == "sometype"

    assert len(params_case8) == 2
    assert params_case8[0][constants.NAME] == constants.RETURN
    assert " ".join(params_case8[0][constants.EXPLANATION].split()) == "description of return"
    assert " ".join(params_case8[0][constants.TYPE].split()) == "some return type"
    assert params_case8[1][constants.NAME] == "x"
    assert " ".join(params_case8[1][constants.EXPLANATION].split()) == "example text for param x"
    assert " ".join(params_case8[1][constants.TYPE].split()) == "sometype"

    assert len(params_case9) == 2
    assert params_case9[0][constants.NAME] == constants.RETURN
    assert params_case9[0][constants.EXPLANATION] is None
    assert params_case9[0][constants.TYPE] is None
    assert params_case9[1][constants.NAME] == "x"
    assert " ".join(params_case9[1][constants.EXPLANATION].split()) == "example multi text for param x"
    assert " ".join(params_case9[1][constants.TYPE].split()) == "sometype"


def test_docstringstyler__style_source_code_md():
    from stibnite.docstring_styler import DocstringStyler

    # TEST FOR BAD INDENTATION

    case1 = '''
def this_is_an_example_source_code(with_multiple_tabs, and, spaces):
    
    def inner_tab():
        class inner_tab_inner_class:
            def __init__():
                pass
        
        return inner_tab_inner_class()
    
    return inner_tab()
    '''

    case2 = '''
    def inner_tab():
        class inner_tab_inner_class:
            def __init__():
                pass

        return inner_tab_inner_class()
    '''

    case3 = '''
            class inner_tab_inner_class:
                def __init__():
                    pass

    '''

    case4 = '''

                def __init__():
                    pass


    '''

    res_case1 = DocstringStyler._style_source_code_md(case1).replace(
        f'??? info "Source Code" \n\t```py3 linenums="1 1 2" \n\n', "")
    res_case2 = DocstringStyler._style_source_code_md(case2).replace(
        f'??? info "Source Code" \n\t```py3 linenums="1 1 2" \n\n', "")
    res_case3 = DocstringStyler._style_source_code_md(case3).replace(
        f'??? info "Source Code" \n\t```py3 linenums="1 1 2" \n\n', "")
    res_case4 = DocstringStyler._style_source_code_md(case4).replace(
        f'??? info "Source Code" \n\t```py3 linenums="1 1 2" \n\n', "")

    assert res_case1.split("\n")[0][0] == "\t"
    assert res_case1.split("\n")[0].split("\t")[1] == "def this_is_an_example_source_code(with_multiple_tabs, and, spaces):"

    assert res_case2.split("\n")[0][0] == "\t"
    assert res_case2.split("\n")[0].split("\t")[1] == "def inner_tab():"

    assert res_case3.split("\n")[0][0] == "\t"
    assert res_case3.split("\n")[0].split("\t")[1] == "class inner_tab_inner_class:"

    assert res_case4.split("\n")[0][0] == "\t"
    assert res_case4.split("\n")[0].split("\t")[1] == "def __init__():"

    # TEST FOR COHERENCE

    case5 = "this is my test"

    res_case5 = DocstringStyler._style_source_code_md(case5)

    assert res_case5 == f'??? info "Source Code" \n\t```py3 linenums="1 1 2" \n\n\tthis is my test\n\n\t```\n\n'


def test_docstringstyler__style_docstring_md():
    from stibnite.docstring_styler import DocstringStyler
    from stibnite import constants

    case1 = """Example one line
        """

    case2 = """
        Example one line below

        """

    case3 = """Example without param

        """

    case4 = """Example with param

        :param x: example text for param x
        :type x: sometype
        """

    case5 = """Example without param type test

        :param x: example text for param x
        """

    case6 = """Example with param without empty line 
        :param x: example text for param x
        :type x: sometype
        """

    case7 = """Example with return

        :param x: example text for param x
        :type x: sometype
        :return: description of return
        """

    case8 = """Example with return and return type

        :param x: example text for param x
        :type x: sometype
        :return: description of return
        :rtype: some return type
        """

    case9 = """Example with multi
        text param

        :param x: example multi text
        for param x
        :type x: sometype
        """

    case10 = """Example with return type but without return desc

        :param x: example text for param x
        :type x: sometype
        :rtype:                         somethingweird
        """

    expected_case1 = "Example one line\n\n"
    expected_case2 = "Example one line below\n\n"
    expected_case3 = "Example without param\n\n"
    expected_case4 = "Example with param\n\n**Parameters**\n\n> **x:** `sometype` -- example text for param x\n\n"
    expected_case5 = "Example without param type test\n\n**Parameters**\n\n> **x:** `n/a` -- example text for param x\n\n"
    expected_case6 = "Example with param without empty line\n\n**Parameters**\n\n> **x:** `sometype` -- example text for param x\n\n"
    expected_case7 = "Example with return\n\n**Parameters**\n\n> **x:** `sometype` -- example text for param x\n\n**Returns**\n\n> `n/a` -- description of return\n\n"
    expected_case8 = "Example with return and return type\n\n**Parameters**\n\n> **x:** `sometype` -- example text for param x\n\n**Returns**\n\n> `some return type` -- description of return\n\n"
    expected_case9 = "Example with multi text param\n\n**Parameters**\n\n> **x:** `sometype` -- example multi text for param x\n\n"
    expected_case10 = "Example with return type but without return desc\n\n**Parameters**\n\n> **x:** `sometype` -- example text for param x\n\n**Returns**\n\n> `somethingweird`\n\n"

    res_case1 = DocstringStyler._style_docstring_md(case1, constants.RESTRUCTERED)
    res_case2 = DocstringStyler._style_docstring_md(case2, constants.RESTRUCTERED)
    res_case3 = DocstringStyler._style_docstring_md(case3, constants.RESTRUCTERED)
    res_case4 = DocstringStyler._style_docstring_md(case4, constants.RESTRUCTERED)
    res_case5 = DocstringStyler._style_docstring_md(case5, constants.RESTRUCTERED)
    res_case6 = DocstringStyler._style_docstring_md(case6, constants.RESTRUCTERED)
    res_case7 = DocstringStyler._style_docstring_md(case7, constants.RESTRUCTERED)
    res_case8 = DocstringStyler._style_docstring_md(case8, constants.RESTRUCTERED)
    res_case9 = DocstringStyler._style_docstring_md(case9, constants.RESTRUCTERED)
    res_case10 = DocstringStyler._style_docstring_md(case10, constants.RESTRUCTERED)

    assert res_case1 == expected_case1
    assert res_case2 == expected_case2
    assert res_case3 == expected_case3
    assert res_case4 == expected_case4
    assert res_case5 == expected_case5
    assert res_case6 == expected_case6
    assert res_case7 == expected_case7
    assert res_case8 == expected_case8
    assert res_case9 == expected_case9
    assert res_case10 == expected_case10

    case11 = '''
            class inner_tab_inner_class:
                def __init__():
                    pass

    '''

    expected_case11 = "\nclass inner_tab_inner_class:\n    def __init__():\n        pass\n\n    \n\n"
    res_case11 = DocstringStyler._style_docstring_md(case11, constants.MARKDOWN)

    assert expected_case11 == res_case11


def test_docstringstyler__style_class_md():
    from stibnite.core_types import ClassType
    from stibnite import constants
    from stibnite.utils import get_project_path
    from stibnite.file_operations import import_module
    from stibnite.docstring_styler import DocstringStyler
    separator = constants.SEPARATOR_DICT[platform.system()]

    module = import_module("src.class_and_function", f"{get_project_path()}example{separator}src{separator}class_and_function.py")

    shark_class = [
        ClassType(obj)
        for name, obj in inspect.getmembers(module, inspect.isclass)
        if obj.__module__ == module.__name__
    ][0]

    result = DocstringStyler._style_class_md(copy.deepcopy(shark_class), constants.MARKDOWN)

    assert isinstance(result, ClassType)
    assert result.name == DocstringStyler._style_class_name_md(shark_class.name)
    assert result.doc == DocstringStyler._style_docstring_md(shark_class.doc, constants.MARKDOWN)


def test_docstringstyler__style_func_md():
    from stibnite.core_types import FunctionType,ClassType
    from stibnite import constants
    from stibnite.utils import get_project_path
    from stibnite.file_operations import import_module
    from stibnite.docstring_styler import DocstringStyler
    separator = constants.SEPARATOR_DICT[platform.system()]

    module = import_module("src.class_and_function",
                           f"{get_project_path()}example{separator}src{separator}class_and_function.py")

    shark_class = [
        ClassType(obj)
        for name, obj in inspect.getmembers(module, inspect.isclass)
        if obj.__module__ == module.__name__
    ][0]

    swimclass_method = shark_class.methods[0]

    maxi_function = [
        FunctionType(obj)
        for name, obj in inspect.getmembers(module, inspect.isfunction)
        if obj.__module__ == module.__name__
    ][0]

    result = DocstringStyler._style_func_md(copy.deepcopy(maxi_function), constants.MARKDOWN)

    assert isinstance(result, FunctionType)
    assert result.name == DocstringStyler._style_function_name_md(maxi_function.name, maxi_function.args)
    assert result.name_in_list == DocstringStyler._style_function_name_in_list_md(maxi_function.name_in_list)
    assert result.doc == DocstringStyler._style_docstring_md(maxi_function.doc, constants.MARKDOWN)
    assert result.source == DocstringStyler._style_source_code_md(maxi_function.source)

    result = DocstringStyler._style_func_md(copy.deepcopy(swimclass_method), constants.MARKDOWN, ismethod=True)

    assert isinstance(result, FunctionType)
    assert result.name == DocstringStyler._style_method_name_md(swimclass_method.obj.__self__.__class__.__name__, swimclass_method.name, swimclass_method.args)
    assert result.name_in_list == DocstringStyler._style_function_name_in_list_md(swimclass_method.name_in_list)
    assert result.doc == DocstringStyler._style_docstring_md(swimclass_method.doc, constants.MARKDOWN)
    assert result.source == DocstringStyler._style_source_code_md(swimclass_method.source)


def test_docstringstyler__style_file_md():
    from stibnite.core_types import FunctionType, ClassType
    from stibnite import constants
    from stibnite.utils import get_project_path
    from stibnite.file_operations import import_module, FileType
    from stibnite.docstring_styler import DocstringStyler
    separator = constants.SEPARATOR_DICT[platform.system()]

    module = import_module("src.class_and_function",
                           f"{get_project_path()}example{separator}src{separator}class_and_function.py")

    classes = [
        ClassType(obj)
        for name, obj in inspect.getmembers(module, inspect.isclass)
        if obj.__module__ == module.__name__
    ]
    functions = [
        FunctionType(obj)
        for name, obj in inspect.getmembers(module, inspect.isfunction)
        if obj.__module__ == module.__name__
    ]

    class_and_functions = FileType("src.class_and_function",
                                   functions=functions,
                                   classes=classes)

    result = DocstringStyler._style_file_md(class_and_functions,constants.MARKDOWN)

    assert isinstance(result, FileType)
    assert hasattr(result, "documentation")
    assert isinstance(result.documentation, dict)
    assert isinstance(result.documentation[constants.CONTENT], str)

def test_docstringstyler_get_styled_structure():
    from stibnite.core_types import FunctionType, ClassType
    from stibnite import constants
    from stibnite.utils import get_project_path
    from stibnite.file_operations import import_module, FileType, FolderType
    from stibnite.docstring_styler import DocstringStyler
    separator = constants.SEPARATOR_DICT[platform.system()]

    module = import_module("src.class_and_function",
                           f"{get_project_path()}example{separator}src{separator}class_and_function.py")

    classes = [
        ClassType(obj)
        for name, obj in inspect.getmembers(module, inspect.isclass)
        if obj.__module__ == module.__name__
    ]
    functions = [
        FunctionType(obj)
        for name, obj in inspect.getmembers(module, inspect.isfunction)
        if obj.__module__ == module.__name__
    ]

    class_and_functions = FileType("src.class_and_function",
                                   functions=functions,
                                   classes=classes)

    src = FolderType("something")
    src.add_file(class_and_functions)

    styler = DocstringStyler(constants.MARKDOWN,constants.MARKDOWN)
    result = styler.get_styled_structure(src)

    assert isinstance(result, FolderType)


if __name__ == "__main__":
    pytest.main()

