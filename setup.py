import os

from setuptools import setup


def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()


setup(
    name="Flask-Docs",
    version="0.2.7",
    url="https://github.com/kwkwc/flask-docs",
    license="MIT",
    author="kwkw",
    author_email="wei497896143@yeah.net",
    description="Adds Docs support to Flask.",
    # long_description=read("README.md"),
    # long_description_content_type="text/markdown",
    packages=["flask_docs"],
    zip_safe=False,
    include_package_data=True,
    platforms="any",
    keywords=[
        "flask",
        "api",
        "apidoc",
        "doc",
        "docs",
        "documentation",
        "md",
        "markdown",
        "RESTful",
        "auto",
    ],
    install_requires=["Flask", "Flask-RESTful"],
    classifiers=[
        "Environment :: Web Environment",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Programming Language :: Python :: 2",
        "Programming Language :: Python :: 3",
        "Topic :: Internet :: WWW/HTTP :: Dynamic Content",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
)
