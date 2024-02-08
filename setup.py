from setuptools import setup

# 


setup(
    name="pysidian",
    version="2.0.2",
    packages=[
        "pysidian",
        "pysidian.core",
        "pysidian.cli",
        "pysidian.data",
        "pysidian.data.pyarmor_runtime_000000"
    ],
    install_requires=[
        "click",
        "toml",
        "packaging",
        "psutil",
        "sioDict",
        "orjson",
    ],
    # include zip files
    include_package_data=True,
    package_data={
        "pysidian.data": ["*.zip"]
    },
    entry_points={
        "console_scripts": [
            "pysidian = pysidian.cli.__main__:cli",
        ]
    },
    python_requires=">=3.10",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    author="ZackaryW",   
)