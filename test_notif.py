import urllib.request, urllib.parse, json
import http.cookiejar

cj = http.cookiejar.CookieJar()
opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cj))
urllib.request.install_opener(opener)

data = urllib.parse.urlencode({'username': 'admin', 'password': '123'}).encode('utf-8')
req = urllib.request.Request('http://127.0.0.1:5000/login', data=data)
try:
    resp = urllib.request.urlopen(req)
except Exception as e:
    pass

req = urllib.request.Request('http://127.0.0.1:5000/api/notifications')
try:
    resp = urllib.request.urlopen(req)
    print(resp.status)
    print(resp.read().decode())
except urllib.error.HTTPError as e:
    print(e.code)
    print(e.read().decode())
