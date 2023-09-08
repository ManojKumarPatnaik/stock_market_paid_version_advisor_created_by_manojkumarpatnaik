import requests

def test_flask_app(prompt):
    url = 'http://localhost:5000/api/compare'
    input_data = {
        "model": "gpt-35-turbo",
        "messages": [
            {
                "role": "assistant",
                "content": prompt
            }
        ],
        "max_tokens": 2000
    }
    response = requests.post(url, json=input_data)
    assert response.status_code == 200
    print(response.json())

if __name__ == "__main__":
    prompt = "Many countries in the world?"
    test_flask_app(prompt)


# if __name__ == "__main__":
#     input_prompt = "Many countries in the world?"
#     example(input_prompt)