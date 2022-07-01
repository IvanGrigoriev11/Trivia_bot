import json
import os

import html2text
import psycopg
import typer
from psycopg import Connection, Cursor


def populated_db(
    dbname: str = typer.Argument(..., help="Database name"),
    host: str = typer.Option("localhost", help="Database host"),
    port: int = typer.Option(5432, help="Database port"),
    questions_file: str = typer.Option(
        "questions.json", help="Questions file used to populate to the database"
    ),
):
    """Populates data from question_file to the selected database."""

    user = os.environ["TRIVIA_POSTGRES_USER"]
    password = os.environ["TRIVIA_POSTGRES_PASSWD"]

    # pylint: disable = not-context-manager
    with psycopg.connect(
        host=host, dbname=dbname, user=user, password=password, port=port
    ) as conn:
        print("Connection is set up")
        _create(conn, questions_file)
    print("Connection was closed")


def _create(conn: Connection, file: str):
    """Creates 'questions' and 'answers' tables in the selected database."""

    # Open a cursor to perform database operations
    with conn.cursor() as cur:
        # Execute a command: this creates a new table
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS questions (
                id integer PRIMARY KEY,
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
                question_id integer,
                text text,
                is_correct bool,
                FOREIGN KEY (question_id) REFERENCES questions(id))
            """
        )
        with open(file, encoding="utf-8") as f:
            all_questions = json.load(f)

        for index, question in enumerate(all_questions):
            modified_question = html2text.html2text(f"{question['question']}").strip()
            cur.execute(
                "INSERT INTO questions (id, category, type, difficulty, question)"
                "VALUES (%s, %s, %s, %s, %s) RETURNING id;",
                (
                    index + 1,
                    f"{question['category']}",
                    f"{question['type']}",
                    f"{question['difficulty']}",
                    f"{modified_question}",
                ),
            )
            question_id = cur.fetchone()[0]
            for answer in question["incorrect_answers"]:
                cur.execute(
                    "INSERT INTO answers (question_id, text, is_correct)"
                    "VALUES (%s, %s, %s)",
                    (
                        question_id,
                        f"{answer}",
                        False,
                    ),
                )
            cur.execute(
                "INSERT INTO answers (question_id, text, is_correct)"
                "VALUES (%s, %s, %s)",
                (
                    question_id,
                    question["correct_answer"],
                    True,
                ),
            )
        print("'questions' and 'answers' tables were created")
        _print_rows_in_table(cur, "questions")
        _print_rows_in_table(cur, "answers")


def _print_rows_in_table(cur: Cursor, table_name: str):
    """Counts rows in the selected table."""

    cur.execute(
        f"""
        SELECT COUNT (*) FROM {table_name};
        """
    )
    print(f"Number of entries in {table_name} table: {cur.fetchone()[0]}")


if __name__ == "__main__":
    typer.run(populated_db)
