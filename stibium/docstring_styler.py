from utils import wrappers
import constants

class DocstringParser:
    def __init__(self,standard):
        self.std = standard

    def parse_docstring(self,docstring):
        return eval(f"DocstringParser._parse_{self.std}(docstring)")

    # TODO: Add raises part
    @staticmethod
    def _parse_rest(docstring):
        parts = docstring.split(":rtype:")
        return_type = parts[-1] if len(parts)>1 else None
        parts = parts[0].split(":return:")
        return_exp = parts[-1] if len(parts)>1 else None
        parts = parts[0].split(":param ")
        explanation = parts[0]
        params_info = [{constants.NAME:constants.RETURN,constants.EXPLANATION:return_exp,constants.TYPE:return_type}]
        for i in range(1,len(parts)):
            param_info={}
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
    escape = lambda text: text.replace('_','\\_')

    def __init__(self, style="md", standard="rest"):
        self.style = style
        self.std = standard

    def get_styled_structure(self, file_structure):
        return eval(f"wrappers.traverse_file_structure(file_structure)(DocstringStyler._style_file_{self.style}_{self.std})()")

    @staticmethod
    def _style_file_md_rest(self, file):
        for clas in file.classes:
            clas = DocstringStyler._style_class_md(clas,"rest")
        for func in file.functions:
            func = DocstringStyler._style_func_md(func,"rest")

    @staticmethod
    def _style_class_md(clas,std):
        clas.name = DocstringStyler._style_class_name_md(clas.name)
        clas.doc = DocstringStyler._style_docstring_md(clas.doc,std)
        for i in range(len(clas.methods)):
            clas.methods[i] = DocstringStyler._style_func_md(clas.methods[i],std,True)
        for i in range(len(clas.functions)):
            clas.functions[i] = DocstringStyler._style_func_md(clas.methods[i],std)

        return clas

    @staticmethod
    def _style_func_md(func,std, ismethod=False):
        if ismethod:
            func.name = DocstringStyler._style_method_name_md(func.obj.__self__.__class__.__name__, func.name, func.args)
        else:
            func.name = DocstringStyler._style_function_name_md(func.name, func.args)
        func.name_in_list = DocstringStyler._style_function_name_in_list_md(func.name_in_list)
        func.doc = DocstringStyler._style_docstring_md(func.doc,std)
        func.source_code = DocstringStyler._style_source_code_md(func.source_code)

        return func

    @staticmethod
    def _style_class_name_md(class_name):
        class_name = DocstringStyler.escape(class_name)
        return f"## **{class_name}**`#!py3 class` {{ #{class_name} data-toc-label={class_name} }}\n\n"

    @staticmethod
    def _style_method_name_md(class_name, method_name, args):
        class_name = DocstringStyler.escape(class_name)
        method_name = DocstringStyler.escape(method_name)
        args = DocstringStyler.escape(args)
        return f"### *{class_name}*.**{method_name}**`#!py3 {args}` {{ #{method_name} data-toc-label={method_name} }}\n\n"

    @staticmethod
    def _style_function_name_md(function_name, args):
        function_name = DocstringStyler.escape(function_name)
        args = DocstringStyler.escape(args)
        return f"## **{function_name}**`#!py3 {args}` {{ #{function_name} data-toc-label={function_name} }}\n\n"

    @staticmethod
    def _style_function_name_in_list_md(name_in_list):
        name_in_list = DocstringStyler.escape(name_in_list)
        return f" - [`{name_in_list}`](#{name_in_list})\n\n\n"

    @staticmethod
    def _style_docstring_md(docstring, standard):
        explanation, params = DocstringParser(standard).parse_docstring(docstring)
        return f"{docstring}\n"

    @staticmethod
    def _style_source_code_md(source_code):
        # fixes indentations
        source = source_code.split("\n")
        nb_indent = len(source[0]) - len(source[0].lstrip())
        source_code = ""
        for i in range(len(source)):
            source_code += f"\t{source[i][nb_indent:]}\n"
        return f'??? info "Source Code" \n\t```py3 linenums="1 1 2" \n{source_code}\n\t```\n\n'


