"""Setup script for the Blueprint package."""
from setuptools import setup, find_packages

setup(
    name="blueprint",
    version="0.1.0",
    packages=find_packages(),
    include_package_data=True,
    install_requires=[],
    python_requires=">=3.6",
    author="Your Name",
    author_email="your.email@example.com",
    description="A Python project blueprint",
    keywords="blueprint, python",
    url="https://github.com/yourusername/blueprint",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
    ],
    entry_points={
        "console_scripts": [
            "blueprint=blueprint.__main__:main",
        ],
    },
) 