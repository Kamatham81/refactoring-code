# 🧪 How to Test the Fixed Application

## 📋 Quick Start Guide

### 1. **Start the Application**
```bash
cd assignments/messy-migration
python app.py
```

**Expected Output:**
```
2025-08-04 05:52:39,605 - WARNING -  * Debugger is active!
2025-08-04 05:52:39,641 - INFO -  * Debugger PIN: 369-626-345
 * Running on all addresses (0.0.0.0)
 * Running on http://127.0.0.1:5009
 * Running on http://[::1]:5009
```

✅ **Success:** Server is running on `http://localhost:5009`

---

## 🌐 Testing Methods

### **Method 1: Using Web Browser**
Open your browser and visit these URLs:

#### **Test 1: Home Page**
```
http://localhost:5009/
```
**Expected Output:** `User Management System`

#### **Test 2: Get All Users**
```
http://localhost:5009/users
```
**Expected Output:**
```json
{
  "users": [
    {
      "email": "john@example.com",
      "id": 1,
      "name": "John Doe"
    },
    {
      "email": "jane@example.com",
      "id": 2,
      "name": "Jane Smith"
    },
    {
      "email": "bob@example.com",
      "id": 3,
      "name": "Bob Johnson"
    }
  ]
}
```

#### **Test 3: Get Single User**
```
http://localhost:5009/user/1
```
**Expected Output:**
```json
{
  "email": "john@example.com",
  "id": 1,
  "name": "John Doe"
}
```

#### **Test 4: SQL Injection Test (Should Fail)**
```
http://localhost:5009/user/1' OR '1'='1
```
**Expected Output:**
```json
{
  "error": "User not found"
}
```
✅ **Success:** SQL injection is blocked!

---

### **Method 2: Using Command Line (curl)**

#### **Test 1: Get All Users**
```bash
curl http://localhost:5009/users
```

#### **Test 2: Get Single User**
```bash
curl http://localhost:5009/user/1
```

#### **Test 3: Create New User**
```bash
curl -X POST http://localhost:5009/users \
  -H "Content-Type: application/json" \
  -d '{"name": "Test User", "email": "test@example.com", "password": "testpass"}'
```
**Expected Output:**
```json
{
  "message": "User created successfully"
}
```

#### **Test 4: Update User**
```bash
curl -X PUT http://localhost:5009/user/1 \
  -H "Content-Type: application/json" \
  -d '{"name": "Updated Name", "email": "updated@example.com"}'
```

#### **Test 5: Search Users**
```bash
curl "http://localhost:5009/search?name=John"
```

#### **Test 6: Login**
```bash
curl -X POST http://localhost:5009/login \
  -H "Content-Type: application/json" \
  -d '{"email": "john@example.com", "password": "password123"}'
```

#### **Test 7: Delete User**
```bash
curl -X DELETE http://localhost:5009/user/1
```

---

### **Method 3: Using Postman**

1. **Download Postman** from https://www.postman.com/
2. **Create a new collection** called "User Management API"
3. **Add these requests:**

#### **GET All Users**
- Method: `GET`
- URL: `http://localhost:5009/users`

#### **POST Create User**
- Method: `POST`
- URL: `http://localhost:5009/users`
- Headers: `Content-Type: application/json`
- Body (raw JSON):
```json
{
  "name": "New User",
  "email": "new@example.com", 
  "password": "newpass123"
}
```

#### **PUT Update User**
- Method: `PUT`
- URL: `http://localhost:5009/user/1`
- Headers: `Content-Type: application/json`
- Body (raw JSON):
```json
{
  "name": "Updated User",
  "email": "updated@example.com"
}
```

---

## 🔍 What to Look For

### ✅ **Signs Everything is Working:**

1. **Clean JSON Responses** (not raw tuples)
2. **Proper HTTP Status Codes:**
   - 200 for success
   - 201 for created
   - 404 for not found
   - 400 for bad request
   - 500 for server error

3. **Security Features:**
   - Passwords NOT visible in responses
   - SQL injection attempts return 404
   - Input validation working

4. **Error Handling:**
   - Invalid JSON returns proper error
   - Missing fields return validation errors
   - Database errors handled gracefully

### ❌ **Signs of Problems:**

1. **Raw tuple responses** like `(1, 'John', 'email', 'password')`
2. **Application crashes** on invalid input
3. **SQL injection works** (returns unauthorized data)
4. **Passwords visible** in API responses

---

## 📊 Expected vs Actual Results

### **Before Fixes (Bad Output):**
```
# Raw tuple format
[(1, 'John Doe', 'john@example.com', 'password123')]

# SQL injection works
Input: 1' OR '1'='1
Output: (1, 'John Doe', 'john@example.com', 'password123')
```

### **After Fixes (Good Output):**
```json
{
  "users": [
    {
      "id": 1,
      "name": "John Doe",
      "email": "john@example.com"
    }
  ]
}
```

```json
// SQL injection blocked
{
  "error": "User not found"
}
```

---

## 🚨 Error Testing

### **Test Invalid JSON:**
```bash
curl -X POST http://localhost:5009/users \
  -H "Content-Type: application/json" \
  -d 'invalid json'
```
**Expected:** `{"error": "Invalid JSON data"}` with status 400

### **Test Missing Fields:**
```bash
curl -X POST http://localhost:5009/users \
  -H "Content-Type: application/json" \
  -d '{"name": "Test"}'
```
**Expected:** `{"error": "Missing required field: email"}` with status 400

### **Test Non-existent User:**
```bash
curl http://localhost:5009/user/999
```
**Expected:** `{"error": "User not found"}` with status 404

---

## 📝 Checking Logs

**In the terminal where you ran `python app.py`, you should see logs like:**

```
2025-08-04 05:55:36,769 - INFO - User found: John Doe
2025-08-04 05:55:36,770 - INFO - 127.0.0.1 - - [04/Aug/2025 05:55:36] "GET /user/1 HTTP/1.1" 200 -
2025-08-04 05:55:21,917 - INFO - User not found
2025-08-04 05:55:21,918 - INFO - 127.0.0.1 - - [04/Aug/2025 05:55:21] "GET /user/1'%20OR%20'1'='1 HTTP/1.1" 404 -
```

✅ **Good signs in logs:**
- `INFO` messages for successful operations
- `WARNING` messages for failed login attempts
- `ERROR` messages for database issues
- Proper HTTP status codes (200, 404, 400, etc.)

---

## 🎯 Quick Verification Checklist

- [ ] Server starts without errors
- [ ] `/users` returns clean JSON (not tuples)
- [ ] `/user/1` returns single user in JSON
- [ ] SQL injection `1' OR '1'='1` returns 404
- [ ] Invalid JSON returns 400 error
- [ ] Missing fields return validation errors
- [ ] Passwords not visible in responses
- [ ] Logs show proper status codes
- [ ] All endpoints respond (no crashes)

**If all checkboxes are ✅, the fixes are working perfectly!**