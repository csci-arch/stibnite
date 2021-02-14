def traverse_file_structure(current, function, **inner_function_args):
    """Recursively traverses the given folder and applies the function to every file that it finds.

    :param current: Source folder
    :type current: stibnite.file_operations.FolderType
    :param function: The function that will be applied to files of the current folder
    :type function: function
    :param inner_function_args: Arguments of the inner function
    :type inner_function_args: dictionary of sting to object
    :return: The same source folder
    :rtype: stibnite.file_operations.FolderType
    """
    if len(current.folders) > 0:
        for folder in current.folders.keys():
            traverse_file_structure(current.get_element(folder), function, **inner_function_args)
    if len(current.files) > 0:
        for file in current.files.keys():
            current.files[file] = function(current.files[file], **inner_function_args)

    return current

