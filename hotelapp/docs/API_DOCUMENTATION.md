# Hotel Booking API Documentation

## Overview
Complete REST API for Hotel Booking System built with Django REST Framework. This API provides all necessary endpoints for integrating a Flutter mobile application with the hotel booking backend.

## Base URL
- **Development**: `http://localhost:8000/api/`
- **Production**: `https://your-domain.com/api/`

## Interactive Documentation
- **Swagger UI**: `/api/docs/`
- **ReDoc**: `/api/redoc/`

## Authentication

### JWT Token Authentication
This API uses JWT (JSON Web Token) for authentication. Include the token in the Authorization header:

```
Authorization: Bearer <your_access_token>
```

### Authentication Endpoints

#### 1. Register User
```http
POST /api/auth/register/
```

**Request Body:**
```json
{
    "username": "john_doe",
    "email": "john@example.com",
    "password": "securepassword123",
    "password_confirm": "securepassword123",
    "first_name": "John",
    "last_name": "Doe",
    "user_type": "Guest"
}
```

**Response:**
```json
{
    "user": {
        "id": 1,
        "username": "john_doe",
        "email": "john@example.com",
        "first_name": "John",
        "last_name": "Doe",
        "user_type": "Guest",
        "is_verified": false,
        "created_at": "2026-02-06T10:00:00"
    },
    "access": "eyJ0eXAiOiJKV1QiLCJhbGc...",
    "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc...",
    "message": "User registered successfully"
}
```

#### 2. Login
```http
POST /api/auth/login/
```

**Request Body:**
```json
{
    "username": "john_doe",
    "password": "securepassword123"
}
```

**Response:**
```json
{
    "user": {
        "id": 1,
        "username": "john_doe",
        "email": "john@example.com",
        "user_type": "Guest"
    },
    "access": "eyJ0eXAiOiJKV1QiLCJhbGc...",
    "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc...",
    "message": "Login successful"
}
```

#### 3. Refresh Token
```http
POST /api/auth/token/refresh/
```

**Request Body:**
```json
{
    "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc..."
}
```

#### 4. Logout
```http
POST /api/auth/logout/
```

**Request Body:**
```json
{
    "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc..."
}
```

#### 5. Get User Profile
```http
GET /api/auth/profile/
```
**Authentication Required**

---

## Hotels

### List All Hotels
```http
GET /api/hotels/
```

**Query Parameters:**
- `region` - Filter by region (GA, AS, CR, etc.)
- `has_payment_setup` - Filter by payment setup (true/false)
- `search` - Search by name, location, or description
- `ordering` - Sort by field (name, created_at, -created_at)
- `page` - Page number for pagination

**Response:**
```json
{
    "count": 50,
    "next": "http://localhost:8000/api/hotels/?page=2",
    "previous": null,
    "results": [
        {
            "id": 1,
            "name": "Grand Hotel Accra",
            "phone_number": "+233123456789",
            "email": "info@grandhotel.com",
            "location": "Accra Central",
            "region": "GA",
            "region_display": "Greater Accra",
            "logo": "https://res.cloudinary.com/...",
            "hotel_image": "https://res.cloudinary.com/...",
            "amenities_count": 8,
            "rooms_count": 25,
            "has_payment_setup": true,
            "created_at": "2026-01-15T10:00:00"
        }
    ]
}
```

### Get Hotel Details
```http
GET /api/hotels/{id}/
```

**Response:**
```json
{
    "id": 1,
    "name": "Grand Hotel Accra",
    "phone_number": "+233123456789",
    "email": "info@grandhotel.com",
    "location": "Accra Central",
    "description": "Luxury hotel in the heart of Accra",
    "region": "GA",
    "region_display": "Greater Accra",
    "logo": "https://res.cloudinary.com/...",
    "hotel_image": "https://res.cloudinary.com/...",
    "amenities": [
        {
            "id": 1,
            "amenity_name": "WiFi"
        },
        {
            "id": 2,
            "amenity_name": "Swimming Pool"
        }
    ],
    "services": [
        {
            "id": 1,
            "name": "Room Service",
            "description": "24/7 room service",
            "category": "RS",
            "category_display": "Room Service",
            "is_available": true,
            "price": "50.00"
        }
    ],
    "has_payment_setup": true,
    "created_at": "2026-01-15T10:00:00"
}
```

