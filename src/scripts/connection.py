import json
import os

import psycopg
import typer

DB_NAME = "postgres"
FETCH_All = "all"
FETCH_ONE = "one"

app = typer.Typer()


@app.command()
def create(
    dbname: str = typer.Argument(
        ..., help="The name of the database which you are calling"
    ),
    host: str = typer.Option(
        "localhost",
        help="""
            Enter host IP. If you skip this parameter, the localhost to be chosen automatically.
            """,
    ),
    port: int = typer.Option(
        5432,
        help="""
            Type the number of port. 5432 is set by default.
            """,
    ),
):
    """The command allows to create 'questions' and 'answers' tables in the selected database."""

    if dbname == DB_NAME:
        user = os.environ["USER_FOR_DATABASE"]
        password = os.environ["PASSWORD_FOR_DB"]

        # Connect to an existing database
        with psycopg.connect(
            host=host, dbname=dbname, user=user, password=password, port=port
        ) as conn:

            # Open a cursor to perform database operations
            with conn.cursor() as cur:
                # Execute a command: this creates a new table
                cur.execute(
                    """
                            CREATE TABLE IF NOT EXISTS questions (
                                id serial PRIMARY KEY,
                                category text,
                                type text,
                                difficulty text,
                                question text
                                )
                            """
                )
                print("The connection is set up")

                # Execute a command: this creates a new table
                cur.execute(
                    """
                            CREATE TABLE IF NOT EXISTS questions (
                                id serial PRIMARY KEY,
                                category text,
                                type text,
                                difficulty text,
                                question text
                                )
                            """
                )

                cur.execute(
                    """
                            CREATE TABLE IF NOT EXISTS answers (
                                question_id serial PRIMARY KEY,
                                correct_answer text,
                                incorrect_answers text
                                )
                            """
                )
                with open("questions.json", mode="r") as my_file:
                    all_questions = json.loads(my_file.read())

                for i in range(len(all_questions)):
                    cur.execute(
                        "INSERT INTO questions (id, category, type, difficulty, question) VALUES (%s, %s, %s, %s, %s)",
                        (
                            i + 1,
                            f"{all_questions[i]['category']}",
                            f"{all_questions[i]['type']}",
                            f"{all_questions[i]['difficulty']}",
                            f"{all_questions[i]['question']}",
                        ),
                    )
                    cur.execute(
                        "INSERT INTO answers (question_id, correct_answer, incorrect_answers) VALUES (%s, %s, %s)",
                        (
                            i + 1,
                            f"{all_questions[i]['correct_answer']}",
                            f"{all_questions[i]['incorrect_answers']}",
                        ),
                    )
                print("'questions' and 'answers' tables were created")
    else:
        print("Database not found")


@app.command()
def delete(
    table: str = typer.Argument(
        ..., help="The name of the table which you want to delete"
    ),
    dbname: str = typer.Argument(
        ..., help="The name of the database which you are calling"
    ),
    host: str = typer.Option(
        "localhost",
        help="""
            Enter host IP. If you skip this parameter, the localhost to be chosen automatically.
            """,
    ),
    port: int = typer.Option(
        5432,
        help="""
            Type the number of port. 5432 is set by default.
            """,
    ),
):
    """Delete selected tables from the database"""

    if dbname == DB_NAME:
        user = os.environ["USER_FOR_DATABASE"]
        password = os.environ["PASSWORD_FOR_DB"]

        # Connect to an existing database
        with psycopg.connect(
            host=host, dbname=dbname, user=user, password=password, port=port
        ) as conn:

            with conn.cursor() as cur:
                cur.execute(f"DELETE FROM {table};")
                print(f"{table} was deleted")
    else:
        print("Database not found")


@app.command()
def select(
    table: str = typer.Argument(
        ..., help="The name of the table which you want to open"
    ),
    dbname: str = typer.Argument(
        ..., help="The name of the database which you are calling"
    ),
    fetch: str = typer.Option(
        "all",
        help="""
        Choose how much data you want to retrieve from the table with the query. If you skip this parameter,
        all data is shown. 
        """,
    ),
    host: str = typer.Option(
        "localhost",
        help="""
        Enter host IP. If you skip this parameter, the localhost to be chosen automatically.
        """,
    ),
    port: int = typer.Option(
        5432,
        help="""
        Type the number of port. 5432 is set by default.
        """,
    ),
):
    """Check table content"""

    if dbname == DB_NAME:
        user = os.environ["USER_FOR_DATABASE"]
        password = os.environ["PASSWORD_FOR_DB"]

        # Connect to an existing database
        with psycopg.connect(
            host=host, dbname=dbname, user=user, password=password, port=port
        ) as conn:

            with conn.cursor() as cur:
                cur.execute(f"SELECT * FROM {table}")
                if fetch == FETCH_ONE:
                    print(cur.fetchone())
                else:
                    print(cur.fetchall())
    else:
        print("Database not found")


if __name__ == "__main__":
    app()
