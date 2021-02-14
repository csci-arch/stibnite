from stibnite import utils, constants
import copy


class DocstringParser:
    """This class is the main class to be used for parsing supported docstrings.

    :param style: The style that documentation written in
    :type style: string
    """
    def __init__(self, style):
        self.style = style

    def parse_docstring(self, docstring):
        """Parses given string and returns two ouput (for now) that contains all the information about the docstring.

        :param docstring: Docstring that is going to be parsed
        :type docstring: string
        :return: A tuple which contains an explanation and information about parameters
        :rtype: A tuple that contains two value which are a string and a dictionary
        """
        return eval(f"DocstringParser._parse_{self.style}(docstring)")

    @staticmethod
    def _parse_rest(docstring):
        """Parses docstrings that are written in reStructered text.

        :param docstring: Docstring that is going to be parsed
        :type docstring: string
        :return: A tuple which contains an explanation and information about parameters
        :rtype: A tuple that contains two value which are a string and a dictionary
        """
        parts = docstring.split(":rtype:")
        return_type = parts[-1] if len(parts)>1 else None
        parts = parts[0].split(":return:")
        return_exp = parts[-1] if len(parts)>1 else None
        parts = parts[0].split(":param ")
        explanation = parts[0]
        params_info = [{constants.NAME: constants.RETURN, constants.EXPLANATION: return_exp, constants.TYPE: return_type}]
        for i in range(1,len(parts)):
            param_info = {}
            param = parts[i]
            param_parts = param.split(":type ")
            param_exp = param_parts[0]
            param_type = param_parts[1] if len(param_parts)>1 else None
            param_info[constants.NAME] = param_exp.split(":")[0]
            param_info[constants.EXPLANATION] = ":".join(param_exp.split(":")[1:])
            param_info[constants.TYPE] = ":".join(param_type.split(":")[1:]) if param_type is not None else None
            params_info.append(param_info)

        return explanation, params_info

