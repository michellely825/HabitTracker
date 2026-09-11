import psycopg2


# creates a fresh connection to postgres DB everytime it is called
def get_connection():
    return psycopg2.connect(host="localhost", dbname="habit_tracker", user="michellely")
