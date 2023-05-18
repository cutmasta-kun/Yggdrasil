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
    name="memory",
    description="Memory - A service for storing and retrieving messages and accessing all data within the knowledge base",
    long_description=get_long_description(),
    long_description_content_type="text/markdown",
    author="cutmasta-kun",
    author_email="cutmastakun@gmail.com",
    url="https://github.com/cutmasta-kun/memory",
    project_urls={
        "Issues": "https://github.com/cutmasta-kun/memory/issues",
        "CI": "https://github.com/cutmasta-kun/memory/actions",
        "Changelog": "https://github.com/cutmasta-kun/memory/releases",
    },
    license="Apache License, Version 2.0",
    classifiers=[
        "Framework :: Datasette",
        "License :: OSI Approved :: Apache Software License",
    ],
    version=VERSION,
    packages=["memory"],
    install_requires=["datasette"],
    extras_require={"test": ["pytest", "pytest-asyncio"]},
    python_requires=">=3.7",
)
