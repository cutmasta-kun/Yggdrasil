# setup.py
# This script is based on the original setup.py script by Simon Willison found at:
# https://github.com/simonw/datasette-chatgpt-plugin/blob/main/setup.py
from setuptools import setup

VERSION = "v1"

setup(
    name="memory",
    description="Memory",
    long_description_content_type="text/markdown",
    author="cutmasta-kun",
    license="Apache License, Version 2.0",
    classifiers=[
        "Framework :: Datasette",
        "License :: OSI Approved :: Apache Software License",
    ],
    version=VERSION,
    packages=["memory"],
    install_requires=[
        "datasette",
        "flask",
        "flask_cors",
        "requests"
        ],
    extras_require={
        "test": [
            "pytest", 
            "pytest-asyncio"
            ]
        },
    python_requires=">=3.10",
)
