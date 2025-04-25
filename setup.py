from setuptools import find_packages, setup

setup(
    name="es_conversational",                # PyPI name
    version="0.1.0",
    description="Conversational Elasticsearch+LLM helper chain",
    long_description=open("README.md", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    author="aidin",
    author_email="aidin@cube10.io",
    url="https://github.com/flowgen-ai/es_conversational_package",
    packages=find_packages(exclude=["tests*", "docs*"]),
    include_package_data=True,               # to pick up YAML
    package_data={"es_conversational": ["helper_prompts.yaml"]},
    install_requires=[
        "python-dotenv",
        "PyYAML",
        "langchain-community",
        "langchain",
        "langchain-elasticsearch",
        "openai",
    ],
    classifiers=[
        "Programming Language :: Python :: 3.10",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.8",
)
