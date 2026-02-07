# Quick Start Guide for Hotel Booking API

## ✅ What's Been Set Up

1. **Django REST Framework** - Installed and configured  
2. **JWT Authentication** - Token-based auth configured
3. **CORS** - Enabled for Flutter/mobile apps
4. **API Endpoints** - Complete REST API created
5. **Swagger Documentation** - Interactive API docs
6. **Serializers** - All models serialized
7. **Permissions** - Authentication & authorization configured

## 🚀 Running the API

### Step 1: Run Migrations

```powershell
cd "c:\Users\HP\OneDrive\Documents\essetech\hotelapp\Hotel-website-Django\hotelapp"
python manage.py migrate
```

If you encounter database issues, the database is already set up in `db.sqlite3`.

### Step 2: Start the Development Server

```powershell
python manage.py runserver
```

The API will be available at: `http://localhost:8000/api/`

### Step 3: Access API Documentation

Open your browser and navigate to:
- **Swagger UI**: http://localhost:8000/api/docs/
- **ReDoc**: http://localhost:8000/api/redoc/
- **API Root**: http://localhost:8000/api/

## 📱 Flutter Integration

### API Base URL
```dart
const String baseUrl = 'http://localhost:8000/api';
// For Android emulator: 'http://10.0.2.2:8000/api'
// For iOS simulator: 'http://localhost:8000/api'
// For production: 'https://your-domain.com/api'
```

### Example: User Registration (Flutter/Dart)

```dart
import 'package:http/http.dart' as http;
import 'dart:convert';

Future<Map<String, dynamic>> registerUser({
  required String username,
  required String email,
  required String password,
  required String firstName,
  required String lastName,
}) async {
  final response = await http.post(
    Uri.parse('$baseUrl/auth/register/'),
    headers: {'Content-Type': 'application/json'},
    body: jsonEncode({
      'username': username,
      'email': email,
      'password': password,
      'password_confirm': password,
      'first_name': firstName,
      'last_name': lastName,
      'user_type': 'Guest',
    }),
  );

  if (response.statusCode == 201) {
    return jsonDecode(response.body);
  } else {
    throw Exception('Failed to register user');
  }
}
```

### Example: Login (Flutter/Dart)

```dart
Future<Map<String, dynamic>> login(String username, String password) async {
  final response = await http.post(
    Uri.parse('$baseUrl/auth/login/'),
    headers: {'Content-Type': 'application/json'},
    body: jsonEncode({
      'username': username,
      'password': password,
    }),
  );

  if (response.statusCode == 200) {
    final data = jsonDecode(response.body);
    // Store tokens
    final accessToken = data['access'];
    final refreshToken = data['refresh'];
    // Save tokens to secure storage
    return data;
  } else {
    throw Exception('Invalid credentials');
  }
}
```

### Example: Get Hotels (Flutter/Dart)

```dart
Future<List<dynamic>> getHotels(String accessToken) async {
  final response = await http.get(
    Uri.parse('$baseUrl/hotels/'),
    headers: {
      'Content-Type': 'application/json',
      'Authorization': 'Bearer $accessToken',
    },
  );

  if (response.statusCode == 200) {
    final data = jsonDecode(response.body);
    return data['results'];
  } else {
    throw Exception('Failed to load hotels');
  }
}
```

### Example: Create Booking (Flutter/Dart)

```dart
Future<Map<String, dynamic>> createBooking({
  required String accessToken,
  required int roomId,
  required String checkIn,
  required String checkOut,
  String? message,
}) async {
  final response = await http.post(
    Uri.parse('$baseUrl/bookings/'),
    headers: {
      'Content-Type': 'application/json',
      'Authorization': 'Bearer $accessToken',
    },
    body: jsonEncode({
      'room_id': roomId,
      'check_in_date': checkIn,  // Format: 'YYYY-MM-DD'
      'check_out_date': checkOut,
      'message': message,
    }),
  );

  if (response.statusCode == 201) {
    return jsonDecode(response.body);
  } else {
    throw Exception('Failed to create booking');
  }
}
```

## 📚 Available Endpoints

### Authentication
- `POST /api/auth/register/` - Register new user
- `POST /api/auth/login/` - Login
- `POST /api/auth/logout/` - Logout
- `POST /api/auth/token/refresh/` - Refresh access token
- `GET /api/auth/profile/` - Get user profile

### Hotels
- `GET /api/hotels/` - List all hotels (supports pagination, filtering, search)
- `GET /api/hotels/{id}/` - Get hotel details
- `GET /api/hotels/{id}/rooms/` - Get hotel rooms
- `GET /api/hotels/{id}/available-rooms/` - Get available rooms
- `GET /api/hotels/{id}/stats/` - Get hotel statistics

