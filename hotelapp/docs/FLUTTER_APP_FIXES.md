# Flutter App Fixes - Images and Profile Editing

## Overview
This document outlines the fixes implemented to resolve image display issues and enable profile editing functionality for the Flutter mobile app.

## Issues Fixed

### 1. Image Display Issues ✅
**Problem:** Images were not displaying properly in the Flutter app.

**Root Cause:** The API serializers were returning CloudinaryField objects without proper URL serialization, making it difficult for the Flutter app to access the full image URLs.

**Solution:** Added `*_url` fields to all serializers that handle images:
- Profile images: Added `profile_url` field
- Hotel images: Added `logo_url` and `hotel_image_url` fields  
- Room images: Added `image_url` field
- Room additional images: Added `image_url` field

**Implementation:** Each serializer now includes a `SerializerMethodField` that extracts the full URL from CloudinaryField or ImageField objects.

### 2. Profile Editing ✅
**Problem:** Users could not edit their profile information from the Flutter app.

**Root Cause:** The `UserProfileView` API endpoint only supported GET requests, lacking PUT and PATCH methods for updates.

**Solution:** Enhanced the `UserProfileView` with full CRUD capabilities:
- GET: Retrieve user profile
- PUT: Full profile update
- PATCH: Partial profile update

## API Changes

### Updated Endpoints

#### 1. Profile Management
**Endpoint:** `/api/auth/profile/`

**GET** - Retrieve Profile
```http
GET /api/auth/profile/
Authorization: Bearer {access_token}
```

**Response:**
```json
{
    "user": {
        "id": 1,
        "username": "johndoe",
        "email": "john@example.com",
        "first_name": "John",
        "last_name": "Doe",
        "user_type": "Guest",
        "is_verified": true,
        "created_at": "2026-02-07T10:00:00"
    },
    "profile": {
        "id": 1,
        "user": {...},
        "first_name": "John",
        "last_name": "Doe",
        "profile": "profile/johndoe.jpg",
        "profile_url": "https://res.cloudinary.com/your-cloud/image/upload/v1234567890/profile/johndoe.jpg",
        "phone": "+1234567890",
        "email": "john@example.com",
        "gender": "M",
        "nationality": "USA",
        "address": "123 Main St, City"
    }
}
```

**PUT** - Full Profile Update
```http
PUT /api/auth/profile/
Authorization: Bearer {access_token}
Content-Type: multipart/form-data

{
    "first_name": "John",
    "last_name": "Doe",
    "phone": "+1234567890",
    "email": "john@example.com",
    "gender": "M",
    "nationality": "USA",
    "address": "123 Main St, City",
    "profile": <file>  // Optional: profile image file
}
```

**PATCH** - Partial Profile Update
```http
PATCH /api/auth/profile/
Authorization: Bearer {access_token}
Content-Type: multipart/form-data

{
    "phone": "+9876543210"  // Update only specific fields
}
```

**Response (PUT/PATCH):**
```json
{
    "user": {...},
    "profile": {...},
    "message": "Profile updated successfully"
}
```

#### 2. Hotels List
**Endpoint:** `/api/hotels/`

**New Fields in Response:**
```json
{
    "id": 1,
    "name": "Grand Hotel",
    "logo": "logos/grand_hotel.jpg",
    "logo_url": "https://res.cloudinary.com/.../logos/grand_hotel.jpg",
    "hotel_image": "hotel_images/grand_hotel_main.jpg",
    "hotel_image_url": "https://res.cloudinary.com/.../hotel_images/grand_hotel_main.jpg",
    ...
}
```

#### 3. Rooms List
**Endpoint:** `/api/rooms/`

**New Fields in Response:**
```json
{
    "id": 1,
    "room_number": "101",
    "image": "rooms/room_101.jpg",
    "image_url": "https://res.cloudinary.com/.../rooms/room_101.jpg",
    ...
}
```

#### 4. Room Details
**Endpoint:** `/api/rooms/{id}/`

