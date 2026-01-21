#!/usr/bin/env python3
import http.cookiejar, urllib.request, urllib.parse, json, re, sys
BASE='http://127.0.0.1:8000'
jar = http.cookiejar.CookieJar()
opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(jar))

# Start interview session
start_url = BASE + '/ai/ai-interview-start/'
print('Starting interview session...')
start_data = urllib.parse.urlencode({
    'interview_type': 'software',
    'difficulty': 'standard',
    'question_count': '5',
    'duration_minutes': '10',
    'interviewer_style': 'balanced'
}).encode('utf-8')
try:
    resp = opener.open(start_url, data=start_data, timeout=15)
    print('start status', resp.getcode())
except Exception as e:
    print('start failed', e)
    sys.exit(1)

# Load live page
live_url = BASE + '/ai/ai-interview-live/'
print('Loading live page to grab SESSION_ID...')
try:
    r = opener.open(live_url, timeout=15)
    html = r.read().decode('utf-8')
except Exception as e:
    print('Failed to load live page:', e)
    sys.exit(1)

m = re.search(r"window\.SESSION_ID\s*=\s*\"(\d+)\"", html)
if not m:
    print('SESSION_ID not found in page')
    sys.exit(1)
sid = int(m.group(1))
print('SESSION_ID=', sid)

def post_next(payload):
    url = BASE + '/ai/voice/next/'
    js = json.dumps(payload).encode('utf-8')
    req = urllib.request.Request(url, data=js, headers={'Content-Type': 'application/json'})
    try:
        r = opener.open(req, timeout=30)
        print('\nPOST /ai/voice/next/ ->', r.getcode())
        body = r.read().decode('utf-8')
        try:
            print(json.dumps(json.loads(body), indent=2))
        except Exception:
            print(body[:1000])
        return body
    except Exception as e:
        print('Request failed:', e)
        return None

# 1) START
post_next({'session_id': sid, 'text': '__START__'})
# 2) Answer 1
post_next({'session_id': sid, 'text': 'This is a brief test answer.'})
# 3) Answer 2
post_next({'session_id': sid, 'text': 'Second short answer to advance.'})
# 4) Try sending code (simulate Send Code behavior)
post_next({'session_id': sid, 'text': 'def solution():\n    return 42', 'stt_source': 'code'})
