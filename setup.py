# coding: utf-8

import io
import os

from setuptools import find_packages, setup

# 包元信息
NAME = 'jycm'  # 实际包的名字
DESCRIPTION = 'A highly flexible json diff framework for python.'  # 项目描述
URL = 'https://github.com/eggachecat/jycm'  # 项目仓库 URL
EMAIL = 'sunao_0626@hotmail.com'  # 维护者邮箱地址
AUTHOR = 'eggachecat'  # 维护者姓名

here = os.path.abspath(os.path.dirname(__file__))


def get_requirements():
    with open(os.path.join(here, "requirements.txt"), "r") as reqs_file:
        reqs = reqs_file.readlines()
    return reqs


def get_requirements_dev():
    final_reqs = get_requirements()
    with open(os.path.join(here, "requirements-dev.txt"), "r") as reqs_file:
        reqs = reqs_file.readlines()
    for r in reqs:
        if "-r" not in r:
            final_reqs.append(r)

    return final_reqs


REQUIRES = get_requirements()
DEV_REQUIRES = get_requirements_dev()

try:
    with io.open(os.path.join(here, 'README.md'), encoding='utf-8') as f:
        long_description = '\n' + f.read()
except IOError:
    long_description = DESCRIPTION

about = {}
with io.open(os.path.join(here, NAME, '__version__.py')) as f:
    exec(f.read(), about)

setup(
    name=NAME,
    version=about['__version__'],
    description=DESCRIPTION,
    long_description=long_description,
    long_description_content_type='text/markdown',
    author=AUTHOR,
    author_email=EMAIL,
    url=URL,
    classifiers=[
        # Trove classifiers
        # Full list: https://pypi.python.org/pypi?%3Aaction=list_classifiers
        'Intended Audience :: Developers',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.5',
    ],
    keywords='json diff jsondiff operator flexible',
    packages=find_packages(exclude=['docs', 'tests']),
    install_requires=REQUIRES,
    tests_require=[
        'pytest>=4.0.0,<5.0.0'
    ],
    python_requires='!=3.0.*,!=3.1.*,!=3.2.*,!=3.3.*,!=3.4.*',
    extras_require={
        ':python_version<"3.5"': [
            'typing>=3.6.4',
        ],
        'dev': DEV_REQUIRES,
    },
    package_data={
        # for PEP484 & PEP561
        NAME: ['py.typed', '*.pyi'],
    },
)
