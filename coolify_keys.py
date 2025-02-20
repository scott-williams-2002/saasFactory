import http.client

conn = http.client.HTTPSConnection("app.coolify.io")

payload = "{\"name\":\"string\",\"description\":\"string\",\"private_key\":\"string\"}"

headers = {
    'Authorization': "Bearer Bearer Token",
    'Content-Type': "application/json"
}

conn.request("POST", "/api/v1/security/keys", payload, headers)

res = conn.getresponse()
data = res.read()

print(data.decode("utf-8"))