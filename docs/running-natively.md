# Running Allycat Natively

This guide will show you how to run and develop with AllyCat natively.

## Prerequisites: 

- [Python 3.11 Environment or above](https://www.python.org/downloads/) or Anaconda Environment
- Ollama setup if planning to run LLM locally
- [Replicate](https://replicate.com) account for running LLM 

## Step-1: Clone this repo

```bash
git clone https://github.com/The-AI-Alliance/allycat/
cd allycat
```

## Step-2: Setup Python Environment

## 2a: Using python virtual env

```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## 2b: Setup using Anaconda Environment

Install [Anaconda](https://www.anaconda.com/) or [conda forge](https://conda-forge.org/)

And then:

```bash
conda create -n allycat-1  python=3.11
conda activate  allycat-1
pip install -r requirements.txt 
```

## LLM setup

We only need option (3) or (4)

## Step-3: Ollama Setup


We will use [ollama](https://ollama.com/) for running open LLMs locally.
This is the default setup.

Follow [setup instructions from Ollama site](https://ollama.com/download)

## Step-4: Replicate Setup (Optional)

For this step, we will be using Replicate API service.  We need a Replicate API token for this step.

Follow these steps:

- Get a **free** account at [replicate](https://replicate.com/home)
- Use this [invite](https://replicate.com/invites/a8717bfe-2f3d-4a52-88ed-1356231cdf03) to add some credit  💰  to your Replicate account!
- Create an API token on Replicate dashboard

Once you have an API token, add it to the project like this:

- Copy the file `env.sample.txt` into `.env`  (note the dot in the beginning of the filename)
- Add your token to `REPLICATE_API_TOKEN` in the .env file.  Save this file.

## Step-5: Continue to workflow

Proceed to [run Allycat](running-allycat.md)