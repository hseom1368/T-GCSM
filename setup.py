"""
Setup script for T-GCSM v2.0
"""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="tgcsm",
    version="2.0.0",
    author="T-GCSM Development Team",
    description="Taiwan Ground Combat Simulation Model based on CSIS wargaming",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/tgcsm-v2",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Science/Research",
        "Topic :: Games/Entertainment :: Turn Based Strategy",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.7",
    install_requires=[
        "pandas>=1.3.0",
        "numpy>=1.21.0",
    ],
    extras_require={
        "dev": [
            "pytest>=6.0",
            "black>=21.0",
            "flake8>=3.9",
        ],
        "viz": [
            "matplotlib>=3.4.0",
            "seaborn>=0.11.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "tgcsm=run_simulation:main",
        ],
    },
)