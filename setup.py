import setuptools

setuptools.setup(
    name="nils-utils",
    version="0.0.1",
    author="Nils Golembiewski",
    author_email="niolopa@gmail.com",
    description="Python utils for all kinds of stuff",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/NilsHasNoGithub/nils-utils",
    package_dir={"": "src"},
    packages=setuptools.find_packages("src"),
    python_requires=">=3.7",
    install_requires=[
        "ray",
        "tqdm",
    ],
)