# Dockerizing AllyCat (Running in Docker)

This guide for packaging up Allycat when running it in 'docker' mode.  If you are running AllyCat natively on python, see [this guide](package-native.md) instead.

The packaged container will contain the following:

- Downloaded and cleaned web content
- vector database that has indexed content
- all runtime code and libraries
- optionally, ollama model

## 1 - Build a Docker container (Optional)

**You only need to do this if you changed any code files.**

Otherwise go to step-2


```bash
docker  build  -t allycat  .
```


## 2 - Running the docker container

```bash
## To run official container
docker run -it --rm -p 8080:8080 sujee/allycat


## To run your custom built container
# docker run -it --rm -p 8080:8080 allycat
```


## 3 - Run AllyCat

Go through all steps in [running AllyCat](running-allycat.md).

This will ensure all the web content is downloaded, cleaned and indexed.  And all models are working.

Make sure the UI at [localhost:8080](http://localhost:8080/) is working.

All artifacts will be in `/allycat/workspace` directory.  You can inspect its contents as follows

```bash
tree  workspace/
```

```text
workspace/
├── crawled
├── llama_index_cache
├── ollama
├── processed
└── rag_website_milvus.db
...
```

## 4 - Packaging Allycat for deployment

**Make sure the AllyCat docker container is running; do not exit - you would loose all the artifacts**

Run these commands on another terminal.

**4.1 - `docker ps`**

Run `docker ps` command to find out the id of running AllyCat

Here is the sample output.  And the container id is `123456`

```text
CONTAINER ID   IMAGE     COMMAND                 CREATED          STATUS          PORTS                                                    NAMES
123456   allycat   "./docker-startup.sh"   17 minutes ago   Up 17 minutes   0.0.0.0:8080->8080/tcp, [::]:8080->8080/tcp, 11434/tcp   peaceful_elbakyan
```

**4.2 - Take a snaphot of the container**

```bash
docker commit    <container_id>    allycat-website-deploy

# eg
docker commit    123456    allycat-aialliance-deploy

# you can also add a version
docker commit    123456    allycat-aialliance-deploy:v1
```

**4.3 - Verify the snapshot is successfull**

```bash
docker   images
```

Sample output

```text
REPOSITORY                              TAG                  IMAGE ID       CREATED             SIZE
allycat-aialliance-deploy                          v1                   5ecf407ac875   3 minutes ago       6.83GB

```

**4.4 - Remove the container**

You can exit the previous allycat container

## 5 - Testing the deploy snapshot

Start the newly snapshotted docker image.


```bash
docker run -it --rm -p 8080:8080   allycat-aialliance-deploy    deploy
```

- the container being launched is `allycat-aialliance-deploy` - this is container we just snapshotted
- `deploy` option launches the web ui
- `p 8080:8080` makes sure the webui is available on `localhost:8080`

Go to url: [localhost:8080/](http://localhost:8080/)

And see if the chat is working.

## 6 - Continue to deploy

Now we are ready to deploy.

Continue to [deploy guide](deploy.md).