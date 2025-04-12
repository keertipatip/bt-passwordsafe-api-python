from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="bt-passwordsafe-api",
    version="1.0.0",
    author="Prudhvi Keertipati",
    author_email="",
    description="A Python package for interacting with BeyondTrust Password Safe API",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/keertipatip/bt-passwordsafe-api-python",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Topic :: Security",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    python_requires=">=3.7",
    install_requires=[
        "requests>=2.25.0",
    ],
    keywords=["beyondtrust", "passwordsafe", "password", "security", "api", "sdk", "pam", "privilegedaccessmanagement"],
)
