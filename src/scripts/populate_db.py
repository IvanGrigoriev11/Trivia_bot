import json
import os
from pathlib import Path

import html2text
import psycopg
import typer
from psycopg import Cursor


def populated_db(
    dbname: str = typer.Argument(..., help="Database name"),
    host: str = typer.Option("localhost", help="Database host"),
    port: int = typer.Option(5432, help="Database port"),
    questions_file: Path = typer.Option(
        "questions.json", help="Questions file used to populate the database."
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
        _create(conn.cursor(), questions_file)
    print("Connection was closed")


def _create(cur: Cursor, questions_fpath: Path):
    """Creates 'questions' and 'answers' tables in the selected database."""

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
    with open(questions_fpath, encoding="utf-8") as f:
        all_questions = json.load(f)

    for index, question in enumerate(all_questions):
        # convert a question of HTML into clean, easy-to-read plain ASCII text
        cleaned_question = html2text.html2text(f"{question['question']}").strip()
        cur.execute(
            "INSERT INTO questions (id, category, type, difficulty, question)"
            "VALUES (%s, %s, %s, %s, %s) RETURNING id;",
            (
                index + 1,
                f"{question['category']}",
                f"{question['type']}",
                f"{question['difficulty']}",
                f"{cleaned_question}",
            ),
        )
        question_row = cur.fetchone()
        if question_row is not None:
            question_id = question_row[0]
            # pylint: disable = reportGeneralTypeIssues
            answers = [(a, False) for a in question["incorrect_answers"]] + [
                (question["correct_answer"], True)
            ]
            for text, answer in answers:
                cur.execute(
                    "INSERT INTO answers (question_id, text, is_correct)"
                    "VALUES (%s, %s, %s)",
                    (
                        question_id,
                        f"{text}",
                        f"{answer}",
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
    row = cur.fetchone()
    if row is not None:
        print(f"Number of entries in {table_name} table: {row[0]}")


if __name__ == "__main__":
    typer.run(populated_db)
