"""
Minimal setup.py for TiktokClipGenerator package installation.

This enables the project to be installed as an editable package, making
the 'adapters' and 'validators' modules importable from anywhere.

Usage:
    pip install -e .

This installs the package in "editable" mode, meaning changes to source
files are immediately available without reinstalling.
"""

from setuptools import setup, find_packages

setup(
    name="tiktok-clip-generator",
    version="0.1.0",
    description="TikTok Clip Generator - AI-powered video content creation pipeline",
    packages=find_packages(exclude=["tests", "tests.*", "output", "output.*"]),
    install_requires=[
        "requests>=2.31.0",
        "streamlit>=1.28.0",
    ],
    python_requires=">=3.8",
)
