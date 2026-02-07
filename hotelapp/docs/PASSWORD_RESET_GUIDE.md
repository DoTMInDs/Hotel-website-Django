# Password Reset & Management API

## Overview
Complete password reset and management functionality for your Flutter app, including:
- **Forgot Password** - Request password reset via email
- **Reset Password** - Reset password using token from email
- **Change Password** - Change password when logged in

---

## 🔐 API Endpoints

### 1. Request Password Reset
Send reset link to user's email.

```http
POST /api/auth/password-reset/
```

**Request Body:**
```json
{
  "email": "user@example.com"
}
```

**Success Response (200):**
```json
{
  "message": "Password reset email sent successfully",
  "uid": "MQ",
  "token": "c5h2vx-a1b2c3d4e5f6g7h8i9j0"
}
```

**Error Response (400):**
```json
{
  "email": ["No user found with this email address"]
}
```

---

### 2. Confirm Password Reset
Reset password using token from email.

```http
POST /api/auth/password-reset-confirm/
```

**Request Body:**
```json
{
  "uid": "MQ",
  "token": "c5h2vx-a1b2c3d4e5f6g7h8i9j0",
  "new_password": "newSecurePass123",
  "new_password_confirm": "newSecurePass123"
}
```

**Success Response (200):**
```json
{
  "message": "Password reset successful. You can now login with your new password."
}
```

**Error Response (400):**
```json
{
  "non_field_errors": ["Invalid or expired reset link"]
}
```

---

### 3. Change Password (Authenticated)
Change password when user is logged in.

```http
POST /api/auth/change-password/
```

**Headers:**
```
Authorization: Bearer <access_token>
```

**Request Body:**
```json
{
  "old_password": "currentPassword123",
  "new_password": "newSecurePass123",
  "new_password_confirm": "newSecurePass123"
}
```

**Success Response (200):**
```json
{
  "message": "Password changed successfully"
}
```

**Error Response (400):**
```json
{
  "error": "Current password is incorrect"
}
```

---

## 📱 Flutter Integration

### Complete Password Reset Service

```dart
import 'package:http/http.dart' as http;
import 'dart:convert';

class PasswordResetService {
  static const String baseUrl = 'http://localhost:8000/api';
  
  /// Step 1: Request password reset
  static Future<Map<String, dynamic>> requestPasswordReset(String email) async {
    final response = await http.post(
      Uri.parse('$baseUrl/auth/password-reset/'),
      headers: {'Content-Type': 'application/json'},
      body: jsonEncode({'email': email}),
    );
    
    if (response.statusCode == 200) {
      return jsonDecode(response.body);
    } else {
      final error = jsonDecode(response.body);
      throw Exception(error['email']?.first ?? 'Failed to send reset email');
    }
  }
  
  /// Step 2: Confirm password reset with token
  static Future<String> confirmPasswordReset({
    required String uid,
    required String token,
    required String newPassword,
  }) async {
    final response = await http.post(
      Uri.parse('$baseUrl/auth/password-reset-confirm/'),
      headers: {'Content-Type': 'application/json'},
      body: jsonEncode({
        'uid': uid,
        'token': token,
        'new_password': newPassword,
        'new_password_confirm': newPassword,
      }),
    );
    
    if (response.statusCode == 200) {
      final data = jsonDecode(response.body);
      return data['message'];
    } else {
      final error = jsonDecode(response.body);
      throw Exception(error['non_field_errors']?.first ?? 'Password reset failed');
    }
  }
  
  /// Change password when logged in
  static Future<String> changePassword({
    required String accessToken,
    required String oldPassword,
    required String newPassword,
  }) async {
    final response = await http.post(
      Uri.parse('$baseUrl/auth/change-password/'),
      headers: {
        'Content-Type': 'application/json',
        'Authorization': 'Bearer $accessToken',
      },
      body: jsonEncode({
        'old_password': oldPassword,
        'new_password': newPassword,
        'new_password_confirm': newPassword,
      }),
    );
    
    if (response.statusCode == 200) {
      final data = jsonDecode(response.body);
      return data['message'];
    } else {
      final error = jsonDecode(response.body);
      throw Exception(error['error'] ?? 'Password change failed');
    }
  }
}
```

---

## 🎯 Flutter UI Examples

### 1. Forgot Password Screen

