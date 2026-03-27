from setuptools import setup, find_packages

setup(
    name="toollibrary-nci",
    version="1.0.0",
    author="Vishvaksen",
    author_email="vishvaksen@student.nci.ie",
    description="Community Tool Lending Library - manage tool loans, status, and borrower limits",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    packages=find_packages(),
    python_requires=">=3.8",
    install_requires=[],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
