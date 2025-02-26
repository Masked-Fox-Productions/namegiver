from setuptools import setup, find_packages

setup(
    name="character-name-generator",
    version="0.1.0",
    packages=find_packages(),
    install_requires=["openai", "python-dotenv"],
    entry_points={
        "console_scripts": [
            "namegen=name_generator:main",
        ],
    },
)