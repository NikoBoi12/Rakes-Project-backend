from google_auth_oauthlib.flow import InstalledAppFlow

# The scope defines what the token is allowed to do.
# This one allows reading and writing to Google Calendar.
SCOPES = ['https://www.googleapis.com/auth/calendar.events']


def generate_postman_token():
    print("Starting the login process...")

    # This reads your credentials.json and prepares the login request
    flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)

    # This opens your web browser to log in
    creds = flow.run_local_server(port=0)

    # Convert the credentials into a JSON string
    token_json_string = creds.to_json()

    # Save it to a file so it's easy to copy
    with open('token.json', 'w') as token_file:
        token_file.write(token_json_string)

    print("\n✅ Success! Here is your token JSON to copy into Postman:")
    print("-" * 50)
    print(token_json_string)
    print("-" * 50)
    print("It has also been saved to 'token.json' in this folder.")


if __name__ == '__main__':
    generate_postman_token()