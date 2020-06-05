"""Reflexec.
"""

from setuptools import find_packages, setup

__version__ = "0.2.0"

with open("README.md") as f:
    long_description = f.read()

setup(
    name="reflexec",
    version=__version__,
    description=(
        "Utility to automate annoying save-and-run routines in terminal environment"
    ),
    long_description=long_description,
    long_description_content_type="text/markdown",
    classifiers=[
        "Development Status :: 4 - Beta",
        "Environment :: Console",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: POSIX :: Linux",
        "Programming Language :: Python :: 3 :: Only",
        "Topic :: Terminals",
        "Topic :: Utilities",
    ],
    keywords="reflexec",
    author="Ivar Smolin",
    author_email="okul@linux.ee",
    url="https://github.com/ookull/reflexec",
    download_url="https://github.com/ookull/reflexec/archive/v{}.tar.gz".format(
        __version__
    ),
    license="MIT",
    install_requires=["pyinotify"],
    packages=find_packages(exclude=("tests", "docs")),
    entry_points={"console_scripts": ["reflexec=reflexec.reflexec:main"]},
)
