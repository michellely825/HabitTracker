## Quick Definitions

**FastAPI** = framework for building APIs (similar to Express in Node)

**framework** = provides structural skeleton, handles routes, logic (calls my code for me when an endpoint is requested) and architecture

**Uvicorn** = runs the server and listens on specified port (similar to Node.js)

**schema** = defines db organization, how tables relate and what rules the data must follow

**psycopg2** = library that allows python to talk to postgreSQL db

## Project Overview

Habit tracker

- for now supports a single use (aka myself) but can/will eventually support multiple users
- a user can:
  - create a user account
  - add a new habit
  - see all their habits
  - see a habit's current streak (could be <= longest streak)
  - see a habit's longest streak
  - mark a habit as completed for the day
  - unmark a habit
  - delete a habit
- a user can not:
  - update contents of a habit -> bc if they could, it would cause problems later on when calculating streaks?
  - access/update other user's habits

## Use Cases

### Add a new habit:

**main flow**

1. User sends a POST/habits request to create a new habit by supplying content
2. BE validates the request, ensuring content is not empty or null (could it be null?)
3. BE saves the new habit into DB, associated with the user
4. BE returns the newly created habit as a habit_id and date_created

**error/edge cases**

- what happens if habit content is invalid (e.g. empty or null) -> return an error (e.g. "missing habit content") instead of saving a blank habit
- what if the habit content is really long? -> DB restricts content limit via VARCHAR(255)
- what if DB fails to write (e.g. network issues etc) -> return an error (e.g. "Network issue, please try again later") instead of silently pretending it worked
- saving habit to wrong user due to missing token/invalid token? -> BE should reject request
- can user create two habits with same content? -> no, DB requires habits to be unique

### See all habits

**main flow**

1. User sends a GET/habits request along with token that has user id, user also specifies if they want to see complete habits only, incomplete habits only or both
2. BE filters DB for user specific habits
3. BE returns list of habits which will include their habit_id, content, date_created

**errors/edge cases**

- missing token/invalid token? -> return an error
- missing habit type filter (complete only, incomplete only etc) -> return all habits
- invalid habit type filter -> reject with an error
- network issues -> return an error instead of silently pretending it worked
- BE returns all habits regardless of user -> issue with querying the DB or potentially issue with the way habits are getting saved
- what happens if user has thousands of habits? -> implement pagination so that not all of them are returned at once?
- what happens if user has no habits? -> return empty list

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

## What can go wrong when...

- creating a new user
  - username is not unique -> this is enforced by the db schema via UNIQUE
  - manually include the user_id -> enforced by schema via "GENERATED ALWAYS AS IDENTITY" which makes postgres auto generate it and also spits out an error if we try to override/provide a user_id
- creating a habit:
  - habit doesn't get saved properly to db bc of network errors? db errors?
  - new habit is missing required fields so shouldn't be saved
-

## AI Usage

- recommended me to use ORM; rather than just defaulting to use what it suggested I asked it wto list what the tradeoffs were
  - ORM (e.g., SQLAlchemy): less boilerplate, built-in SQL injection protection, easier migrations but hides the actual SQL, adds a new abstraction to learn, and can generate inefficient queries I don't immediately see
  - Raw SQL (e.g., psycopg2): full transparency into exactly what queries run, reinforces SQL skills directly, no new abstraction to learn but more manual work per query, manual connection handling, and no automatic migration tooling
- Decision: decided to go with raw SQL because I want to practice writing queries and know exactly what's happening

## Next steps?

- set up my DB
- think through table schema
- create user table first
- sanity check/validate schema design in psql terminal by inserting new users into table; making sure ids auto generate, usernames have to be unique etc.
- then test python to postgres connection

## DB Schema

- Schema changes get more expensive over time aka once I have real data in a table, changing its structure means migrating existing rows so its best to spend time planning schema in advance
- design decision tradeoffs:
  - **Approach #1 (my initial thought process): storing todays_completion_status inside the habits table**
    - pro: simple, fast reads because no counting/looping through rows, streak is just sitting right there as a column
    - pro/con: less data stored; not storing individual completion records over time so no historical data (but do i need that or is it just taking up storage?)
    - con: can only store one status at a time, will need to be cleared every day?
  - **Approach #2: separate habits table and completion history table**
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
