from dataclasses import dataclass
from typing import List, Optional

import requests
import typer

QUESTIONS = []


@dataclass
class ScrapperState:
    session_token: str
    is_finished: bool


def request_token() -> str:
    """Get token from OpenTrivia API"""

    response = requests.post("https://opentdb.com/api_token.php?command=request")
    assert (
        response.status_code == 200
    ), f"Expected status code 0 but got {response.status_code}"
    session_token = response.json()["token"]
    return session_token


def download_questions(session_token: str, first_launch: bool) -> ScrapperState:
    """Download the database of questions from OpenTriviaDB"""

    package_of_questions = requests.post(
        f"https://opentdb.com/api.php?amount=50&token={session_token}"
    )
    assert (
        package_of_questions.status_code == 200
    ), f"Expected status code 0 but got {package_of_questions.status_code}"
    data = package_of_questions.text
    code = package_of_questions.json()["response_code"]

    if code == 0:
        if first_launch:
            QUESTIONS.append(f"[{data}")

        QUESTIONS.append(f",{data}")
        print("the process is running")
        return ScrapperState(session_token, False)
    elif code == 1:
        print("No Results")
    elif code == 2:
        print("Invalid Parameter")
    elif code == 3:
        print("Token Not Found")

    QUESTIONS.append(f"]")
    record_data(QUESTIONS)
    reset_token_session(session_token)
    return ScrapperState(session_token, True)


def reset_token_session(session_token: str):
    """Reset token which will wipe story about last connection with API"""

    requests.post(
        f"https://opentdb.com/api_token.php?command=reset&token={session_token}"
    )
    QUESTIONS.clear()
    print("The session was reset!")


def record_data(data: List[str]):
    """Save all recorded data into file"""

    with open("questions.json", mode="w") as result:
        for item in data:
            result.write(item)
    print("All information was recorded")


def main():
    max_number = 0
    session = download_questions(request_token(), True)
    while session.is_finished is not True:
        max_number += 1
        session = download_questions(session.session_token, False)
    else:
        print(f"the max number of the questions is: {max_number*50}")


if __name__ == "__main__":
    typer.run(main)
