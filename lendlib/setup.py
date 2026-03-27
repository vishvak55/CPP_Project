"""Setup configuration for lendlib package."""

from setuptools import setup, find_packages

setup(
    name="lendlib",
    version="1.0.0",
    description="Community Tool Lending Library - Custom OOP Python Library",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    author="Vishvaksen Machana",
    author_email="x25173421@student.ncirl.ie",
    packages=find_packages(),
    python_requires=">=3.8",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
