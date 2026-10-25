import psycopg2
from schemas import HabitCreate
from fastapi import APIRouter, HTTPException, Request
from database import get_connection
from typing import Optional
from auth import extract_token_from_header, verify_token, ensure_habit_valid

router = APIRouter()


# TODO: update HTTP date from GMT to PST
@router.post("/habits", status_code=201)
def create_habit(habit: HabitCreate, request: Request):
    content = habit.content
    token = extract_token_from_header(request)

    decoded_payload = verify_token(token)
    user_id = decoded_payload["user_id"]

    conn = get_connection()
    cursor = conn.cursor()

    try:
        cursor.execute(
            "INSERT INTO habits (content, user_id) VALUES (%s, %s) RETURNING habit_id;",
            (content, user_id),
        )
        habit_id = cursor.fetchone()[0]  # returns first tuple val
        conn.commit()
        return {"message": "Habit successfully created!", "habit_id": habit_id}
    except psycopg2.Error as e:
        raise HTTPException(
            status_code=500, detail="Unable to create new habit due to database error"
        )
    finally:
        cursor.close()
        conn.close()


@router.get("/habits", status_code=200)
def get_habits(
    request: Request, status: Optional[str] = None
):  # status - optional query param after '?' in URL
    token = extract_token_from_header(request)
    decoded_payload = verify_token(token)
    user_id = decoded_payload["user_id"]

    conn = get_connection()
    cursor = conn.cursor()

    try:
        if status == "complete":
            cursor.execute(
                "SELECT * FROM habits INNER JOIN completions ON habits.habit_id = completions.habit_id WHERE habits.user_id = %s AND habits.is_active = true AND completions.completion_date = CURRENT_DATE;",
                (user_id,),
            )
        elif status == "incomplete":
            cursor.execute(
                "SELECT * FROM habits LEFT JOIN completions ON habits.habit_id = completions.habit_id AND completions.completion_date = CURRENT_DATE WHERE habits.user_id = %s AND habits.is_active = true AND completions.completion_id is NULL;",
                (user_id,),
            )
        else:
            cursor.execute(
                "SELECT * FROM habits WHERE user_id = %s AND is_active = TRUE;",
                (user_id,),
            )

        habits = cursor.fetchall()
        return habits
    except psycopg2.Error as e:
        raise HTTPException(
            status_code=500, detail="Unable to get habits due to database error"
        )
    finally:
        cursor.close()
        conn.close()


@router.post("/habits/{habit_id}/complete", status_code=201)
# habit_id is a path param in the URL
def mark_habit_complete(habit_id: int, request: Request):
    token = extract_token_from_header(request)
    user_id = verify_token(token)["user_id"]  # verify token before proceeding

    conn = get_connection()
    cursor = conn.cursor()
    try:
        ensure_habit_valid(cursor, user_id, habit_id)
        cursor.execute(
            "INSERT INTO completions (habit_id) VALUES (%s) RETURNING completion_id;",
            (habit_id,),
        )
        conn.commit()
        return {"message": f"Habit id#{habit_id} has been marked as completed"}
    except (
        psycopg2.errors.UniqueViolation
    ) as e:  # enforced by UNIQUE (habit_id, completion_date) constraint in schema
        conn.rollback()  # resets the connection after the failed insertion
        print(f"Habit id#{habit_id} has already been marked as complete - no-op")
        return {"message": f"Habit id#{habit_id} marked complete"}
    except psycopg2.Error as e:
        raise HTTPException(
            status_code=500,
            detail="Unable to mark habit complete due to database error",
        )
    finally:
        cursor.close()
        conn.close()


# deletes the specified habit's completion row for current date
# no-op if state is already correct (e.g. calling the fx twice in a row on same habit)
@router.delete("/habits/{habit_id}/complete")
def mark_habit_incomplete(habit_id: int, request: Request):
    token = extract_token_from_header(request)
    user_id = verify_token(token)["user_id"]

    conn = get_connection()
    cursor = conn.cursor()

    try:
        ensure_habit_valid(cursor, user_id, habit_id)
        cursor.execute(
            "DELETE FROM completions WHERE habit_id = %s AND completion_date = CURRENT_DATE;",
            (habit_id,),
        )
        conn.commit()
        if cursor.rowcount == 0:
            print(f"Habit #id{habit_id} has not been completed yet today - no-op")
        return {"message": f"Habit id#{habit_id} marked incomplete"}
    except psycopg2.Error as e:
        raise HTTPException(
            status_code=500,
            detail="Unable to mark habit incomplete due to database error",
        )
    finally:
        cursor.close()
        conn.close()


@router.patch("/habits/{habit_id}")
def soft_delete_habit(habit_id: int, request: Request):
    token = extract_token_from_header(request)
    user_id = verify_token(token)["user_id"]

    conn = get_connection()
    cursor = conn.cursor()

    try:
        ensure_habit_valid(cursor, user_id, habit_id)
        cursor.execute(
            "UPDATE habits SET is_active = FALSE WHERE habit_id = %s AND is_active = TRUE;",
            (habit_id,),
        )
        conn.commit()
        # TODO: rethink
        if cursor.rowcount == 0:
            return {
                "message": f"Nothing to delete. Habit #id{habit_id} has already been deleted."
            }
        return {"message": f"Habit id#{habit_id} was deleted."}
    except psycopg2.Error as e:
        raise HTTPException(
            status_code=500, detail="Unable to delete habit due to database error"
        )
    finally:
        cursor.close()
        conn.close()


# TODO: reactivate a deleted habit
