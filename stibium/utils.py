
def traverse_file_structure(current, function, **inner_function_args):
    if len(current.folders)>0:
        for folder in current.folders.keys():
            traverse_file_structure(current.get_element(folder), function, **inner_function_args)
    if len(current.files)>0:
        for file in current.files.keys():
            current.files[file] = function(current.files[file], **inner_function_args)

    return current

