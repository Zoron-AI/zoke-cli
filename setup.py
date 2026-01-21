from setuptools import setup, find_packages

setup(
    name="zoke",
    version="0.1.0",
    description="Convert natural language to shell commands using OpenAI",
    packages=find_packages(),
    python_requires=">=3.8",
    install_requires=[
        "openai>=1.0.0",
    ],
    entry_points={
        "console_scripts": [
            "zoke=zoke.cli:main",
        ],
    },
)
