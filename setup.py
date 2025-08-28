from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="accessibility-toolkit",
    version="1.0.0",
    author="Pythonic Accessibility Toolkit Team",
    author_email="team@accessibility-toolkit.org",
    description="A Python-based accessibility toolkit for automated website accessibility testing",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/pythonic-accessibility-toolkit",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Intended Audience :: Information Technology",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Internet :: WWW/HTTP",
        "Topic :: Software Development :: Testing",
        "Topic :: Software Development :: Quality Assurance",
        "Topic :: Text Processing :: Markup :: HTML",
        "Topic :: Web Accessibility",
    ],
    python_requires=">=3.8",
    install_requires=requirements,
    extras_require={
        "dev": [
            "pytest>=7.4.3",
            "pytest-asyncio>=0.21.1",
            "black>=23.0.0",
            "flake8>=6.0.0",
            "mypy>=1.5.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "accessibility-toolkit=accessibility_toolkit.cli:main",
        ],
    },
    include_package_data=True,
    package_data={
        "accessibility_toolkit": ["templates/*", "config/*"],
    },
)
