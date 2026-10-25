import psycopg2


# creates a fresh connection to postgres DB everytime it is called
# raises an exception if connection fails
def get_connection():
    return psycopg2.connect(host="localhost", dbname="habit_tracker", user="michellely")
