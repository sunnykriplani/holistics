from flask import Flask, request, redirect,jsonify
import requests

app = Flask(__name__)
app.config["DEBUG"] = True

# Tyndall specific Client and Secret ID
CLIENT_ID = "3f034891bb6540cdf2bbbc19be0bdb7fb9d11800691a0043534fe7e7be995274"
CUSTOMER_SECRET = "bca35e1f804aaaf8a089967d29abbf4259cf179f06e1c008949c0cf5d1ed057c"
STATE = "dev"
ACCOUNT_URL = "https://account.withings.com"
WBSAPI_URL = "https://wbsapi.withings.net"

# Azure hosting specific URL
CALLBACK_URI = "http://wsnhol.azurewebsites.net/get_token"
USER = "sunny"
PASS = "sunny"
acc_list = []



# Function to check if requested user is available in 
# database
@app.route("/login")
def login():
    usrname = request.args.get('user')
    password = request.args.get('pass')
    print(usrname)
    print(password)
    print(usrname + password)
    if (usrname == USER) and (password == PASS):
        return "login successful"
    else:
        return "login failed"


#   Function to take permission from user for OAUTH and redirects
#   to login page where user will approve the permissions this will 
#   post the access code on success
@app.route("/")
def get_code():

    payload = {'response_type': 'code',  # Specific to the Api
               'client_id': CLIENT_ID,
               'state': STATE,
               # permissions to be taken from user
               'scope': 'user.info,user.metrics,user.activity',  
               'redirect_uri': CALLBACK_URI,  # URL of this app
               }

    r_auth = requests.get(f'{ACCOUNT_URL}/oauth2_user/authorize2',
                          params=payload)
    print(r_auth.url)
    return redirect(r_auth.url)


#   Server POST Request URL which will allow Withings to send
#   access code to the server and access code can be used to 
#   fetch Access token/ Refresh Token
@app.route("/get_token")
def get_token():


    code = request.args.get('code')
    state = request.args.get('state')
    print(code)
    print(state)
    payload = {'grant_type': 'authorization_code',
               'client_id': CLIENT_ID,
               'client_secret': CUSTOMER_SECRET,
               'code': code,
               'redirect_uri': CALLBACK_URI
               }

    r_token = requests.post(f'{ACCOUNT_URL}/oauth2/token',
                            data=payload).json()
    access_token = r_token.get('access_token', '')
    acc_list.append(access_token)
    print(access_token)
    # GET Some info with this token
    headers = {'Authorization': 'Bearer ' + access_token}
    payload = {'action': 'getdevice'}
    
    # Javascript to return to the user which will allow
    # user to jump to other activity upon success
    
    js = "<title>Fetch Data</title> \
    <script language=\"javascript\"> \
    function sendtoAndroid() { \
    var str = \"" + str(access_token) + "\";\
    javascript_object.OpenActivity(str); }  \
    </script> \
    <center>  <h2>Successfully Captured the token</h2> \
    <button onclick=\"sendtoAndroid()\">Fetch Data</button> \
    </center> "
    
    # List devices of returned user
    # r_getdevice = requests.get(f'{WBSAPI_URL}/v2/user',
    #                            headers=headers,
    #                            params=payload).json()
                                 
        
    return js


#   Additional function which allow user to request for Data
@app.route("/get_data")
def get_data():
    measure_type = request.args.get('type')
    print(acc_list)
    headers = {'Authorization': 'Bearer ' + acc_list[0]}
    payload = {'action': 'getmeas',
                'meastypes': measure_type,
                'category' : '1',
                }
                
    r_getdata = requests.get(f'{WBSAPI_URL}/measure',
                                headers=headers,
                                params=payload).json()
    return str(r_getdata)

#   main function to run the server 
if __name__ == '__main__':
    app.run()
