from setuptools import setup, find_packages

setup(
    name="namegiver",
    version="0.1.2",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    install_requires=[
        "openai",
        "python-dotenv",
        "python-Levenshtein",
    ],
    author="Aaron Pogue",
    author_email="aaron.pogue@maskedfox.com",
    description="AI-based Character Name Generator",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/masked-fox-productions/namegiver",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
    entry_points={
        "console_scripts": [
            "namegen=namegiver.namegiver:main",
        ],
    },
)