### Get Hotel Rooms
```http
GET /api/hotels/{id}/rooms/
```

### Get Available Rooms for Hotel
```http
GET /api/hotels/{id}/available-rooms/
```

**Query Parameters:**
- `check_in` - Check-in date (YYYY-MM-DD)
- `check_out` - Check-out date (YYYY-MM-DD)

### Get Hotel Statistics
```http
GET /api/hotels/{id}/stats/
```

**Response:**
```json
{
    "total_rooms": 25,
    "available_rooms": 15,
    "occupied_rooms": 10,
    "total_bookings": 120,
    "total_reservations": 150,
    "total_reviews": 45,
    "average_rating": 4.5
}
```

---

## Rooms

### List All Rooms
```http
GET /api/rooms/
```

**Query Parameters:**
- `hotel` - Filter by hotel ID
- `room_type` - Filter by type (standard, suite, deluxe, family)
- `bed_type` - Filter by bed type (single, double, queen, king)
- `status` - Filter by status (Available, Maintenance, Occupied)
- `max_guests` - Filter by guest capacity
- `search` - Search by room number or hotel name
- `ordering` - Sort by field (price, created_at, room_number)

**Response:**
```json
{
    "count": 100,
    "next": null,
    "previous": null,
    "results": [
        {
            "id": 1,
            "room_number": "101",
            "room_type": "deluxe",
            "room_type_display": "Deluxe",
            "bed_type": "king",
            "bed_type_display": "King",
            "price": "250.00",
            "status": "Available",
            "status_display": "Available",
            "max_guests": 2,
            "hotel": 1,
            "hotel_name": "Grand Hotel Accra",
            "star_rating": {
                "id": 5,
                "star": 5
            },
            "image": "https://res.cloudinary.com/...",
            "created_at": "2026-01-15T10:00:00"
        }
    ]
}
```

### Get Room Details
```http
GET /api/rooms/{id}/
```

### Get Available Rooms
```http
GET /api/rooms/available/
```

**Query Parameters:**
- `check_in` - Check-in date (YYYY-MM-DD)
- `check_out` - Check-out date (YYYY-MM-DD)

### Check Room Availability
```http
POST /api/rooms/{id}/check-availability/
```

**Request Body:**
```json
{
    "room_id": 1,
    "check_in_date": "2026-03-15",
    "check_out_date": "2026-03-20"
}
```

**Response:**
```json
{
    "available": true,
    "message": "Room is available for booking",
    "price_per_night": "250.00",
    "total_nights": 5,
    "total_price": 1250.00
}
```

---

## Bookings

### List User Bookings
```http
GET /api/bookings/
```
**Authentication Required**

### Get My Bookings
```http
GET /api/bookings/my-bookings/
```
**Authentication Required**

### Create Booking
```http
POST /api/bookings/
```
**Authentication Required**

**Request Body:**
```json
{
    "room_id": 1,
    "check_in_date": "2026-03-15",
    "check_out_date": "2026-03-20",
    "message": "Late check-in expected"
}
```

**Response:**
```json
{
    "id": 10,
    "guest": {
        "id": 5,
        "first_name": "John",
        "last_name": "Doe",
        "full_name": "John Doe",
        "email": "john@example.com",
        "phone_number": "+233123456789"
    },
    "room": {
        "id": 1,
        "room_number": "101",
        "room_type_display": "Deluxe",
        "hotel_name": "Grand Hotel Accra",
        "price": "250.00"
    },
    "check_in_date": "2026-03-15",
    "check_out_date": "2026-03-20",
    "message": "Late check-in expected",
    "total_price": "1250.00",
    "calculated_total": 1250.00,
    "nights": 5,
    "is_paid": false,
    "created_at": "2026-02-06T10:00:00"
}
```

