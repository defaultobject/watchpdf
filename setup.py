import setuptools



setuptools.setup(
    name="Paper Rename", 
    version="0.0.1",
    author="O Hamelijnck",
    author_email="ohamelijnck@turing.ac.uk",
    description="Watch and rename accedmic papers",
    long_description="",
    long_description_content_type="text/markdown",
    url="N/A",
    packages=setuptools.find_packages(),
    scripts=["cli/watchpdf"],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
    install_requires = [
        "typer",
        "watchdog",
        " pdf-renamer==1.0rc9"
    ],
    extras_require={

    }
)
