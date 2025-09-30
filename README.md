# Dead simple PostgreSQL agent

The quick implementation of dead simple agent which helps querying the PostgreSQL database.
The agent has interactions memory and can be used fun playground (see sample questions below).

The code was been tested using following:

* Python 3.11
* Windows 10, WSL2 @ Ubuntu
* RTX 3060 12GB

## Running

* Install Ollama and Docker
* Create virtual environment and install dependencies
* Run docker-compose in separate terminal
* Run agent (`python ./main.py`) and have fun!

### Install Ollama

The agent uses local Ollama installation, please install Ollama and pull `qwen2.5:14b` model.

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

It will take around 10-15 seconds to boot the agent.

## Sample conversation log

```
> show me top 2 users with longest email addresses.
+ SELECT id, name, email FROM public.users ORDER BY LENGTH(email) DESC LIMIT 2;
+ SELECT column_name, data_type FROM information_schema.columns WHERE table_schema = 'public' AND table_name = 'users';
+ SELECT id, username, email FROM public.users ORDER BY LENGTH(email) DESC LIMIT 2;
< The top 2 users with the longest email addresses are:

| id | username | email                                          |
|----|----------|------------------------------------------------|
| 4  | dave     | dave@midlengthdomain.example.org               |
| 5  | eve      | eve@example.domain.com                         |

User `dave` has the longest email address, followed by user `eve`.
```

```
> show top 2 users who owns most projects
+ SELECT column_name FROM information_schema.columns WHERE table_schema = 'public' AND table_name = 'projects';
+ SELECT u.id AS user_id, u.username, COUNT(p.owner_id) AS project_count FROM public.users u JOIN public.projects p ON u.id = p.owner_id GROUP BY u.id, u.username ORDER BY project_count DESC LIMIT 2;
< The top 2 users who own the most projects are:

| user_id | username | project_count |
|---------|----------|---------------|
| 1       | alice    | 3             |
| 3       | charlie  | 2             |

User `alice` owns the most projects with a total of 3, followed by user `charlie` with 2 projects.
```

Quite cool.
