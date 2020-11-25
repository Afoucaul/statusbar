import setuptools

with open("./requirements.txt", "r") as fd:
    requirements = list(fd)


setuptools.setup(
    author="Armand Foucault",
    long_description=open("README.md").read(),
    name="statusbar",
    packages=setuptools.find_packages(),
    install_requires=requirements
)
