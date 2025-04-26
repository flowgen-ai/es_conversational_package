# es_conversational_package

A helper package for building conversational retrieval chains over Elasticsearch using LangChain and OpenAI.

## Features

- **Elasticsearch Retriever**: Combines k-NN vector search with text matching for richer results.
- **Conversational Chain**: Builds a `ConversationalRetrievalChain` with memory and custom prompts.
- **Environment & Prompts Loader**: Automatically loads `.env` variables and YAML-based prompts.
- **Utility Functions**: URL extraction from text and easy access to embeddings & LLM instances.

## Installation

Install directly from GitHub:

```bash
pip install git+https://github.com/flowgen-ai/es_conversational_package.git@main
```

Or specify a tag:

```bash
pip install git+https://github.com/flowgen-ai/es_conversational_package.git@v0.1.1
```

## Quickstart

1. **Configure environment**:

   Create a `.env` file in your project root:
   ```env
   ELASTICSEARCH_URL=https://your-es-domain:9200
   OPENAI_API_KEY=sk-...
   ```

2. **Use the package**:

   ```python
   from es_conversational import create_retriever, create_conversational_chain

   # Create a retriever for one or more indices:
   retriever = create_retriever(["index1", "index2"])

   # Build the conversational chain:
   convo = create_conversational_chain(retriever)

   # Ask a question:
   result = convo({"question": "What are the latest trends?"})
   print(result['answer'])
   for doc in result['source_documents']:
       print(doc.page_content)
   ```

3. **Extract URLs** (utility):

   ```python
   from es_conversational import extract_urls
   text = "Check our site at https://example.com for details"
   print(extract_urls(text))  # ['https://example.com']
   ```

## API Reference

### `create_retriever(collection_names: list[str]) -> ElasticsearchRetriever`

- **collection_names**: List of Elasticsearch index names.
- **Returns**: Configured `ElasticsearchRetriever` that uses a combined vector & text query.

### `create_conversational_chain(retriever, llm: Optional = None) -> ConversationalRetrievalChain`

- **retriever**: An `ElasticsearchRetriever` instance.
- **llm**: (Optional) A custom LLM instance; defaults to `ChatOpenAI(temperature=0.7, model_name="gpt-4o-mini")`.
- **Returns**: A LangChain `ConversationalRetrievalChain` with memory and source-chaining.

### `extract_urls(text: str) -> list[str]`

- Extracts all HTTP/HTTPS URLs from the input text.

## Development

Clone the repo and install in editable mode:

```bash
git clone https://github.com/flowgen-ai/es_conversational_package.git
cd es_conversational_package
pip install -e .
```

Run linting and tests (if any):

```bash
flake8 .
pytest
```

## Contributing

Contributions are welcome! Please open issues or pull requests against `main`.

1. Fork the repository
2. Create a branch for your feature or bugfix
3. Commit your changes and open a PR
4. Ensure all tests pass and code is linted

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

