import json
import os
from dataclasses import dataclass

import html2text
import psycopg
import typer


@dataclass()
class Common:
    dbname: str
    host: str
    port: int
    file: str


def connect(
    ctx: typer.Context,
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
    file: str = typer.Option(
        "questions.json",
        help="Type the name of the file which you want to populate to the database.",
    ),
):
    """Connects to the selected database."""

    ctx.obj = Common(dbname, host, port, file)

    user = os.environ["TRIVIA_POSTGRES_USER"]
    password = os.environ["TRIVIA_POSTGRES_PASSWD"]

    # pylint: disable = not-context-manager
    with psycopg.connect(
        host=host, dbname=dbname, user=user, password=password, port=port
    ) as conn:

        print("Connection is set up")
        create(conn, ctx.obj.file)
    print("Connection was closed")


def create(conn, file):
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
                FOREIGN KEY (question_id) REFERENCES questions(id) 
                )
            """
        )
        with open(file, encoding="utf-8") as f:
            all_questions = json.load(f)

        for index, question in enumerate(all_questions):
            question["question"] = html2text.html2text(
                f"{question['question']}"
            ).strip()
            cur.execute(
                "INSERT INTO questions (id, category, type, difficulty, question)"
                "VALUES (%s, %s, %s, %s, %s) RETURNING id;",
                (
                    index + 1,
                    f"{question['category']}",
                    f"{question['type']}",
                    f"{question['difficulty']}",
                    f"{question['question']}",
                ),
            )
            question_id = cur.fetchone()[0]
            for answer in range(len(question["incorrect_answers"])):
                cur.execute(
                    "INSERT INTO answers (question_id, text, is_correct)"
                    "VALUES (%s, %s, %s)",
                    (
                        question_id,
                        f"{question['incorrect_answers'][answer]}",
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
        count_rows_in_table(cur, "questions")
        count_rows_in_table(cur, "answers")


def count_rows_in_table(cur, table_name: str):
    """Counts rows in the selected table."""

    cur.execute(
        f"""
        SELECT COUNT (*) FROM {table_name};
        """
    )
    print(f"{table_name} in the database: {cur.fetchone()[0]}")


if __name__ == "__main__":
    typer.run(connect)