### Rooms
- `GET /api/rooms/` - List all rooms
- `GET /api/rooms/{id}/` - Get room details
- `GET /api/rooms/available/` - Get available rooms
- `POST /api/rooms/{id}/check-availability/` - Check room availability

### Bookings
- `GET /api/bookings/` - List user bookings
- `POST /api/bookings/` - Create booking
- `GET /api/bookings/{id}/` - Get booking details
- `GET /api/bookings/my-bookings/` - Get current user's bookings

### Reservations
- `GET /api/reservations/` - List reservations
- `POST /api/reservations/` - Create reservation
- `GET /api/reservations/{id}/` - Get reservation details
- `GET /api/reservations/upcoming/` - Get upcoming reservations
- `GET /api/reservations/past/` - Get past reservations

### Reviews
- `GET /api/reviews/` - List reviews
- `POST /api/reviews/` - Create review
- `GET /api/reviews/hotel_reviews/?hotel_id={id}` - Get hotel reviews

### Search
- `GET /api/search/hotels/?q={query}&region={region}` - Search hotels
- `GET /api/search/rooms/?hotel={id}&check_in={date}&check_out={date}` - Search rooms

### Other Resources
- `GET /api/services/` - List hotel services
- `GET /api/amenities/` - List amenities
- `GET /api/guests/` - List guests
- `POST /api/leads/` - Submit contact form (no auth required)

## 🔐 Authentication Headers

Include JWT token in all authenticated requests:

```
Authorization: Bearer <your_access_token>
```

## 📊 Response Format

### Success Response (List)
```json
{
  "count": 50,
  "next": "http://localhost:8000/api/hotels/?page=2",
  "previous": null,
  "results": [...]
}
```

### Success Response (Single Object)
```json
{
  "id": 1,
  "name": "Hotel Name",
  ...
}
```

### Error Response
```json
{
  "detail": "Error message"
}
```

or

```json
{
  "field_name": ["Error message for this field"]
}
```

## 🧪 Testing the API

### Using curl
```bash
# Register
curl -X POST http://localhost:8000/api/auth/register/ \
  -H "Content-Type: application/json" \
  -d '{"username":"testuser","email":"test@example.com","password":"testpass123","password_confirm":"testpass123","first_name":"Test","last_name":"User","user_type":"Guest"}'

# Login
curl -X POST http://localhost:8000/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{"username":"testuser","password":"testpass123"}'

# Get Hotels
curl -X GET http://localhost:8000/api/hotels/ \
  -H "Authorization: Bearer YOUR_TOKEN_HERE"
```

### Using Postman
1. Import the API endpoints
2. Set base URL: `http://localhost:8000/api`
3. For authenticated endpoints, add Authorization header: `Bearer <token>`

### Using Swagger UI
1. Go to http://localhost:8000/api/docs/
2. Click "Authorize" button
3. Enter: `Bearer <your_token>`
4. Test endpoints directly from the browser

## 🌐 CORS Configuration

CORS is configured to allow requests from:
- `http://localhost:8080` (Flutter web debug)
- `http://localhost:3000` (Common dev port)
- Any origin in DEBUG mode

For production, update `CORS_ALLOWED_ORIGINS` in settings.py with your Flutter app domains.

## 📝 Important Notes

1. **Token Expiry**: Access tokens expire after 24 hours. Use the refresh endpoint to get new tokens.

2. **Date Format**: All dates must be in `YYYY-MM-DD` format (e.g., `2026-03-15`).

3. **Pagination**: Most list endpoints return paginated results (20 items per page by default).

4. **Filtering**: Use query parameters for filtering:
   - `?region=GA` - Filter by region
   - `?room_type=deluxe` - Filter by room type
   - `?status=Available` - Filter by status

5. **Search**: Use `?search=query` for text search on relevant fields.

6. **Ordering**: Use `?ordering=field_name` or `?ordering=-field_name` (descending).

## 🔧 Troubleshooting

### Issue: CORS errors in Flutter
**Solution**: Ensure CORS headers are properly configured and the correct base URL is used.

### Issue: 401 Unauthorized
**Solution**: Check that the JWT token is valid and not expired. Use the refresh endpoint if needed.

### Issue: 404 Not Found
**Solution**: Verify the endpoint URL is correct. Check the API documentation.

### Issue: Token expired
**Solution**: Use the token refresh endpoint:
```dart
POST /api/auth/token/refresh/
Body: {"refresh": "your_refresh_token"}
```

## 📞 Support

For detailed API documentation, visit:
- Swagger UI: http://localhost:8000/api/docs/
- Full Documentation: See `docs/API_DOCUMENTATION.md`

## 🎉 Next Steps

1. Run the development server
2. Test endpoints using Swagger UI
3. Integrate with your Flutter app
4. Implement token storage in Flutter (use `flutter_secure_storage`)
5. Handle token refresh logic
6. Implement error handling
7. Add loading states in your Flutter UI

Happy coding! 🚀
