import os
import logging
import re
import yaml
from datetime import datetime
from dotenv import load_dotenv
from langchain_community.embeddings import OpenAIEmbeddings
from langchain.prompts import ChatPromptTemplate
from langchain_elasticsearch import ElasticsearchRetriever
from langchain.memory import ConversationBufferMemory
from langchain.chains import ConversationalRetrievalChain
from langchain_openai import ChatOpenAI

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Globals for environment and prompts
_data_loaded = False
_prompts = None

def _load_env_and_prompts():
    global _data_loaded, _prompts
    if not _data_loaded:
        logger.info("Loading environment variables and prompts...")
        load_dotenv()
        es_url = os.getenv('ELASTICSEARCH_URL')
        if not es_url:
            logger.error("Elasticsearch URL `ELASTICSEARCH_URL` not found.")
            raise ValueError("Elasticsearch URL (`ELASTICSEARCH_URL`) is required.")
        # Load prompts YAML from same directory
        yaml_path = os.path.join(os.path.dirname(__file__), 'helper_prompts.yaml')
        logger.info(f"Loading helper prompts from {yaml_path}")
        with open(yaml_path, 'r') as f:
            _prompts = yaml.safe_load(f)
        _data_loaded = True

# Initialize embeddings and LLM
_embeddings = None
_llm = None

def get_embeddings_and_llm():
    global _embeddings, _llm
    _load_env_and_prompts()
    if _embeddings is None or _llm is None:
        _embeddings = OpenAIEmbeddings()
        _llm = ChatOpenAI(temperature=0.7, model_name="gpt-4o-mini")
    return _embeddings, _llm

# Build the Elasticsearch query body
def vector_query(search_query: str):
    embeddings, _ = get_embeddings_and_llm()
    vector = embeddings.embed_query(search_query)
    return {
        "size": 20,
        "query": {
            "bool": {
                "must": [
                    {"match": {"text": {"query": search_query, "boost": 0.3}}}
                ],
                "should": [
                    {"knn": {"field": "vector", "query_vector": vector, "num_candidates": 15, "boost": 0.7}}
                ]
            }
        }
    }

# Create an Elasticsearch retriever for given indices
def create_retriever(collection_names: list):
    _load_env_and_prompts()
    index_names = ",".join(collection_names)
    logger.info(f"Using Elasticsearch indices: {index_names}")
    return ElasticsearchRetriever.from_es_params(
        index_name=index_names,
        body_func=vector_query,
        content_field='text',
        url=os.getenv('ELASTICSEARCH_URL'),
    )

# Create a conversational retrieval chain using YAML-defined prompt
def create_conversational_chain(retriever, llm=None):
    _load_env_and_prompts()
    _, llm_instance = get_embeddings_and_llm() if llm is None else (None, llm)
    # Prepare system prompt
    current_dt = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    template = _prompts['conversational_chain']['system_prompt']
    prompt_text = template.replace("{current_dt}", current_dt)
    # Build prompt template
    prompt = ChatPromptTemplate.from_messages([
        ("system", prompt_text),
        ("human", "{question}")
    ])
    memory = ConversationBufferMemory(
        memory_key="chat_history",
        return_messages=True,
        output_key="answer"
    )
    return ConversationalRetrievalChain.from_llm(
        llm=llm_instance,
        retriever=retriever,
        memory=memory,
        return_source_documents=True,
        combine_docs_chain_kwargs={
            "prompt": prompt,
            "document_separator": "\n\n"
        },
        verbose=True
    )

# Utility to extract URLs from text
def extract_urls(text: str):
    return re.findall(
        r"http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+",
        text
    )
