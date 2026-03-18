from setuptools import setup, find_packages

setup(
    name="ai-content-studio-agent",
    version="1.1.0",
    packages=find_packages(),
    install_requires=[
        "fastapi",
        "uvicorn",
        "google-genai",
        "python-dotenv",
        "pydantic",
        "python-jose[cryptography]",
        "passlib[bcrypt]==1.7.4",
        "bcrypt==3.2.2",
        "python-multipart",
        "cryptography",
        "httpx",
        "setuptools"
    ],
)
