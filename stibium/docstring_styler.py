from stibium import utils, constants
import copy


class DocstringParser:
    def __init__(self,standard):
        self.std = standard

    def parse_docstring(self,docstring):
        return eval(f"DocstringParser._parse_{self.std}(docstring)")

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

    def __init__(self, style, standard):
        self.style = style
        self.std = standard

    def get_styled_structure(self, file_structure):
        return utils.traverse_file_structure(file_structure, DocstringStyler._style_file_md, standard=self.std)
        #return wrappers.traverse_file_structure(file_structure, standard=self.std)(DocstringStyler._style_file_md)()
        #return eval(f"wrappers.traverse_file_structure(file_structure, standard=self.std)(DocstringStyler._style_file_{self.style})()")

    @staticmethod
    def _style_file_md(file, standard):
        documentation = ""
        for i in range(len(file.classes)):
            styled_class = DocstringStyler._style_class_md(copy.deepcopy(file.classes[i]), standard)
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
            styled_function = DocstringStyler._style_func_md(file.functions[i], standard)
            documentation += styled_function.name
            documentation += styled_function.doc
            documentation += styled_function.source

            documentation += "______\n\n"

        file.documentation = {constants.FORMAT:constants.MARKDOWN, constants.CONTENT:documentation}

        return file

    @staticmethod
    def _style_class_md(clas,std):
        clas.name = DocstringStyler._style_class_name_md(clas.name)
        clas.doc = DocstringStyler._style_docstring_md(clas.doc,std)
        for i in range(len(clas.methods)):
            clas.methods[i] = DocstringStyler._style_func_md(clas.methods[i],std,True)
        for i in range(len(clas.functions)):
            clas.functions[i] = DocstringStyler._style_func_md(clas.functions[i],std)

        return clas

    @staticmethod
    def _style_func_md(func,std, ismethod=False):
        if ismethod:
            func.name = DocstringStyler._style_method_name_md(func.obj.__self__.__class__.__name__, func.name, func.args)
        else:
            func.name = DocstringStyler._style_function_name_md(func.name, func.args)
        func.name_in_list = DocstringStyler._style_function_name_in_list_md(func.name_in_list)
        func.doc = DocstringStyler._style_docstring_md(func.doc,std)
        func.source = DocstringStyler._style_source_code_md(func.source)

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
        return f" - [`{name_in_list}`](#{name_in_list})\n\n"


    @staticmethod
    def _style_docstring_md(docstring, standard):
        if standard == constants.MARKDOWN:
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

        else:
            explanation, params = DocstringParser(standard).parse_docstring(docstring)
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
        # fixes indentations
        source = source_code.split("\n")
        nb_indent = len(source[0]) - len(source[0].lstrip())
        source_code = ""
        for i in range(len(source)):
            source_code += f"\t{source[i][nb_indent:]}\n"
        return f'??? info "Source Code" \n\t```py3 linenums="1 1 2" \n\n{source_code}\n\t```\n\n'


