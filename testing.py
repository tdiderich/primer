import requests
import os

PRIMER_API_KEY = os.getenv('PRIMER_API_KEY')

def main():
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {PRIMER_API_KEY}'
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
