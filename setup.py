# setup.py
from setuptools import setup, find_packages

setup(
    name="agentic_hackathon",
    version="0.1",
    packages=find_packages(),
    install_requires=[
        "cdp-sdk>=0.0.13",
        "cdp-langchain>=0.0.13",
        "langchain>=0.1.0",
        "langchain-openai>=0.0.1",
        "python-dotenv>=1.0.0",
        "requests>=2.31.0",
    ],
)