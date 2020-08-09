import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="Atorin-Discord-Bot",
    version="0.0.1",
    author="liamdj23",
    author_email="me@liamdj23.ovh",
    description="Great Discord Bot with 1k+ servers",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/liamdj23/Atorin-Discord-Bot",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: GNU License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)