# -*- coding: utf-8 -*-

from setuptools import find_packages, setup
import runpy

__version__ = runpy.run_path("markshift/__init__.py")["__version__"]

setup(
    name="markshift",
    version=__version__,
    author="Shohei Fujii",
    url="https://github.com/ompugao/markshift",
    description="Indentation oriented markup language and its parser",
    packages=find_packages(
        exclude=("configs", "tests", "tests.*", "docs.*", "projects.*")
    ),
    python_requires='>=3.7, <4',
    install_requires=['lark', 'regex', 'click'],
    extras_require={
        "dev": ["pysen", "flake8==4.0.1", "isort==5.10.1", "black==21.4b2", "mypy==0.910", "ipython"],
    },
    ext_modules=[],
    entry_points={
        'console_scripts': [
            'markshift_cli=markshift.cli.main:main',
            ]
        }
)
