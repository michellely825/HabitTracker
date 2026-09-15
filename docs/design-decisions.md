## Design Decisions/Tradeoffs

- how to check uniqueness of username
  - Options
    - A: Check first, then insert (what I originally was thinking)
      - Query: "does a user with this username already exist?"
      - If yes → return an error, stop here
      - If no → proceed to insert the new user
    - B: Just try to insert, and catch the failure
      - Attempt the insert directly
      - If the UNIQUE constraint on the DB rejects it (throws an error), catch that error in your code and translate it into a friendly "username already taken" response
      - If it succeeds, great — no separate check needed
  - Thought process
    - Intuitively Approach A made more sense to me logically **ask Victor**
    - But AI said Approach B is actually often preferred in real systems, because Approach A has a subtle flaw: between my "check" and my "insert," a tiny window exists where another request could sneak in and create that same username — so relying only on the check isn't always airtight. The database's UNIQUE constraint is the actual, guaranteed source of truth; your own check-first query is more of a nicety for a faster/friendlier error, not a substitute for it.
- how does user_id get into a POST/habits request
  - Options
    - A: Client sends user_id directly in the request body -> security issues & potential issue of saving habit to wrong user
    - B: Server determines user_id from authentication (e.g., a JWT token), not from the request body at all
  - Thought process
    - Approach B is slightly more work but safer security wise so I will go with that
- should password hashing remain in my POST/users route or should I move it into its own standalone fx outside of the route?
  - pros: easier unit testing (no need to involve server, DB, HTTP etc)
  - cons: requires creating new fx/new file
  - ultimately decided to create a new auth.py file which will store my security/auth related fxs: hash_password, verify_password, create_jwt etc
- to use an ORM or to not
  - AI recommended me to use an ORM; rather than just defaulting to use what AI suggested I asked AI to list what the tradeoffs were
  - ORM (e.g., SQLAlchemy): less boilerplate, built-in SQL injection protection, easier migrations but hides the actual SQL, adds a new abstraction to learn, and can generate inefficient queries I don't immediately see
  - Raw SQL (e.g., psycopg2): full transparency into exactly what queries run, reinforces SQL skills directly, no new abstraction to learn but more manual work per query, manual connection handling, and no automatic migration tooling
  - Decision: decided to go with raw SQL because I want to practice writing queries and know exactly what's happening; allows me to see the actual mechanics that every ORM is secretly doing on my behalf; understand why a connection and cursor are needed per-request; also this way makes learning an ORM later much faster bc once I eventually do pick up SQLAlchemy (or go back to Mongoose/similar), I'll understand what it's actually doing for me, rather than treating it as magic. I'll recognize "oh, this ORM is just doing the connection/cursor dance I already know, behind a nicer interface"

## Security

- CORS
  - Currently using `allow_origins=["*"]` for CORS since this is local-only
  - will replace with specific allowed origin(s) before any public deployment
- Auth feedback
  - Context: considered how specific my error messages should be. for instance, "username not found" or "incorrect password" vs something more generic like "incorrect credentials"
  - attacker attempting to break into an account can efficiently enumerate valid usernames first by trying many usernames, watching for which ones return "incorrect password" instead of "username not found" — since that tells them the username exists, just the password was wrong
  - a generic, identical error for both cases (e.g. "invalid username or password)
    - denies the attacker any information about which part was wrong, forcing them to always guess both pieces together, with no shortcuts.

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