```dart
class ForgotPasswordScreen extends StatefulWidget {
  @override
  _ForgotPasswordScreenState createState() => _ForgotPasswordScreenState();
}

class _ForgotPasswordScreenState extends State<ForgotPasswordScreen> {
  final _emailController = TextEditingController();
  final _formKey = GlobalKey<FormState>();
  bool _isLoading = false;

  Future<void> _requestReset() async {
    if (!_formKey.currentState!.validate()) return;

    setState(() => _isLoading = true);

    try {
      final result = await PasswordResetService.requestPasswordReset(
        _emailController.text,
      );

      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text(result['message'])),
      );

      // Navigate to reset confirmation screen with uid and token
      Navigator.push(
        context,
        MaterialPageRoute(
          builder: (_) => ResetPasswordScreen(
            uid: result['uid'],
            token: result['token'],
          ),
        ),
      );
    } catch (e) {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text(e.toString())),
      );
    } finally {
      setState(() => _isLoading = false);
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: Text('Forgot Password')),
      body: Padding(
        padding: EdgeInsets.all(16.0),
        child: Form(
          key: _formKey,
          child: Column(
            mainAxisAlignment: MainAxisAlignment.center,
            children: [
              Text(
                'Enter your email to receive reset instructions',
                textAlign: TextAlign.center,
                style: TextStyle(fontSize: 16),
              ),
              SizedBox(height: 24),
              TextFormField(
                controller: _emailController,
                decoration: InputDecoration(
                  labelText: 'Email',
                  border: OutlineInputBorder(),
                ),
                keyboardType: TextInputType.emailAddress,
                validator: (value) {
                  if (value?.isEmpty ?? true) return 'Email is required';
                  if (!value!.contains('@')) return 'Invalid email';
                  return null;
                },
              ),
              SizedBox(height: 24),
              ElevatedButton(
                onPressed: _isLoading ? null : _requestReset,
                child: _isLoading
                    ? CircularProgressIndicator()
                    : Text('Send Reset Link'),
                style: ElevatedButton.styleFrom(
                  minimumSize: Size(double.infinity, 48),
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }
}
```

### 2. Reset Password Screen

```dart
class ResetPasswordScreen extends StatefulWidget {
  final String uid;
  final String token;

  const ResetPasswordScreen({
    required this.uid,
    required this.token,
  });

  @override
  _ResetPasswordScreenState createState() => _ResetPasswordScreenState();
}

class _ResetPasswordScreenState extends State<ResetPasswordScreen> {
  final _passwordController = TextEditingController();
  final _confirmPasswordController = TextEditingController();
  final _formKey = GlobalKey<FormState>();
  bool _isLoading = false;
  bool _obscurePassword = true;

  Future<void> _resetPassword() async {
    if (!_formKey.currentState!.validate()) return;

    setState(() => _isLoading = true);

    try {
      final message = await PasswordResetService.confirmPasswordReset(
        uid: widget.uid,
        token: widget.token,
        newPassword: _passwordController.text,
      );

      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text(message)),
      );

      // Navigate back to login
      Navigator.pushNamedAndRemoveUntil(context, '/login', (route) => false);
    } catch (e) {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text(e.toString())),
      );
    } finally {
      setState(() => _isLoading = false);
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: Text('Reset Password')),
      body: Padding(
        padding: EdgeInsets.all(16.0),
        child: Form(
          key: _formKey,
          child: Column(
            mainAxisAlignment: MainAxisAlignment.center,
            children: [
              TextFormField(
                controller: _passwordController,
                decoration: InputDecoration(
                  labelText: 'New Password',
                  border: OutlineInputBorder(),
                  suffixIcon: IconButton(
                    icon: Icon(_obscurePassword
                        ? Icons.visibility
                        : Icons.visibility_off),
                    onPressed: () {
                      setState(() => _obscurePassword = !_obscurePassword);
                    },
                  ),
                ),
                obscureText: _obscurePassword,
                validator: (value) {
                  if (value?.isEmpty ?? true) return 'Password is required';
                  if (value!.length < 8) {
                    return 'Password must be at least 8 characters';
                  }
                  return null;
                },
              ),
              SizedBox(height: 16),
              TextFormField(
                controller: _confirmPasswordController,
                decoration: InputDecoration(
                  labelText: 'Confirm Password',
                  border: OutlineInputBorder(),
                ),
                obscureText: _obscurePassword,
                validator: (value) {
                  if (value != _passwordController.text) {
                    return 'Passwords do not match';
                  }
                  return null;
                },
              ),
              SizedBox(height: 24),
              ElevatedButton(
                onPressed: _isLoading ? null : _resetPassword,
                child: _isLoading
                    ? CircularProgressIndicator()
                    : Text('Reset Password'),
                style: ElevatedButton.styleFrom(
                  minimumSize: Size(double.infinity, 48),
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }
}
```

### 3. Change Password Screen (When Logged In)

