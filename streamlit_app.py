import streamlit as st
import requests
from authlib.integrations.requests_client import OAuth2Session
from pandas import json_normalize


API_URL = "https://api.sappy-iguana.test.carta.rocks"
AUTH_URL = "https://login.sappy-iguana.test.carta.rocks/o/authorize/"
TOKEN_URL = "https://login.sappy-iguana.test.carta.rocks/o/access_token/"
SCOPES = "read_issuer_info read_issuer_securities"
# In order to test this further, we need to specify this as an acceptable URI for the test app (or all other applications)
REDIRECT_URI = "https://public-api-example.streamlit.app"


def _headers(auth_token) -> dict:
  return {
      "Authorization": f"Bearer {auth_token}"
  }

def get_access_token(url):
    response = requests.post(
        TOKEN_URL,
        data={"grant_type": "client_credentials", },
        auth=(st.secrets["client_id"], st.secrets["client_secret"]),
    )
    return response.json()["access_token"]
        

def authenticate():
    # Create an OAuth2 session
    client = OAuth2Session(client_id=st.secrets["client_id"], client_secret=st.secrets["client_secret"], scope=SCOPES, redirect_uri=REDIRECT_URI)

    # Generate the authorization URL
    authorization_url, state = client.create_authorization_url(AUTH_URL)

    st.write("Please go to the following URL to authorize access:", f"[Authorize here]({authorization_url})")

    query_params = st.query_params
    
    if query_params.get("code"):
        st.write(query_params)
        query_string = "&".join([f"{key}={value}" for key, value in query_params.items()])
        full_url = f"https://public-api-example.streamlit.app/?{query_string}"
        st.write(full_url)
        token = client.fetch_token(TOKEN_URL, authorization_response=full_url)
        if 'key' not in st.session_state:
            st.session_state['token'] = token
        st.write(f"Access token: {token['access_token']}")
        st.write(f"Scopes granted: {token['scope']}")

def request_and_show_data(api_endpoint: str) -> dict:
    request_url = API_URL + api_endpoint
    response = requests.get(request_url, headers=_headers(st.session_state.token))

    if response.status_code == 200:
        data = response.json()
        dataframe = json_normalize(data["convertibleNotes"])
        st.write(dataframe)
    else:
        st.error(f"Request failed with status code {response.status_code}")


st.write("### List ConvertibleNotes")
authenticate()


if st.button("List Certificates"):
    request_and_show_data("/v1alpha1/issuers/1222/convertibleNotes")
