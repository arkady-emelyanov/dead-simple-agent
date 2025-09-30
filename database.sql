CREATE TABLE IF NOT EXISTS users (
  id SERIAL PRIMARY KEY,
  username TEXT NOT NULL,
  email TEXT NOT NULL,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT now()
);

INSERT INTO users (id, username, email) VALUES
  (1, 'alice', 'alice@example.com'),
  (2, 'bob', 'bob@short.io'),
  (3, 'charlie', 'charlie@example.com'),
  (4, 'dave', 'dave@midlengthdomain.example.org'),
  (5, 'eve', 'eve@example.domain.com'),
  (6, 'mallory', 'mallory@example.org'),
  (7, 'trent', 'trent@short.co');


CREATE TABLE projects (
  id SERIAL PRIMARY KEY,
  name TEXT NOT NULL,
  owner_id INTEGER NOT NULL,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT now(),
  FOREIGN KEY (owner_id) REFERENCES users (id)
);

INSERT INTO projects (id, name, owner_id) VALUES
  (1, 'Project 1.1', 1),
  (2, 'Project 2.1', 1),
  (3, 'Project 3.1', 1),
  (4, 'Project 4.3', 3),
  (5, 'Project 5.3', 3),
  (6, 'Project 6.5', 5),
  (7, 'Project 7.7', 7);
