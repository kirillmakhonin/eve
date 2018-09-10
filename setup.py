from setuptools import setup
import os
import re

PACKAGE_ROOT_PATH = os.path.dirname(os.path.abspath(__file__))


def extract_requirements(filename):
    """
    Extracts requirements from a pip formatted requirements file.

    :param filename: str path to file
    :return: list of package names as strings
    """
    with open(filename, 'r') as requirements_file:
        return requirements_file.read().splitlines()


def extract_version(filename):
    """
    Extract version from .py file using regex

    :param filename: str path to file
    :return: str version
    """
    with open(filename, 'r') as version_file:
        file_content = open(filename, "rt").read()
        VSRE = r"^__version__ = ['\"]([^'\"]*)['\"]"
        mo = re.search(VSRE, file_content, re.M)
        if mo:
            return mo.group(1)
        else:
            raise RuntimeError("Unable to find version string in %s." % (file_content,))


setup(name='kirahhe',
      version=extract_version(os.path.join(PACKAGE_ROOT_PATH, 'kirahhe', 'version.py')),
      description='Startup process catcher',
      url='https://github.com/kirillmakhonin/kirahhe',
      author='Kirill Makhonin',
      author_email='kirill@makhonin.biz',
      license='Apache v2',
      packages=['kirahhe'],
      include_package_data=True,
      scripts=['bin/kirahhe'],
      classifiers=[
          "Programming Language :: Python :: 3",
          "License :: OSI Approved :: MIT License",
          "Operating System :: POSIX :: Linux",
          "Topic :: Software Development :: Debuggers",
          "Topic :: System :: Monitoring"
      ],
      zip_safe=False)
