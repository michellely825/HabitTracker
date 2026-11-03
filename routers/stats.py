import psycopg2
from database import get_connection
from auth import extract_token_from_header, verify_token, ensure_habit_valid
from fastapi import APIRouter, HTTPException, Request
from pprint import pprint  # formats dicts/lists prettier in server terminal
from datetime import timedelta

router = APIRouter()


@router.get("/habits/{habit_id}/stats", status_code=200)
def get_stats(habit_id: int, request: Request):
    token = extract_token_from_header(request)
    user_id = verify_token(token)["user_id"]

    conn = get_connection()
    cursor = conn.cursor()

    try:
        ensure_habit_valid(cursor, user_id, habit_id)
        cursor.execute(
            "SELECT * FROM completions WHERE habit_id = %s ORDER BY completion_date ASC;",
            (habit_id,),
        )
        completions = cursor.fetchall()
        current_streak, best_streak = calculate_streaks(completions)

        return {
            "message": f"Current streak: {current_streak}, Best streak: {best_streak}"
        }
    except psycopg2.Error as e:
        raise HTTPException(
            status_code=500, detail="Unable to get habit stats due to database error"
        )
    finally:
        cursor.close()
        conn.close()


def calculate_streaks(completions: list[tuple]) -> tuple[int, int]:
    if not completions:  # empty list -> habit has never been completed
        return (0, 0)

    # habit has been completed at least once so current & best streak are at minimum 1
    current_streak = 1
    best_streak = 1

    for i in range(1, len(completions)):
        if completions[i][2] - completions[i - 1][2] == timedelta(days=1):
            current_streak += 1
        else:
            best_streak = max(best_streak, current_streak)
            current_streak = 1  # reset streak

    # handles edge case where there is no gap - final check to see if ending current streak is highest overall
    best_streak = max(best_streak, current_streak)
    return (current_streak, best_streak)
