# Project Takeaways & Lessons Learned

My brain dump of conceptual thoughts, software principles I attempted to apply and lessons learned during development

## Historical vs. mutable data

**Context:** Completions table rows represent historical facts (e.g., "this habit was completed on this date") - they should only ever be inserted or deleted, never updated, since mutating a historical record risks losing information that can't be recovered.

**Design question:** If a user deletes a habit, should that cascade-delete its completion history or should the habit be soft-deleted instead (preserving history)?

**Decision:** Soft-delete via an `is_active` flag on `habits`. When a user "deletes" a habit, `is_active` is set to `False` rather than removing the row - this preserves the habit's full completion history rather than losing it to a cascade delete.

**Confirm with Victor:** whether `is_active`-based soft delete is the right approach here or if there's a more standard pattern for this kind of historical-data preservation.

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

- SQL
  - if it's a SELECT: result = cursor.fetchone() or fetchall()
  - if it's an INSERT/UPDATE/DELETE: conn.commit()

## Software Engineering Principles

- DRY
  - don't repeat yourself
  - implemented with get_connection fx that every route calls to create a connection with db

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

## Next steps?

- [x] set up my DB
- [x] create user table first
- [x] validate schema design in psql terminal by inserting new users into table, making sure ids auto generate, usernames have to be unique etc.
- [x] test python to postgres connection via POST/users
- [x] create habits table
- [x] validate check habits schema in psql terminal
- [x] set up password hashing via bcrypt
- [x] pytest for password hashing
- [] set up JWT auth?
- []
