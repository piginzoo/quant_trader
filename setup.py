# coding:utf8
from setuptools import setup,Command,find_packages
import os
class CleanCommand(Command):
    """Custom clean command to tidy up the project root."""
    user_options = []

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def run(self):
        os.system('rm -vrf ./build ./dist ./*.pyc ./*.tgz ./*.egg-info')

setup(
    name="quant_trader",
    version="1.0.0",
    description="Trade Proxy for realtime",
    long_description="",
    author="piginzoo",
    author_email="piginzoo@gmail.com",
    license="BSD",
    url="https://github.com/piginzoo/quant_trader",
    keywords="China stock trade",
    cmdclass={
        'clean': CleanCommand,
    },
    packages=find_packages(where=".", exclude=('test', 'test.*', 'conf'), include=('*',))
)
