from setuptools import setup

setup(
    name="pysidian",
    version="1.1.1",
    packages=[
        "pysidian",
        "pysidian.core",
    ],
    install_requires=[
        "zrcl3",
        "click",
        "click_shell"
    ],
    entry_points={
        "console_scripts": [
            "pysidian = pysidian.shell:main",
        ]
    },
    python_requires=">=3.8",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    author="ZackaryW",   
)