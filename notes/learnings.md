## Next steps?

- [x] set up my DB
- [x] think through table schema
- [x] create user table first
- [x] sanity check/validate schema design in psql terminal by inserting new users into table; making sure ids auto generate, usernames have to be unique etc.
- [x] test python to postgres connection via POST/users
- [x] create habits table
- [x] sanity check schema in psql terminal
- []

## Quick Definitions

**FastAPI** = framework for building APIs (similar to Express in Node)

**FastAPI route** = regular Python function with decorator (@app.get(...), @app.post(...)), so that FastAPI knows to call it when a matching request comes in

**framework** = provides structural skeleton, handles routes, logic (calls my code for me when an endpoint is requested) and architecture

**Uvicorn** = runs the server and listens on specified port (similar to Node.js)

**schema** = defines db organization, how tables relate and what rules the data must follow

**psycopg2** = library that allows python to talk to postgreSQL db

**pydantic** = library for data validation and parsing using type hints; powers the BaseModel classes

**pyjwt** = library for creating and verifying JWTs for authenticating users

**dotenv** = library to load .env files in python

## Project Overview

Habit tracker

- supports multiple users
- a user can:
  - create a user account
  - add a new habit
  - get their habits
  - get a habit's current streak (could be <= longest streak)
  - get a habit's longest streak
  - mark a habit as completed for the day
  - unmark a habit
  - delete a habit
- a user can not:
  - update contents of a habit -> bc if they could, it would cause problems later on when calculating streaks?
  - access/update other user's habits

## HTTP Status Codes

- 200 OK: The request succeeded
- 201 Created: The request succeeded and a new resource was created as a result
- 202 Accepted: The request has been accepted for processing, but processing is not complete yet
- 400 Bad Request: The server cannot process the request due to perceived client error (e.g., malformed request syntax)
- 401 Unauthorized: The request lacks valid authentication credentials
- 403 Forbidden: The server understands the request and the client identity is known, but the client does not have permission access rights
- 404 Not Found: The server cannot find the requested resource
- 422 Unprocessable Entity: more specific to "the request is structured correctly (valid JSON, right fields present), but a value inside it fails a validation rule" — e.g., password is too short, email isn't in a valid email format
- 429 Too Many Requests: The user has sent too many requests in a given amount of time (rate-limiting)
- 500 Internal Server Error: A generic error message when the server encounters an unexpected condition
- 502 Bad Gateway: The server, while acting as a gateway or proxy, received an invalid response from the upstream server
- 503 Service Unavailable: The server is currently unable to handle the request due to temporary overloading or maintenance
- 504 Gateway Timeout: The server, while acting as a gateway or proxy, did not receive a timely response from the upstream server

## Backend logic

- my main.py file builds the app object which holds all routes
- every decorator runs once at startup and registers the route to app (not everytime a request comes in)
- the fx itself is not called yet until a request comes in
- after the whole file has been executed, uvicorn starts listening on port and waits for incoming requests
- let's say I defined two routes with same path & method, FastAPI doesn't overwrite the first with second; instead it registers both routes into the app obj and when a req comes in, it executes the first
  match

## Virtual Environments

what is it?

- a folder of installed packages and small scripts inside venv/bin (such as activate)
- these scripts have the exact absolute path baked into them via plain text
- let's say I manually rename the folder, the scripts will continue to point to old path which no longer exists -> problemo
  - lesson learned: don't rename a venv folder after creating, instead delete and recreate it

benefits

- avoids version clashes bc it isolates project packages/dependencies so they don't conflict with other probjects
- helps with reproducability
- keeps computer clean bc packages get installed into isolated folder preventing global clutter

db in venv

- when trying to set up my db i was unsure if i needed to re-install postgres into my venv (which alr existed globally)
- postgres is a standalone db server that does not live in venv
- venv is only for python packages!

## Misc

- requirements.txt is the equivalent to package.json for node aka lists dependencies and their versions for reproducibility purposes
- SQL
  - if it's a SELECT: result = cursor.fetchone() or fetchall()
  - if it's an INSERT/UPDATE/DELETE: conn.commit()

## Issues ive ran across so far..

- renamed my venv folder to .venv manually rather than deleting it and creating it fresh; this caused my venv to break -> claude gave me a bunch of lines to run in my terminal
  to rebuild it from scratch which looked like a bunch of gibberish so i stopped and asked what each
  line meant and what it was doing beforehand:

  ```
  deactivate
  rm -rf .venv
  python3 -m venv .venv
  source .venv/bin/activate
  which python3
  echo $VIRTUAL_ENV
  ```

  deactivates broken venv

  recursively removes folders and everything inside the venv

  create brand new venv

  activates it

  two verification checks - confirms both paths match

- syntax issue: using single vs double quotes in psql

  - single quotes is a string literal
  - double quotes is an identifier (e.g. a column, table name, etc)

- cursor is undefined error
  - Every time a route needs to talk to the database, it needs its own fresh connection and cursor, created inside that route's function — created and creating a cursor doesn't happen once for your whole app; it happens per-request, inside whatever function is handling that specific request.
  - Connection vs. Cursor
    - Connection (conn) — represents the actual open "line" between your Python program and the Postgres server. Think of it like picking up a phone and dialing — you're now linked to the database, but you haven't said anything yet. Opening a connection is a relatively "expensive" operation (it takes a moment to establish), so you typically open one connection and reuse it for multiple operations, rather than reconnecting for every single query.
    - Cursor (cursor) — created from an open connection, and it's what actually lets you execute commands and retrieve results. Continuing the phone analogy: the connection is the open phone line, and the cursor is you actually speaking into it — sending a specific request ("run this query") and listening for the response.
  - why this error? This comes down to your choice not to use an ORM (a decision you made deliberately, remember) — you're using the "raw" driver, which means you're doing the low-level work yourself (open connection, create cursor, execute, fetch, close) instead of a library doing it invisibly for you. If you had used SQLAlchemy (the Postgres equivalent of Mongoose, roughly) — you'd similarly set up a connection once.
