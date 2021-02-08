#!/usr/bin/env python
import os
from time import sleep
from subprocess import call, Popen
import webbrowser
from stibium import write_doc

if __name__ == "__main__":
    source_path = r"C:\My Files\stibium_input\FortuneTellerServer\src"
    output_path = r"C:\My Files\stibium_output\output"

    write_doc(source_path, output_path)

    sleep(1)

    os.chdir(output_path)

    call(["mkdocs", "build", "--clean"])
    Popen(["mkdocs", "serve"])

    sleep(2)

    webbrowser.open("http://127.0.0.1:8000/")
