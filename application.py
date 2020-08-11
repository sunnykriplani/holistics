from flask import Flask, request, redirect
import requests

app = Flask(__name__)

CLIENT_ID = "3f034891bb6540cdf2bbbc19be0bdb7fb9d11800691a0043534fe7e7be995274"
CUSTOMER_SECRET = "bca35e1f804aaaf8a089967d29abbf4259cf179f06e1c008949c0cf5d1ed057c"
STATE = "dev"
ACCOUNT_URL = "https://account.withings.com"
WBSAPI_URL = "https://wbsapi.withings.net"
CALLBACK_URI = "https://holistics.azurewebsites.net/get_token"


@app.route("/")
def get_code():
    """
    Route to get the permission from an user to take his data.
    This endpoint redirects to a Withings' login page on which
    the user has to identify and accept to share his data
    """
    payload = {'response_type': 'code',  # imposed string by the api
               'client_id': CLIENT_ID,
               'state': STATE,
               'scope': 'user.info',  # see docs for enhanced scope
               'redirect_uri': CALLBACK_URI,  # URL of this app
               }

    r_auth = requests.get(f'{ACCOUNT_URL}/oauth2_user/authorize2',
                          params=payload)

    return redirect(r_auth.url)


@app.route("/get_token")
def get_token():
    """
    Callback route when the user has accepted to share his data.
    Once the auth has arrived Withings servers come back with
    an authentication code and the state code provided in the
    initial call
    """
    code = request.args.get('code')
    state = request.args.get('state')

    payload = {'grant_type': 'authorization_code',
               'client_id': CLIENT_ID,
               'client_secret': CUSTOMER_SECRET,
               'code': code,
               'redirect_uri': CALLBACK_URI
               }

    r_token = requests.post(f'{ACCOUNT_URL}/oauth2/token',
                            data=payload).json()

    access_token = r_token.get('access_token', '')

    # GET Some info with this token
    headers = {'Authorization': 'Bearer ' + access_token}
    payload = {'action': 'getdevice'}

    # List devices of returned user
    r_getdevice = requests.get(f'{WBSAPI_URL}/v2/user',
                               headers=headers,
                               params=payload).json()

    return r_getdevice

if __name__ == '__main__':
    app.run()
