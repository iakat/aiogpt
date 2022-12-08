from setuptools import setup, find_packages

setup(
    name="aiogpt",
    version="0.0.7",
    description="An asyncio wrapper for the OpenAI ChatGPT API",
    url="https://github.com/katlol/aiogpt",
    packages=find_packages(),
    install_requires=[
        "aiohttp",
    ],
    python_requires=">=3.6",
    classifiers=[
        "Development Status :: 2 - Pre-Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
    ],
)
