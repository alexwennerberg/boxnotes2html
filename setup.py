from setuptools import find_packages, setup

with open("readme.md", "r") as fh:
    long_description = fh.read()

setup(
    name="boxnotes2html",
    version="0.1.3",
    author="Alex Wennerberg",
    author_email="alex@alexwennerberg.com",
    description="Converting from Box Notes to HTML",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/alexwennerberg/boxnotes2html",
    packages=find_packages(),
    install_requires=[],
    setup_requires=["pytest-runner"],
    tests_require=["pytest"],
    include_package_data=True,
    entry_points={
        "console_scripts": [
            "boxnotes2html=boxnotes2html.cli:run",
            "boxnote2html=boxnotes2html.cli:run",
        ]  # alias because if you're like me you'll type it wrong
    },
    classifiers=[
        # As from http://pypi.python.org/pypi?%3Aaction=list_classifiers
        # 'Development Status :: 1 - Planning',
        # 'Development Status :: 2 - Pre-Alpha',
        "Development Status :: 3 - Alpha",
        # 'Development Status :: 4 - Beta',
        # 'Development Status :: 5 - Production/Stable',
        # 'Development Status :: 6 - Mature',
        # 'Development Status :: 7 - Inactive',
        "Programming Language :: Python :: 3",
    ],
)