### Get Booking Details
```http
GET /api/bookings/{id}/
```
**Authentication Required**

---

## Reservations

### List Reservations
```http
GET /api/reservations/
```
**Authentication Required**

**Query Parameters:**
- `status` - Filter by status (Pending, Confirmed, Checked In, Checked Out, Cancelled)
- `room` - Filter by room ID
- `check_in_date` - Filter by check-in date

### Get Upcoming Reservations
```http
GET /api/reservations/upcoming/
```
**Authentication Required**

### Get Past Reservations
```http
GET /api/reservations/past/
```
**Authentication Required**

### Create Reservation
```http
POST /api/reservations/
```
**Authentication Required** (Staff/Manager only)

**Request Body:**
```json
{
    "guest_id": 5,
    "room_id": 1,
    "first_name": "John",
    "last_name": "Doe",
    "email": "john@example.com",
    "phone_number": "+233123456789",
    "check_in_date": "2026-03-15",
    "check_out_date": "2026-03-20",
    "check_in_time": "15:00:00",
    "check_out_time": "11:00:00",
    "num_adults": 2,
    "num_children": 0,
    "num_guests": 2,
    "price_per_night_at_booking": "250.00",
    "total_price": "1250.00",
    "booking_source": "Online",
    "notes": "Guest requested upper floor"
}
```

---

## Guests

### List Guests
```http
GET /api/guests/
```
**Authentication Required**

### Get My Guest Profile
```http
GET /api/guests/me/
```
**Authentication Required**

### Get Guest Bookings
```http
GET /api/guests/{id}/bookings/
```
**Authentication Required**

### Get Guest Reservations
```http
GET /api/guests/{id}/reservations/
```
**Authentication Required**

---

## Reviews

### List Reviews
```http
GET /api/reviews/
```

### Get Hotel Reviews
```http
GET /api/reviews/hotel_reviews/?hotel_id=1
```

**Response:**
```json
{
    "reviews": [
        {
            "id": 1,
            "guest_name": "John Doe",
            "hotel_name": "Grand Hotel Accra",
            "rating": {
                "id": 5,
                "star": 5
            },
            "comment": "Excellent service and beautiful rooms!",
            "created_at": "2026-02-01T10:00:00"
        }
    ],
    "average_rating": 4.5,
    "total_reviews": 45
}
```

### Create Review
```http
POST /api/reviews/
```
**Authentication Required**

**Request Body:**
```json
{
    "reservation_id": 10,
    "rating_id": 5,
    "comment": "Excellent service and beautiful rooms!"
}
```

---

## Services

### List Services
```http
GET /api/services/
```

**Query Parameters:**
- `category` - Filter by category (RS, FB, WL, TR, etc.)
- `is_available` - Filter by availability

---

## Amenities

### List Amenities
```http
GET /api/amenities/
```

---

## Search

### Search Hotels
```http
GET /api/search/hotels/
```

**Query Parameters:**
- `q` - Search term
- `region` - Filter by region

### Search Rooms
```http
GET /api/search/rooms/
```

**Query Parameters:**
- `hotel` - Hotel ID
- `room_type` - Room type
- `min_price` - Minimum price
- `max_price` - Maximum price
- `max_guests` - Minimum guest capacity
- `check_in` - Check-in date (YYYY-MM-DD)
- `check_out` - Check-out date (YYYY-MM-DD)

---

## Leads (Contact Form)

### Submit Lead
```http
POST /api/leads/
```
**No Authentication Required**

**Request Body:**
```json
{
    "full_name": "John Doe",
    "email": "john@example.com",
    "phone": "+233123456789",
    "hotel_name": "My Hotel",
    "message": "I'm interested in partnering with BaseLink"
}
```

