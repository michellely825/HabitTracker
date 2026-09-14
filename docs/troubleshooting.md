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
- pytest not being able to locate my auth.py file to import the fx I am trying to test
  - error msg: `ImportError while importing test module '/Users/michellely/Desktop/habit_tracker/tests/test_auth.py'.  ModuleNotFoundError: No module named 'auth'`
  - why? bc pytest does't know where my home/root dir is
  - AI initially recommended to fix by creating an empty conftest.py file which essentially tells pytest where the root dir is
  - I pushed back because I didn't like the idea of having an empty file to clutter up my root dir since it seems like a waste of space and so I asked for alt options
  - AI suggested instead of running `pytest` to use `python3 -m pytest` which runs pytest as a module via python itself and tells pytest directly where my project root is (still don't fullyyy understand this well but it worked..lol)
