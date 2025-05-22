# Developing Allycat

## Contributing

We welcome your feedback / suggestions.

We also **love** pull requests 😄

## 1 - allycat Docker

We publish Allycat as an easy to run Docker image.

The 'dev' version of AllyCat only has code + libraries (like Ollama) installed.  No user data (like downloaded website content)

When ever any code / documentation changes are made, we would publish a new Docker image

## 2 - Env Setup

Before you start:  make sure you have completed [native python env setup](running-natively.md).

## 3 - Build  Docker

```bash
docker build . -f Dockerfile-dev -t allycat
```
Note: We are supplying `Dockerfile-dev` as build file.

## 4 - (Optional) Including Ollama Models in Docker

This docker image does not have ollama model yet.  We can  add that.

This will increase docker image size.  Typical 'good model' can be about 1G in size.

### 4.1 - Run the new image

Running the allycat-0docker

```bash
docker run -it --rm -p 8080:8080 allycat
```

### 4.2 - Download the ollama model

Once in the container, download Ollama models.  Our default model is gemma3:1b.

```bash
# inside docker
ollama   pull    gemma3:1b
```

### 4.3 - Take a snapshot

Find the running container id 

```bash
# from another terminal
docker ps
```

Take a snapshot

```bash
docker   commit   <container_id>   allycat2
```

### 4.4 - Try the new docker image

```bash
docker run -it --rm -p 8080:8080 allycat2
```

Check downloaded models by

```bash
ollama   list
```

### 4.5 - Tag the model

```bash
docker    tag   allycat2   allycat
```

## 5 - Publish the docker  image

```bash
docker  login 

# tag the image to match dockerhub account
# Replace "USER" with your dockerhub username (e.g. 'sujee')
docker image tag  allycat    USER/allycat
# e.g.
docker image tag  allycat    sujee/allycat
# we can add version info
docker image tag  allycat    sujee/allycat:v1


# push it
docker  push   USER/allycat
# e.g.
docker  push   sujee/allycat
# pushing specific versions
docker  push   sujee/allycat:v1
```

---

