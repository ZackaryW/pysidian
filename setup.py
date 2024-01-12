from setuptools import setup

# 


setup(
    name="pysidian",
    version="2.0.2",
    packages=[
        "pysidian",
        "pysidian.utils",
    ],
    install_requires=[
        "click",
        "toml"
    ],
    # include zip files
    include_package_data=True,
    package_data={
        "pysidian": ["*.zip"]
    },
    entry_points={
        "console_scripts": [
            "pysidian = pysidian.cli:cli_main",
            "pysid = pysidian.cli:cli_main",
        ]
    },
    python_requires=">=3.8",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    author="ZackaryW",   
)