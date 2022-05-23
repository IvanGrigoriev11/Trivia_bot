import requests


def initial_request() -> str:
    data = requests.post("https://opentdb.com/api_token.php?command=request")
    token = data.json()['token']

    assert data.status_code == 200, f"Expected status code 0 but got {data.status_code}"
    print(data.json()['response_message'])
    return token


def scraping_process(token_for_session: str, first_step: bool) -> str:
    package_of_questions = requests.post(f"https://opentdb.com/api.php?amount=50&token={token_for_session}")
    data = package_of_questions.text
    code = package_of_questions.json()['response_code']
    assert package_of_questions.status_code == 200, f"Expected status code 0 but got {package_of_questions.status_code}"

    if code == 0:
        if first_step:
            recording_data(f"[{data}")

        recording_data(f",{data}")
        print("the process is running")
    elif code == 1:
        print("No Results")
    elif code == 2:
        print("Invalid Parameter")
    elif code == 3:
        print("Token Not Found")
    else:
        reset_token_session(token_for_session)
        recording_data("]")
        return "Token Empty"
    return token_for_session


def reset_token_session(token_for_session: str):
    requests.post(f"https://opentdb.com/api_token.php?command=reset&token={token_for_session}")
    print("All jobs were done!")


def recording_data(data: str):
    with open('questions.json', mode='a') as result:
        result.write(data)


def main():
    token_for_session = scraping_process(initial_request(), True)
    while scraping_process(token_for_session, False) != "Token Empty":
        continue


if __name__ == "__main__":
    main()
