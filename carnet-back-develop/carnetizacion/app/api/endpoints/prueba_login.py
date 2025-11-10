import requests
import json

reqUrl = "https://sigenu.cujae.edu.cu/sigenu-ldap-cujae/ldap/login"

headersList = {
 "Accept": "*/*",
 "User-Agent": "Thunder Client (https://www.thunderclient.com)",
 "Authorization": "Basic ZnBpY2F5by5zZWM6U2lnZW51X3NlY18qMjAxNCo=",
 "Content-Type": "application/json"
}

payload = json.dumps({
    "username": "accarlosaas",
    "password": "cujae2022*+"
})

response = requests.request("POST", reqUrl, data=payload,  headers=headersList)

#print(response.text)
