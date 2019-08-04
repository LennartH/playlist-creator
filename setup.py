from setuptools import setup, find_packages

__version__ = "0.1.0"

install_requires = [
    "gmusicapi"
]

long_description = "Small project to create playlists for Google Play Music and Spotify"
# with open("README.md") as f:
#     long_description = f.read()

setup(
    name="playlist-creator",
    version=__version__,
    author="Lennart Hensler",
    author_email="lennarthensler@gmail.com",
    description="Small project to create playlists for Google Play Music and Spotify",
    long_description=long_description,
    long_description_content_type="text/markdown",
    project_urls={
        "Source": "https://github.com/LennartH/playlist-creator"
    },
    install_requires=install_requires,
    python_requires=">=3.7",
    packages=find_packages(exclude=["test", "jupyter"]),
    zip_safe=False,
    classifiers=[
        "Development Status :: 3 - Alpha",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3.7"
    ]
)
