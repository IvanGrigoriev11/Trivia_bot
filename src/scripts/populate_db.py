import json
import os

import psycopg
import typer

DB_NAME = "postgres"


def main(
    dbname: str = typer.Argument(
        ..., help="The name of the database which you are calling"
    ),
    host: str = typer.Option(
        "localhost",
        help="Enter host IP. ",
    ),
    port: int = typer.Option(
        5432,
        help="Type the number of port. 5432 is set by default.",
    ),
):
    """Creates 'questions' and 'answers' tables in the selected database."""

    if dbname == DB_NAME:
        user = os.environ["USER_FOR_DATABASE"]
        password = os.environ["PASSWORD_FOR_DB"]

        # Connect to an existing database
        with psycopg.connect(
            host=host, dbname=dbname, user=user, password=password, port=port
        ) as conn:

            print("Connection is set up")
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

                for index, question in enumerate(all_questions):
                    cur.execute(
                        "INSERT INTO questions (id, category, type, difficulty, question)"
                        "VALUES (%s, %s, %s, %s, %s)",
                        (
                            index + 1,
                            f"{question['category']}",
                            f"{question['type']}",
                            f"{question['difficulty']}",
                            f"{question['question']}",
                        ),
                    )
                    cur.execute(
                        "INSERT INTO answers (question_id, correct_answer, incorrect_answers)"
                        "VALUES (%s, %s, %s)",
                        (
                            index + 1,
                            f"{question['correct_answer']}",
                            f"{question['incorrect_answers']}",
                        ),
                    )
                print("'questions' and 'answers' tables were created")
                cur.execute(
                    """
                    SELECT COUNT (*) FROM questions;
                    """
                )
                print(f"Questions in the database: {cur.fetchone()}")
            print("Connection was closed")
    else:
        print("Database not found")


if __name__ == "__main__":
    typer.run(main)