- CORS policy
  - tried using fetch() request to POST/users endpoint from about:blank origin and came across CORS policy error
    - about:blank's origin is treated as "null" (string null) and bc its origin doesn't match the server, the cors policy gets triggered
  - CORS policy: built in browser security that prevents clients from different or unauthorized origins to make requests to APIs; requires that the frontend and backend be on same origin or an authorized origin in order for them to talk to each other
  - origin: the combination of protocol + domain + port (e.g. http://localhost:3000, http://localhost:8000)
  - possible solutions suggested by AI
    - option 1: allow_origins=["*"]
      - fixes/bypasses the CORS error but potentially exposes the app/makes it vulnerable to the security issues that this policy protects against (e.g. malicious site trying to make direct requests to my API)
      - fine for local dev since my API isn't deployed publicly, it is only reachable on localhost and there's no real user/sensitive data at stake yet
      - The purpose right now is learning/testing, not securing a production system; optimizing for "unblock myself and keep learning" is the right tradeoff at this stage
    - option 2: explicitly list only the specific origin(s) I trust
      - prevents random sites from making authorized cross-origin requests to my API
      - more restrictive which requires me to actually know and maintain the list of allowed origins which may require a bit of ongoing configuration as my setup changes (e.g. different port for a future frontend)

## Security

- Currently using `allow_origins=["*"]` for CORS since this is local-only
- will replace with specific allowed origin(s) before any public deployment

## AI Usage

- AI recommended me to use an ORM; rather than just defaulting to use what AI suggested I asked AI to list what the tradeoffs were
  - ORM (e.g., SQLAlchemy): less boilerplate, built-in SQL injection protection, easier migrations but hides the actual SQL, adds a new abstraction to learn, and can generate inefficient queries I don't immediately see
  - Raw SQL (e.g., psycopg2): full transparency into exactly what queries run, reinforces SQL skills directly, no new abstraction to learn but more manual work per query, manual connection handling, and no automatic migration tooling
- Decision: decided to go with raw SQL because I want to practice writing queries and know exactly what's happening; allows me to see the actual mechanics that every ORM is secretly doing on my behalf; understand why a connection and cursor are needed per-request; also this way makes learning an ORM later much faster bc once I eventually do pick up SQLAlchemy (or go back to Mongoose/similar), I'll understand what it's actually doing for me, rather than treating it as magic. I'll recognize "oh, this ORM is just doing the connection/cursor dance I already know, behind a nicer interface"

## DRY

- common software principle sometimes called "don't repeat yourself" (DRY)
- implemented with get_connection fx that every route calls

## DB Schema

- Schema changes get more expensive over time aka once I have real data in a table, changing its structure means migrating existing rows so its best to spend time planning schema in advance
- design decision tradeoffs:
  - **Approach #1 (my initial thought process): storing todays_completion_status inside the habits table**
    - pro: simple, fast reads because no counting/looping through rows, streak is just sitting right there as a column
    - pro/con: less data stored; not storing individual completion records over time so no historical data (but do i need that or is it just taking up storage?)
    - con: can only store one status at a time, will need to be cleared every day?
  - **Approach #2 (what I ultimately went with): separate habits table and completion history table**
    - pro: stores history/every date that a habit was completed (creates a new row)
    - pro: scales better since a habit can have multiple completions and I can choose to display them all via a calendar view or something later on if I build a FE
    - con: slightly more complex queries involving checking two tables via JOIN to answer qs like longest streak, current streak etc

## Approach #2 Schema design / data modeling notes

- users table (must create this table first so habit table can reference it; will only hold one row aka me for now)
  - user_id INT PRIMARY KEY GENERATED ALWAYS AS IDENTITY -> postgres auto generates/populates
  - username VARCHAR(50) NOT NULL UNIQUE
  - password_hash VARCHAR(255) NOT NULL
- habits table
  - habit_id INT PRIMARY KEY GENERATED ALWAYS AS IDENTITY
  - content TEXT NOT NULL
  - date_created DATE DEFAULT CURRENT_DATE -----> auto populates; user does not need to enter
  - user_id INT NOT NULL FOREIGN KEY
- completions table
  - habit_id INT NOT NULL FOREIGN KEY
  - completion_date DATE DEFAULT CURRENT_DATE

## Browser Dev Tools

- fetch(): built in js fx provided by the browser that is specifically designed for making HTTP reqs

## Command line/Postgres

- start server: `uvicorn main:app --reload`

- connect to postgres server, specifically pointed to postgres db:
  `psql postgres
`

- switch to diff db:
  `\c {db_name}`

- see a list of tables in the db: `\dt`

- When psql shows -# instead of =#, it means it's waiting for more lines/statements
- `quit` or `\q` to exit out of psql completely
- `Ctrl+C` to quit out of writing a statement and go back to a fresh prompt =#
- regenerate requirements.txt to capture all newly installed dependencies: `pip3 freeze > requirements.txt`
- generate a secret key as a one off command in terminal: `pip3 freeze > requirements.txt`
