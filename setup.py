import setuptools

from mementomap import __VERSION__

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="mementomap",
    version=__VERSION__,
    author="Sawood Alam",
    author_email="ibnesayeed@gmail.com",
    description="A Tool to Summarize Web Archive Holdings",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/oduwsdl/MementoMap",
    license="MIT License",
    packages=setuptools.find_packages(),
    provides=[
        "mementomap"
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Environment :: Console",
        "Topic :: Internet",
        "Topic :: Internet :: WWW/HTTP",
        "Topic :: Internet :: WWW/HTTP :: Indexing/Search",
        "Development Status :: 4 - Beta"
    ],
    python_requires='>=3.6',
    entry_points={
        "console_scripts": [
            "mementomap = mementomap.__main__:main"
        ]
    }
)
