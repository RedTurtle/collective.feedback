# -*- coding: utf-8 -*-
"""Installer for the collective.feedback package."""

from setuptools import find_packages
from setuptools import setup


long_description = "\n\n".join(
    [
        open("README.rst").read(),
        open("CONTRIBUTORS.rst").read(),
        open("CHANGES.rst").read(),
    ]
)


setup(
    name="collective.feedback",
    version="1.1.2",
    description="Feedback mechanism integration for io-comune",
    long_description=long_description,
    # Get more from https://pypi.org/classifiers/
    classifiers=[
        "Development Status :: 1 - Planning",
        "Environment :: Web Environment",
        "Framework :: Plone",
        "Framework :: Plone :: Addon",
        "Framework :: Plone :: 5.2",
        "Framework :: Plone :: 6.0",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Operating System :: OS Independent",
        "License :: OSI Approved :: GNU General Public License v2 (GPLv2)",
    ],
    keywords="Python Plone CMS",
    author="RedTurtle Technology",
    author_email="sviluppoplone@redturtle.it",
    url="https://github.com/collective/collective.feedback",
    project_urls={
        "PyPI": "https://pypi.org/project/collective.feedback/",
        "Source": "https://github.com/collective/collective.feedback",
        "Tracker": "https://github.com/collective/collective.feedback/issues",
        # 'Documentation': 'https://collective.feedback.readthedocs.io/en/latest/',
    },
    license="GPL version 2",
    packages=find_packages("src", exclude=["ez_setup"]),
    namespace_packages=["collective"],
    package_dir={"": "src"},
    include_package_data=True,
    zip_safe=False,
    python_requires=">=3.7",
    install_requires=[
        "setuptools",
        "souper.plone",
        "collective.honeypot>=2.1",
    ],
    extras_require={
        "test": [
            "gocept.pytestlayer",
            "plone.app.testing",
            "plone.restapi[test]",
            "pytest-cov",
            "pytest-plone>=0.2.0",
            "pytest-docker",
            "pytest-mock",
            "pytest",
            "zest.releaser[recommended]",
            "zestreleaser.towncrier",
            "pytest-mock",
            "requests-mock",
        ],
    },
    entry_points="""
    [z3c.autoinclude.plugin]
    target = plone
    [console_scripts]
    update_locale = collective.feedback.locales.update:update_locale
    """,
)