---

## Error Responses

### 400 Bad Request
```json
{
    "field_name": [
        "Error message"
    ]
}
```

### 401 Unauthorized
```json
{
    "detail": "Authentication credentials were not provided."
}
```

### 403 Forbidden
```json
{
    "detail": "You do not have permission to perform this action."
}
```

### 404 Not Found
```json
{
    "detail": "Not found."
}
```

### 500 Internal Server Error
```json
{
    "detail": "Internal server error."
}
```

---

## Pagination

All list endpoints support pagination with the following structure:

```json
{
    "count": 100,
    "next": "http://localhost:8000/api/endpoint/?page=2",
    "previous": null,
    "results": []
}
```

---

## Flutter Integration Examples

### 1. Setup HTTP Client with JWT

```dart
import 'package:http/http.dart' as http;
import 'dart:convert';

class ApiService {
  static const String baseUrl = 'http://localhost:8000/api';
  String? accessToken;
  
  Map<String, String> getHeaders() {
    return {
      'Content-Type': 'application/json',
      if (accessToken != null) 'Authorization': 'Bearer $accessToken',
    };
  }
  
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
      accessToken = data['access'];
      return data;
    } else {
      throw Exception('Failed to login');
    }
  }
  
  Future<List<dynamic>> getHotels() async {
    final response = await http.get(
      Uri.parse('$baseUrl/hotels/'),
      headers: getHeaders(),
    );
    
    if (response.statusCode == 200) {
      final data = jsonDecode(response.body);
      return data['results'];
    } else {
      throw Exception('Failed to load hotels');
    }
  }
  
  Future<Map<String, dynamic>> createBooking(Map<String, dynamic> bookingData) async {
    final response = await http.post(
      Uri.parse('$baseUrl/bookings/'),
      headers: getHeaders(),
      body: jsonEncode(bookingData),
    );
    
    if (response.statusCode == 201) {
      return jsonDecode(response.body);
    } else {
      throw Exception('Failed to create booking');
    }
  }
}
```

### 2. Check Room Availability

```dart
Future<bool> checkRoomAvailability(int roomId, String checkIn, String checkOut) async {
  final response = await http.post(
    Uri.parse('$baseUrl/rooms/$roomId/check-availability/'),
    headers: getHeaders(),
    body: jsonEncode({
      'room_id': roomId,
      'check_in_date': checkIn,
      'check_out_date': checkOut,
    }),
  );
  
  if (response.statusCode == 200) {
    final data = jsonDecode(response.body);
    return data['available'];
  }
  return false;
}
```

---

## Important Notes

1. **Token Expiry**: Access tokens expire after 24 hours. Use the refresh token endpoint to get new tokens.

2. **CORS**: The API is configured to accept requests from Flutter apps. Make sure CORS is properly configured for your domain in production.

3. **Date Format**: All dates should be in `YYYY-MM-DD` format.

4. **Cloudinary Images**: Image URLs are provided by Cloudinary and can be displayed directly in Flutter using `Image.network()`.

5. **Permissions**:
   - Public endpoints: Hotels (list/detail), Rooms (list/detail), Search, Leads
   - Authenticated: Bookings, Reservations, Guests, Reviews
   - Admin/Staff only: Hotel/Room creation and updates

6. **Rate Limiting**: Consider implementing rate limiting in production.

---

## Testing the API

You can test the API using:
1. **Swagger UI**: Navigate to `/api/docs/` in your browser
2. **ReDoc**: Navigate to `/api/redoc/` for beautiful documentation
3. **Postman**: Import the API endpoints
4. **curl**: Command-line testing

Example curl command:
```bash
curl -X POST http://localhost:8000/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{"username":"testuser","password":"testpass123"}'
```

---

## Support

For issues or questions, contact: esmondabban@gmail.com
