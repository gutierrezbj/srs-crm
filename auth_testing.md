# Auth Testing Playbook - System Rapid Solutions CRM

## Step 1: Create Test User & Session

```bash
mongosh --eval "
use('test_database');
var userId = 'test-user-' + Date.now();
var sessionToken = 'test_session_' + Date.now();
db.users.insertOne({
  user_id: userId,
  email: 'juancho@systemrapidsolutions.com',
  name: 'JuanCho Test',
  picture: null,
  role: 'admin',
  created_at: new Date().toISOString()
});
db.user_sessions.insertOne({
  user_id: userId,
  session_token: sessionToken,
  expires_at: new Date(Date.now() + 7*24*60*60*1000).toISOString(),
  created_at: new Date().toISOString()
});
print('Session token: ' + sessionToken);
print('User ID: ' + userId);
"
```

## Step 2: Test Backend API

```bash
# Get session token first
SESSION_TOKEN=$(mongosh --quiet --eval "use('test_database'); db.user_sessions.findOne({}, {session_token: 1, _id: 0}).session_token")

# Test auth endpoint
API_URL="https://dronesys-crm.preview.emergentagent.com"

curl -X GET "$API_URL/api/auth/me" \
  -H "Authorization: Bearer $SESSION_TOKEN"

# Test leads endpoints
curl -X POST "$API_URL/api/leads" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $SESSION_TOKEN" \
  -d '{"empresa": "Test Corp", "contacto": "John Doe", "email": "john@test.com", "valor_estimado": 5000}'

curl -X GET "$API_URL/api/leads" \
  -H "Authorization: Bearer $SESSION_TOKEN"

curl -X GET "$API_URL/api/leads/stats" \
  -H "Authorization: Bearer $SESSION_TOKEN"
```

## Step 3: Browser Testing

```python
# Set cookie and navigate
await page.context.add_cookies([{
    "name": "session_token",
    "value": "YOUR_SESSION_TOKEN",
    "domain": "dronesys-crm.preview.emergentagent.com",
    "path": "/",
    "httpOnly": True,
    "secure": True,
    "sameSite": "None"
}])
await page.goto("https://dronesys-crm.preview.emergentagent.com/dashboard")
```

## Quick Debug

```bash
# Check data format
mongosh --eval "
use('test_database');
db.users.find().limit(2).pretty();
db.user_sessions.find().limit(2).pretty();
db.leads.find().limit(2).pretty();
"

# Clean test data
mongosh --eval "
use('test_database');
db.users.deleteMany({email: /test/});
db.user_sessions.deleteMany({session_token: /test_session/});
db.leads.deleteMany({empresa: /Test/});
"
```

## Checklist
- [ ] User document has user_id field (custom UUID, MongoDB's _id is separate)
- [ ] Session user_id matches user's user_id exactly
- [ ] All queries use `{"_id": 0}` projection to exclude MongoDB's _id
- [ ] Backend queries use user_id (not _id or id)
- [ ] API returns user data with user_id field (not 401/404)
- [ ] Browser loads dashboard (not login page)
