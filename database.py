import psycopg2


def get_connection():
    return psycopg2.connect(host="localhost", dbname="habit_tracker", user="michellely")
