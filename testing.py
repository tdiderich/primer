import requests


def main():
    headers = {
        'Content-Type': 'application/json',
        'Authorization': 'Bearer Jkan5rpruBkmDajv_lll7beQ8xzhgzIM2gB7rhl_WZc'
    }

    emails = [
        'dude, what are you doing',
        'I really appreciate it',
        'I am not sure if this is working out as expected',
        'Thanks for all the help!'
    ]

    for email in emails:


        response = requests.post(
            url='https://engines.primer.ai/api/v1/classify/sentiment',
            headers=headers,
            json={'text': email}
        )

        print(f'--- TEXT ---')
        print(email)
        print(f'--- RESPONSE ---')
        print(response.json())


if __name__ == '__main__':
    main()