class DocstringStyler:
    """This class is the main class that stylize the information that is collected from python files into documentation with given style.

    :param input_style: The style that the documentation written in
    :type input_style: string
    :param output_style: The style that the documentation will be written in
    :type output_style: string
    """
    escape = lambda text: text.replace('_','\\_')

    def __init__(self, output_style, input_style):
        self.output_style = output_style
        self.input_style = input_style

    def get_styled_structure(self, file_structure):
        """Stylizes the given file structure

        :param file_structure: The root of the file structure that is going to be traversed to stylize
        :type file_structure: stibnite.file_operations.FolderType
        :return: The same root but each documentation field in stibnite.file_operations.FileType under the file structure of the root is filled with stylized documentation text 
        :rtype: stibnite.file_operations.FolderType
        """
        return eval(f"utils.traverse_file_structure(file_structure, DocstringStyler._style_file_{self.output_style}, input_style=self.input_style)")

    @staticmethod
    def _style_file_md(file, input_style):
        """Stylizes the given file structure in markdown style

        :param file: The file that is going to be stylized
        :type file: stibnite.file_operations.FileType
        :return: The same file but documentation field is filled with stylized documentation text 
        :rtype: stibnite.file_operations.FileType
        """
        documentation = ""
        for i in range(len(file.classes)):
            styled_class = DocstringStyler._style_class_md(copy.deepcopy(file.classes[i]), input_style)
            documentation += styled_class.name
            documentation += styled_class.doc if not styled_class.doc.isspace() else ""
            if len(styled_class.methods) > 0:
                documentation += f"**class methods:** \n\n"
                for method in styled_class.methods:
                    documentation += method.name_in_list
            if len(styled_class.functions) > 0:
                documentation += f"**class functions & static methods:** \n\n"
                for function in styled_class.functions:
                    documentation += function.name_in_list

            for method in styled_class.methods:
                documentation += method.name
                documentation += method.doc if not method.doc.isspace() else ""
                documentation += method.source

            for function in styled_class.functions:
                documentation += function.name
                documentation += function.doc if not function.doc.isspace() else ""
                documentation += function.source

            documentation += "______\n\n"

        for i in range(len(file.functions)):
            styled_function = DocstringStyler._style_func_md(file.functions[i], input_style)
            documentation += styled_function.name
            documentation += styled_function.doc
            documentation += styled_function.source

            documentation += "______\n\n"

        file.documentation = {constants.FORMAT:constants.MARKDOWN, constants.CONTENT:documentation}

        return file

    @staticmethod
    def _style_class_md(clas, input_style):
        """Stylizes the given class in markdown style

        :param clas: The class that is going to be stylized
        :type clas: stibnite.core_types.ClassType
        :param input_style: Style of the inputted docstring
        :type input_style: string
        :return: The same class but name, doc, methods and functions fields are changed with stylized version of them 
        :rtype: stibnite.core_types.ClassType
        """
        clas.name = DocstringStyler._style_class_name_md(clas.name)
        clas.doc = DocstringStyler._style_docstring_md(clas.doc,input_style)
        for i in range(len(clas.methods)):
            clas.methods[i] = DocstringStyler._style_func_md(clas.methods[i],input_style,True)
        for i in range(len(clas.functions)):
            clas.functions[i] = DocstringStyler._style_func_md(clas.functions[i],input_style)

        return clas

    @staticmethod
    def _style_func_md(func, input_style, ismethod=False):
        """Stylizes the given function or method in markdown style

        :param func: The function that is going to be stylized
        :type func: stibnite.core_types.FunctionType
        :param input_style: Style of the inputted docstring
        :type input_style: string
        :param ismethod: Flag that changes styling from function styling to method styling, defaults to False
        :type ismethod: bool, optional
        :return: The same function or method but name, name_in_list, doc and source fields are changed with stylized version of them 
        :rtype: stibnite.core_types.FunctionType
        """
        if ismethod:
            func.name = DocstringStyler._style_method_name_md(func.obj.__self__.__class__.__name__, func.name, func.args)
        else:
            func.name = DocstringStyler._style_function_name_md(func.name, func.args)
        func.name_in_list = DocstringStyler._style_function_name_in_list_md(func.name_in_list)
        func.doc = DocstringStyler._style_docstring_md(func.doc, input_style)
        func.source = DocstringStyler._style_source_code_md(func.source)

        return func

    @staticmethod
    def _style_class_name_md(class_name):
        """Stylizes the given class name in markdown style

        :param class_name: Name of the class
        :type class_name: string
        :return: Class name stylized in markdown style
        :rtype: string
        """
        class_name = DocstringStyler.escape(class_name)
        return f"## **{class_name}**`#!py3 class` {{ #{class_name} data-toc-label={class_name} }}\n\n"

    @staticmethod
    def _style_method_name_md(class_name, method_name, args):
        """Stylizes the given method name in markdown style

        :param class_name: Name of the method's parent class
        :type class_name: string
        :param method_name: Name of the method
        :type method_name: string
        :param args: Arguments seperated with ','
        :type args: string
        :return: Method name stylized in markdown style
        :rtype: string
        """
        class_name = DocstringStyler.escape(class_name)
        method_name = DocstringStyler.escape(method_name)
        return f"### *{class_name}*.**{method_name}**`#!py3 {args}` {{ #{method_name} data-toc-label={method_name} }}\n\n"

    @staticmethod
    def _style_function_name_md(function_name, args):
        """Stylizes the given function name in markdown style

        :param function_name: Name of the function
        :type function_name: string
        :param args: Arguments seperated with ','
        :type args: string
        :return: Function name stylized in markdown style
        :rtype: string
        """
        function_name = DocstringStyler.escape(function_name)
        return f"## **{function_name}**`#!py3 {args}` {{ #{function_name} data-toc-label={function_name} }}\n\n"

    @staticmethod
    def _style_function_name_in_list_md(name_in_list):
        """Stylizes the given function name to list functions of classes in markdown style

        :param name_in_list: Name of the function
        :type name_in_list: string
        :return: Function name stylized in markdown style
        :rtype: string
        """
        return f" - [`{name_in_list}`](#{name_in_list})\n\n"


    @staticmethod
    def _style_docstring_md(docstring, input_style):
        """Stylizes the docstring in markdown style

        :param docstring: The docstring that is going to be stylized
        :type docstring: string
        :param input_style: Style of the inputted docstring
        :type input_style: string
        :return: The docstring stylized in markdown style
        :rtype: string
        """
        if input_style == constants.MARKDOWN:
            rows = docstring.split("\n")
            first_string = None
            for row in rows:
                if not row.isspace() and row != '':
                    first_string = row
                    break
            if first_string is None:
                return docstring

            nb_indent = len(first_string) - len(first_string.lstrip())
            for i in range(len(rows)):
                if len(rows[i])>nb_indent:
                    rows[i] = rows[i][nb_indent:]
            doc = '\n'.join(rows)
            doc = f"{doc}\n\n"

        else:
            explanation, params = DocstringParser(input_style).parse_docstring(docstring)
            doc = ""
            rows = explanation.split("\n")
            rows = [row for row in rows if row != "" and not row.isspace()]
            for i in range(len(rows)):
                rows[i] = rows[i].lstrip().rstrip()
            explanation = " ".join(rows)
            doc += f"{explanation}\n\n" if not explanation.isspace() and explanation != "" else ""
            if len(params) > 1:
                doc+=f"**Parameters**\n\n"
                for i in range(1, len(params)):
                    if params[i][constants.TYPE] is not None:
                        doc += f"> **{params[i][constants.NAME].lstrip().rstrip()}:** `{params[i][constants.TYPE].lstrip().rstrip()}` -- {params[i][constants.EXPLANATION].lstrip().rstrip()}\n\n"
                    else:
                        doc += f"> **{params[i][constants.NAME].lstrip().rstrip()}:** `n/a` -- {params[i][constants.EXPLANATION].lstrip().rstrip()}\n\n"
            if params[0][constants.TYPE] is not None or params[0][constants.EXPLANATION] is not None:
                doc += f"**Returns**\n\n> `{params[0][constants.TYPE].lstrip().rstrip() if params[0][constants.TYPE] is not None else 'n/a'}`"
                desc = ' -- ' + params[0][constants.EXPLANATION].lstrip().rstrip() if params[0][constants.EXPLANATION] is not None else ''
                doc += f"{desc}\n\n"

        return doc

    @staticmethod
    def _style_source_code_md(source_code):
        """Stylizes the source code in markdown style

        :param source_code: The source code that is going to be stylized
        :type source_code: string
        :return: The source code stylized in markdown style
        :rtype: string
        """
        # Fixes indentations
        source = source_code.split("\n")
        nb_indent = len(source[0]) - len(source[0].lstrip())
        source_code = ""
        for i in range(len(source)):
            source_code += f"\t{source[i][nb_indent:]}\n"
        return f'??? info "Source Code" \n\t```py3 linenums="1 1 2" \n\n{source_code}\n\t```\n\n'


