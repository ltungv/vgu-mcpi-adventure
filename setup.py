from setuptools import setup


with open('README.md', 'r') as f:
    long_description = f.read()


setup(
    name='mcpi_adventure',
    version='1.5',
    description="A minecraft's mini game created using python on MinecraftPi",
    long_description=long_description,
    author='Tung Le Vo',
    author_email='letung3105@gmail.com',
    url='https://www.github.com/letung3105/vgu-mcpi-adventure',
    packages=[
        'mcpi_adventure',
    ],

    install_requires=[
        'mcpi',
    ],

    scripts=[
        'bin/mcpi_adventure',
    ],

    entry_points={
        'console_scripts': ['mcpi_adventure=mcpi_adventure.command_line:main'],
    },
)
