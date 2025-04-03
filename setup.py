from setuptools import setup, find_packages

setup(
    name="data-annotation-tool",
    version="1.0.0",
    description="A GUI tool for annotating tabular data",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    author="Yuqun Zhang",
    author_email="yuqunzhang@GolGrin.com",
    packages=find_packages(),
    install_requires=[
        "pandas>=1.3.0",
        "openpyxl>=3.0.7",
        "xlrd>=2.0.1"
    ],
    entry_points={
        "console_scripts": [
            "data-annotator=src.main:main"
        ]
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.7",
)
