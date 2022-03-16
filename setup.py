#! python3

import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name='curriculum_mapper',
    version='0.1',
    author="Timmy Chan",
    author_email="mathtodata@gmail.com",
    description="A Utility for Mapping University Curriculum using NetworkX and PyVis",  # noqa: E501
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/TimmyChan/curriculum_mapper",
    packages=setuptools.find_packages(where="src"),
    package_dir={"": "src"},
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent"
    ],
    python_requires=">=3.8",
)
