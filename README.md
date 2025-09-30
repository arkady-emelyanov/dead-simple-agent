# Dead simple PostgreSQL agent

The quick implementation of dead simple agent which helps 

The code was been tested using following:

* Windows 10, WSL2, Ubuntu
* RTX 3060 12GB

## Running

* Install Ollama and Docker
* Create virtual environment and install dependencies
* Run docker-compose
* Run agent and have fun!

### Install Ollama

The agent uses local Ollama installation, please install Ollama and pull `qwen3` model.

```bash
curl https://ollama.ai/install.sh | sh
```

```bash
ollama pull qwen2.5:14b
```

### Install Docker

Follow the [official instructions](https://docs.docker.com/desktop/setup/install/windows-install/).

### Run docker-compose

In separate terminal window run:

```bash
docker-compose up
```

### Run agent

```bash
python ./main.py
```

## Sample conversations

```
> show me top 2 users with longest email addresses.
< The top 2 users with the longest email addresses are:

| user_id | username |                 email                  | email_length |
|---------|----------|----------------------------------------|-------------|
|       4 | dave     | dave@midlengthdomain.example.org       |          32 |
|       5 | eve      | eve@example.domain.com                 |          22 |

Dave has the longest email address with a length of 32 characters,
followed by Eve with an email length of 22 characters.
```

```
> show top 2 users who owns most projects
< The top 2 users who own the most projects are:

| user_id | username   | project_count |
|---------|------------|---------------|
|       1 | alice      |             3 |
|       3 | charlie    |             2 |

Alice is the leading owner with 3 projects, followed by Charlie with 2 projects.
```


```
> perform maintenance of tables in public schema
< Maintenance operations such as VACUUM ANALYZE have been successfully executed 
on the `users` and `projects` tables within the `public` schema. This will help 
optimize their performance by cleaning up dead rows and updating statistics 
used by the query planner.
```

Quite cool.