**New Fields in Response:**
```json
{
    "id": 1,
    "room_number": "101",
    "image": "rooms/room_101.jpg",
    "image_url": "https://res.cloudinary.com/.../rooms/room_101.jpg",
    "additional_images": [
        {
            "id": 1,
            "room": 1,
            "image": "room_images/room_101_view1.jpg",
            "image_url": "https://res.cloudinary.com/.../room_images/room_101_view1.jpg"
        },
        ...
    ],
    ...
}
```

## Flutter Implementation Guide

### 1. Displaying Images

**Before (might fail):**
```dart
Image.network(room['image'])  // May not work with CloudinaryField
```

**After (recommended):**
```dart
// Use the new *_url fields
Image.network(
    room['image_url'] ?? room['image'],  // Fallback to image field if url not available
    errorBuilder: (context, error, stackTrace) {
        return Icon(Icons.broken_image);
    },
)
```

### 2. Profile Editing Example

```dart
import 'package:http/http.dart' as http;
import 'dart:convert';
import 'package:http_parser/http_parser.dart';

class ProfileService {
    final String baseUrl = 'https://your-api-url.com/api';
    
    // Get Profile
    Future<Map<String, dynamic>> getProfile(String accessToken) async {
        final response = await http.get(
            Uri.parse('$baseUrl/auth/profile/'),
            headers: {
                'Authorization': 'Bearer $accessToken',
            },
        );
        
        if (response.statusCode == 200) {
            return json.decode(response.body);
        } else {
            throw Exception('Failed to load profile');
        }
    }
    
    // Update Profile (with image)
    Future<Map<String, dynamic>> updateProfile({
        required String accessToken,
        String? firstName,
        String? lastName,
        String? phone,
        String? email,
        String? gender,
        String? nationality,
        String? address,
        File? profileImage,
    }) async {
        var request = http.MultipartRequest(
            'PATCH',
            Uri.parse('$baseUrl/auth/profile/'),
        );
        
        // Add headers
        request.headers['Authorization'] = 'Bearer $accessToken';
        
        // Add fields
        if (firstName != null) request.fields['first_name'] = firstName;
        if (lastName != null) request.fields['last_name'] = lastName;
        if (phone != null) request.fields['phone'] = phone;
        if (email != null) request.fields['email'] = email;
        if (gender != null) request.fields['gender'] = gender;
        if (nationality != null) request.fields['nationality'] = nationality;
        if (address != null) request.fields['address'] = address;
        
        // Add image file if provided
        if (profileImage != null) {
            request.files.add(
                await http.MultipartFile.fromPath(
                    'profile',
                    profileImage.path,
                    contentType: MediaType('image', 'jpeg'),
                ),
            );
        }
        
        // Send request
        var streamedResponse = await request.send();
        var response = await http.Response.fromStream(streamedResponse);
        
        if (response.statusCode == 200) {
            return json.decode(response.body);
        } else {
            throw Exception('Failed to update profile: ${response.body}');
        }
    }
}
```

### 3. Image Caching (Recommended)

Use a package like `cached_network_image` for better performance:

```dart
import 'package:cached_network_image/cached_network_image.dart';

CachedNetworkImage(
    imageUrl: room['image_url'],
    placeholder: (context, url) => CircularProgressIndicator(),
    errorWidget: (context, url, error) => Icon(Icons.error),
)
```

## Testing Checklist

### Backend Testing (using Postman or curl)

1. **Test Profile GET:**
```bash
curl -X GET \
  http://localhost:8000/api/auth/profile/ \
  -H 'Authorization: Bearer YOUR_ACCESS_TOKEN'
```

2. **Test Profile PATCH (update phone):**
```bash
curl -X PATCH \
  http://localhost:8000/api/auth/profile/ \
  -H 'Authorization: Bearer YOUR_ACCESS_TOKEN' \
  -F 'phone=+1234567890'
```

