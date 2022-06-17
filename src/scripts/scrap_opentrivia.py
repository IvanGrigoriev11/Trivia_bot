import json
from typing import Dict, List, Optional

import requests
import typer


def request_token() -> str:
    """
    Returns a new session token for OpenTrivia API.
    The token is used for tracking the set of returned questions and to avoid getting duplicates.
    """

    response = requests.post("https://opentdb.com/api_token.php?command=request")
    assert response.status_code == 200, f"Unexpected status code {response.status_code}"
    session_token = response.json()["token"]
    return session_token


def get_questions(session_token: str) -> List[Dict]:
    """Download the database of questions from OpenTriviaDB."""

    response = requests.post(
        f"https://opentdb.com/api.php?amount=50&token={session_token}"
    )
    code = response.json()["response_code"]
    if code == 0:
        return json.loads(response.text)["results"]
    termination_reason = {
        1: "No results",
        2: "Invalid parameter",
        3: "Token not found",
        4: "Token Empty",
    }.get(code, f"Unknown. Code = {code}")
    print(termination_reason)
    return []


def main(
    max_questions: Optional[int] = typer.Option(
        None,
        help="""
        Puts a limit on the number of questions to be downloaded. If not set, the script will download all questions.
        """,
    )
):
    session_token = request_token()
    all_questions = []
    while True:
        questions = get_questions(session_token)
        if questions:
            all_questions.extend(questions)
            print(f"Downloaded {len(all_questions)} questions")
        else:
            break

        if max_questions and max_questions <= len(all_questions):
            break

    with open("questions.json", "w", encoding="utf-8") as f:
        f.write(json.dumps(all_questions))

    print("All finished")


if __name__ == "__main__":
    typer.run(main)
