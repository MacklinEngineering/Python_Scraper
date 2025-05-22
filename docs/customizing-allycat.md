# Customizing Allycat

- [1 - To try a different LLM with Ollama](#1---to-try-a-different-llm-with-ollama)
- [2 - Trying a different model with Replicate](#2---trying-a-different-model-with-replicate)


## 1 - To try a different LLM with Ollama

**Edit file [my_config.py](../my_config.py)**

```python
MY_CONFIG.LLM_RUN_ENV = 'local_ollama'
MY_CONFIG.LLM_MODEL = "gemma3:1b" 
``` 

Change the model to something else:

```python
MY_CONFIG.LLM_MODEL = "qwen3:1.7b"
```

**Download the ollama model**

```bash
ollama  pull qwen3:1.7b
```

Verify the model is ready:

```bash
ollama   list
```

Make sure the model is listed.  Now the model is ready to be used.

Now you can run the query:

```bash
python   4_query.py
```

## 2 - Trying a different model with Replicate

**Edit file [my_config.py](../my_config.py)**

```python
MY_CONFIG.LLM_RUN_ENV = 'replicate'
MY_CONFIG.LLM_MODEL = "meta/meta-llama-3-8b-instruct"
```

Change the model to the desired model:

```python
MY_CONFIG.LLM_MODEL = "ibm-granite/granite-3.2-8b-instruct
```

Now you can run the query:

```bash
python   4_query.py
```

## 3 - Trying various embedding models

**Edit file [my_config.py](../my_config.py)** and change these lines:

```python
MY_CONFIG.EMBEDDING_MODEL = 'ibm-granite/granite-embedding-30m-english'
MY_CONFIG.EMBEDDING_LENGTH = 384
```

You can find [embedding models here](https://huggingface.co/spaces/mteb/leaderboard)

Once embedding model is changed:

1) Rerun chunking and embedding again

```bash
python  3_save_to_vector_db.py
```

2) Run query

```bash
python   4_query.py
```


