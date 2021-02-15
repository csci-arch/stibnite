import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="stibnite",
    version="0.0.1",
    author="csci-arch dev team",
    description="An automated python documentation generator",
    long_description=long_description,
    long_description_content_type="text/markdown",
    license='Apache License 2.0',
    url="https://github.com/csci-arch/stibnite",
    packages=setuptools.find_packages(),
    entry_points={"console_scripts": ["stibnite=stibnite.main:main"]},
    install_requires=['mkdocs', 'mkdocs-material', 'pymdown-extensions'],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: OS Independent",
    ],
)
