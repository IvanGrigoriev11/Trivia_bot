import json
from typing import Dict, List

import requests
import typer


def request_token() -> str:
    """Get session_token from OpenTrivia API.

    Returns:
        session_token (str): a unique key which helps to keep track of the question the API has already retrieved.
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
        print("the process is running")
        return json.loads(response.text)["results"]
    else:
        termination_reason = {
            1: "No results",
            2: "Invalid parameter",
            3: "Token not found",
            4: "Token Empty",
        }.get(code, f"Unknown. Code = {code}")
        print(termination_reason)
        return []


def show_max_number(all_questions: List[Dict]) -> int:
    """Counts the max number of questions to download from OpenTrivia API."""

    max_number = len(all_questions)
    return max_number


def main():
    session_token = request_token()
    all_questions = []
    while True:
        questions = get_questions(session_token)
        if questions:
            all_questions.extend(questions)
        else:
            typer.echo(show_max_number(all_questions))
            break

    with open("questions.json", "w") as f:
        f.write(json.dumps(all_questions))


if __name__ == "__main__":
    typer.run(main)