```dart
class ChangePasswordScreen extends StatefulWidget {
  @override
  _ChangePasswordScreenState createState() => _ChangePasswordScreenState();
}

class _ChangePasswordScreenState extends State<ChangePasswordScreen> {
  final _oldPasswordController = TextEditingController();
  final _newPasswordController = TextEditingController();
  final _confirmPasswordController = TextEditingController();
  final _formKey = GlobalKey<FormState>();
  bool _isLoading = false;

  Future<void> _changePassword() async {
    if (!_formKey.currentState!.validate()) return;

    setState(() => _isLoading = true);

    try {
      // Get access token from secure storage
      final accessToken = await getAccessToken(); // Your token storage method

      final message = await PasswordResetService.changePassword(
        accessToken: accessToken,
        oldPassword: _oldPasswordController.text,
        newPassword: _newPasswordController.text,
      );

      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text(message)),
      );

      Navigator.pop(context);
    } catch (e) {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text(e.toString())),
      );
    } finally {
      setState(() => _isLoading = false);
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: Text('Change Password')),
      body: Padding(
        padding: EdgeInsets.all(16.0),
        child: Form(
          key: _formKey,
          child: Column(
            children: [
              TextFormField(
                controller: _oldPasswordController,
                decoration: InputDecoration(
                  labelText: 'Current Password',
                  border: OutlineInputBorder(),
                ),
                obscureText: true,
                validator: (value) =>
                    value?.isEmpty ?? true ? 'Required' : null,
              ),
              SizedBox(height: 16),
              TextFormField(
                controller: _newPasswordController,
                decoration: InputDecoration(
                  labelText: 'New Password',
                  border: OutlineInputBorder(),
                ),
                obscureText: true,
                validator: (value) {
                  if (value?.isEmpty ?? true) return 'Required';
                  if (value!.length < 8) return 'Min 8 characters';
                  return null;
                },
              ),
              SizedBox(height: 16),
              TextFormField(
                controller: _confirmPasswordController,
                decoration: InputDecoration(
                  labelText: 'Confirm New Password',
                  border: OutlineInputBorder(),
                ),
                obscureText: true,
                validator: (value) {
                  if (value != _newPasswordController.text) {
                    return 'Passwords do not match';
                  }
                  return null;
                },
              ),
              SizedBox(height: 24),
              ElevatedButton(
                onPressed: _isLoading ? null : _changePassword,
                child: _isLoading
                    ? CircularProgressIndicator()
                    : Text('Change Password'),
                style: ElevatedButton.styleFrom(
                  minimumSize: Size(double.infinity, 48),
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }
}
```

---

## 🔒 Security Features

✅ **Token Expiration** - Reset tokens expire after 24 hours  
✅ **One-time Use** - Tokens are invalidated after successful password reset  
✅ **Email Verification** - Reset link sent only to registered email  
✅ **Password Strength** - Minimum 8 characters required  
✅ **Old Password Verification** - Required when changing password while logged in

---

## 📧 Email Configuration

Make sure your Django email settings are configured in `settings.py`:

```python
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.zoho.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = os.getenv('EMAIL_HOST_USER')
EMAIL_HOST_PASSWORD = os.getenv('EMAIL_HOST_PASSWORD')
DEFAULT_FROM_EMAIL = os.getenv('DEFAULT_FROM_EMAIL')
```

---

## 🧪 Testing

### Using curl

**1. Request Password Reset:**
```bash
curl -X POST http://localhost:8000/api/auth/password-reset/ \
  -H "Content-Type: application/json" \
  -d '{"email":"user@example.com"}'
```

**2. Confirm Password Reset:**
```bash
curl -X POST http://localhost:8000/api/auth/password-reset-confirm/ \
  -H "Content-Type: application/json" \
  -d '{
    "uid":"MQ",
    "token":"c5h2vx-a1b2c3d4e5f6g7h8i9j0",
    "new_password":"newpass123",
    "new_password_confirm":"newpass123"
  }'
```

**3. Change Password (Authenticated):**
```bash
curl -X POST http://localhost:8000/api/auth/change-password/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -d '{
    "old_password":"oldpass123",
    "new_password":"newpass123",
    "new_password_confirm":"newpass123"
  }'
```

---

## 📱 Deep Linking for Flutter

For better UX, configure deep links in your Flutter app:

### Android (`android/app/src/main/AndroidManifest.xml`):
```xml
<intent-filter>
    <action android:name="android.intent.action.VIEW" />
    <category android:name="android.intent.category.DEFAULT" />
    <category android:name="android.intent.category.BROWSABLE" />
    <data android:scheme="yourapp" android:host="reset-password" />
</intent-filter>
```

### iOS (`ios/Runner/Info.plist`):
```xml
<key>CFBundleURLTypes</key>
<array>
    <dict>
        <key>CFBundleURLSchemes</key>
        <array>
            <string>yourapp</string>
        </array>
    </dict>
</array>
```

Then use the deep link in your password reset email:
```
yourapp://reset-password?uid=MQ&token=c5h2vx-a1b2c3d4e5f6g7h8i9j0
```

---

## ✅ All Password Management Endpoints

| Endpoint | Method | Auth | Description |
|----------|--------|------|-------------|
| `/api/auth/password-reset/` | POST | No | Request password reset |
| `/api/auth/password-reset-confirm/` | POST | No | Confirm password reset |
| `/api/auth/change-password/` | POST | Yes | Change password (logged in) |

---

Complete password management system ready for your Flutter app! 🎉
