"""
Setup script for CryptoAlpha AI Portfolio Manager
"""
from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="cryptoalpha",
    version="1.0.0",
    author="CryptoAlpha Team",
    author_email="team@cryptoalpha.ai",
    description="AI-powered cryptocurrency portfolio manager for Recall Network competitions",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/cryptoalpha/recall-agent",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Intended Audience :: Financial and Insurance Industry",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Office/Business :: Financial :: Investment",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
    ],
    python_requires=">=3.8",
    install_requires=requirements,
    extras_require={
        "dev": [
            "pytest>=7.4.0",
            "black>=23.7.0",
            "flake8>=6.0.0",
            "mypy>=1.5.0",
        ],
        "plotting": [
            "matplotlib>=3.7.2",
            "seaborn>=0.12.2",
        ],
    },
    entry_points={
        "console_scripts": [
            "cryptoalpha=main:main",
            "cryptoalpha-backtest=run_backtest:main",
        ],
    },
)
