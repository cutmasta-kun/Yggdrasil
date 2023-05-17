# setup.py
# This script is based on the original setup.py script by Simon Willison found at:
# https://github.com/simonw/datasette-chatgpt-plugin/blob/main/setup.py
from setuptools import setup
import os

VERSION = "0.1"

def get_long_description():
    with open(
        os.path.join(os.path.dirname(os.path.abspath(__file__)), "README.md"),
        encoding="utf8",
    ) as fp:
        return fp.read()

setup(
    name="datasette-chatgpt-plugin",
    description="A Datasette plugin that turns a Datasette instance into a ChatGPT plugin",
    long_description=get_long_description(),
    long_description_content_type="text/markdown",
    author="cutmasta-kun",
    author_email="cutmastakun@gmail.com",
    url="https://github.com/cutmasta-kun/datasette-chatgpt-plugin",
    project_urls={
        "Issues": "https://github.com/cutmasta-kun/datasette-chatgpt-plugin/issues",
        "CI": "https://github.com/cutmasta-kun/datasette-chatgpt-plugin/actions",
        "Changelog": "https://github.com/cutmasta-kun/datasette-chatgpt-plugin/releases",
    },
    license="Apache License, Version 2.0",
    classifiers=[
        "Framework :: Datasette",
        "License :: OSI Approved :: Apache Software License",
    ],
    version=VERSION,
    packages=["datasette_chatgpt_plugin"],
    entry_points={"datasette": ["chatgpt_plugin = datasette_chatgpt_plugin"]},
    install_requires=["datasette"],
    extras_require={"test": ["pytest", "pytest-asyncio"]},
    python_requires=">=3.7",
)