3. **Test Profile PATCH (update image):**
```bash
curl -X PATCH \
  http://localhost:8000/api/auth/profile/ \
  -H 'Authorization: Bearer YOUR_ACCESS_TOKEN' \
  -F 'profile=@/path/to/image.jpg'
```

4. **Test Hotels API (check image URLs):**
```bash
curl -X GET http://localhost:8000/api/hotels/
```

5. **Test Rooms API (check image URLs):**
```bash
curl -X GET http://localhost:8000/api/rooms/
```

### Flutter Testing

1. **Test Image Display:**
   - Verify hotel logos display correctly
   - Verify hotel images display correctly
   - Verify room images display correctly
   - Verify profile images display correctly

2. **Test Profile Editing:**
   - Update individual fields (phone, address, etc.)
   - Update profile image
   - Verify changes persist after app restart
   - Test error handling for invalid data

## Migration Notes

### For Existing Flutter Code

1. **Update Image Display Logic:**
   - Replace all `Image.network(item['image'])` with `Image.network(item['image_url'] ?? item['image'])`
   - Add proper error handling for failed image loads

2. **Implement Profile Editing:**
   - Add profile editing form/screen
   - Implement image picker for profile photo
   - Use PATCH for partial updates to avoid overwriting unchanged fields

3. **Update API Models:**
   - Add `*_url` fields to your Dart model classes
   - Update JSON deserialization to include new fields

### Example Dart Model Update

```dart
class Hotel {
    final int id;
    final String name;
    final String? logo;
    final String? logoUrl;  // New field
    final String? hotelImage;
    final String? hotelImageUrl;  // New field
    
    Hotel({
        required this.id,
        required this.name,
        this.logo,
        this.logoUrl,
        this.hotelImage,
        this.hotelImageUrl,
    });
    
    factory Hotel.fromJson(Map<String, dynamic> json) {
        return Hotel(
            id: json['id'],
            name: json['name'],
            logo: json['logo'],
            logoUrl: json['logo_url'],
            hotelImage: json['hotel_image'],
            hotelImageUrl: json['hotel_image_url'],
        );
    }
    
    // Use this method to get the best available image URL
    String? get bestLogoUrl => logoUrl ?? logo;
    String? get bestImageUrl => hotelImageUrl ?? hotelImage;
}
```

## Important Notes

1. **Authentication Required:** All profile update operations require a valid JWT access token in the Authorization header.

2. **Image Upload:** When uploading images, use `multipart/form-data` content type.

3. **Field Validation:**
   - Email must be valid format
   - Phone number accepts various formats
   - Gender: "M" for Male, "F" for Female
   
4. **Partial Updates:** Use PATCH instead of PUT when updating only specific fields to avoid accidentally clearing other fields.

5. **Profile Creation:** If a user doesn't have a profile, it will be automatically created on the first update request.

6. **Image URLs:** All `*_url` fields provide full absolute URLs ready to be used in Flutter's `Image.network()` widget.

## Performance Tips

1. **Image Caching:** Use `cached_network_image` package to cache images and reduce network calls
2. **Lazy Loading:** Implement pagination for large lists of hotels/rooms
3. **Optimized Images:** Cloudinary automatically optimizes images; consider using transformation parameters in URLs for thumbnails
4. **Error Handling:** Always implement proper error handling for network requests and image loading

## Support

If you encounter any issues:
1. Check the server logs for error messages
2. Verify JWT token is valid and not expired
3. Ensure proper headers are set (Authorization, Content-Type)
4. Check image file size limits (Cloudinary may have restrictions)

## Summary

✅ **Images:** All image fields now include corresponding `*_url` fields with full URLs  
✅ **Profile Editing:** PUT and PATCH methods added to `/api/auth/profile/` endpoint  
✅ **Profile Creation:** Automatic profile creation if it doesn't exist  
✅ **User Updates:** user's first_name, last_name, and email can also be updated  
✅ **Compatibility:** All changes are backward compatible; old code will still work
