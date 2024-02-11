from setuptools import setup

setup(
    name="pysidian",
    version="3.2.0",
    packages=[
        "pysidian",
        "pysidian.core",
        "pysidian.data",
        "pysidian.utils",
    ],
    install_requires=[
        "click",
        "toml",
        "packaging",
        "psutil",
        "sioDict",
        "orjson",
        "uuid",
    ],
    # include zip files
    include_package_data=True,
    package_data={
        "pysidian.data": ["*.zip"],
    },
    entry_points={
        "console_scripts": [
            "pysidian = pysidian.cli:cli",
        ]
    },
    python_requires=">=3.10",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    author="ZackaryW",
    description="A CLI tool written in Python intended for managing obsidian plugin deployments and development",
)
