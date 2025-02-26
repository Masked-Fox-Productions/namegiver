from setuptools import setup, find_packages

setup(
    name="namegiver",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "openai",
        "python-dotenv",
        "python-Levenshtein",
    ],
    author="Your Name",
    description="AI-based Character Name Generator",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    python_requires=">=3.6",
    entry_points={
        "console_scripts": [
            "namegen=name_generator:main",
        ],
    },
)