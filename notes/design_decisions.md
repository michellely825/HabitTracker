## Design Decisions/Tradeoffs

- Checking uniqueness of username
  - Options
    - Approach #1: Check first, then insert (what I originally was thinking)
      - Query: "does a user with this username already exist?"
      - If yes → return an error, stop here
      - If no → proceed to insert the new user
    - Approach 2: Just try to insert, and catch the failure
      - Attempt the insert directly
      - If the UNIQUE constraint on the DB rejects it (throws an error), catch that error in your code and translate it into a friendly "username already taken" response
      - If it succeeds, great — no separate check needed
  - intuitively Approach 1 made more sense to me logically **ask Victor**
  - But AI said Approach 2 is actually often preferred in real systems, because Approach 1 has a subtle flaw: between my "check" and my "insert," a tiny window exists where another request could sneak in and create that same username — so relying only on the check isn't always airtight. The database's UNIQUE constraint is the actual, guaranteed source of truth; your own check-first query is more of a nicety for a faster/friendlier error, not a substitute for it.
  - design question: how does user_id get into a habit creation request
    - Option A: Client sends user_id directly in the request body -> security issues & potential issue of saving habit to wrong user
    - Option B: Server determines user_id from authentication (e.g., a JWT token), not from the request body at all
