# Inventory Management System API Documentation

## Base URL
```
http://your-domain.com/api/v1/
```

## Available Endpoints

### 1. Users API
- **GET** `/users/` - Get all users
- **GET** `/users/{id}/` - Get specific user
- **POST** `/users/` - Create new user
- **PUT** `/users/{id}/` - Update user
- **DELETE** `/users/{id}/` - Delete user

### 2. Equipment API
- **GET** `/equipment/` - Get all equipment
- **GET** `/equipment/{id}/` - Get specific equipment
- **POST** `/equipment/` - Create new equipment
- **PUT** `/equipment/{id}/` - Update equipment
- **DELETE** `/equipment/{id}/` - Delete equipment

#### Equipment Custom Endpoints:
- **GET** `/equipment/in_store/` - Get equipment currently in store
- **GET** `/equipment/in_field/` - Get equipment currently in field
- **GET** `/equipment/returning/` - Get equipment currently returning
- **GET** `/equipment/{id}/accessories/` - Get accessories for specific equipment
- **GET** `/equipment/{id}/history/` - Get history for specific equipment

### 3. Accessories API
- **GET** `/accessories/` - Get all accessories
- **GET** `/accessories/{id}/` - Get specific accessory
- **POST** `/accessories/` - Create new accessory
- **PUT** `/accessories/{id}/` - Update accessory
- **DELETE** `/accessories/{id}/` - Delete accessory

#### Accessories Custom Endpoints:
- **GET** `/accessories/in_store/` - Get accessories currently in store
- **GET** `/accessories/in_use/` - Get accessories currently in use
- **GET** `/accessories/returning/` - Get accessories currently returning
- **GET** `/accessories/standalone/` - Get standalone accessories (not linked to equipment)
- **GET** `/accessories/{id}/history/` - Get history for specific accessory

### 4. Personnel API
- **GET** `/personnel/` - Get all personnel
- **GET** `/personnel/{id}/` - Get specific personnel
- **POST** `/personnel/` - Create new personnel
- **PUT** `/personnel/{id}/` - Update personnel
- **DELETE** `/personnel/{id}/` - Delete personnel

#### Personnel Custom Endpoints:
- **GET** `/personnel/active/` - Get active personnel
- **GET** `/personnel/{id}/chainmen/` - Get chainmen assigned to specific personnel

### 5. Chainmen API
- **GET** `/chainmen/` - Get all chainmen
- **GET** `/chainmen/{id}/` - Get specific chainman
- **POST** `/chainmen/` - Create new chainman
- **PUT** `/chainmen/{id}/` - Update chainman
- **DELETE** `/chainmen/{id}/` - Delete chainman

#### Chainmen Custom Endpoints:
- **GET** `/chainmen/active/` - Get active chainmen
- **GET** `/chainmen/unassigned/` - Get unassigned chainmen

### 6. Equipment History API (Read Only)
- **GET** `/equipment-history/` - Get all equipment history
- **GET** `/equipment-history/{id}/` - Get specific history entry
- **GET** `/equipment-history/recent/` - Get recent equipment history (last 50 entries)

### 7. Accessory History API (Read Only)
- **GET** `/accessory-history/` - Get all accessory history
- **GET** `/accessory-history/{id}/` - Get specific history entry
- **GET** `/accessory-history/recent/` - Get recent accessory history (last 50 entries)

## Example API Calls

### Get all equipment in store:
```bash
curl -X GET http://localhost:8000/api/v1/equipment/in_store/
```

### Get accessories for equipment ID 1:
```bash
curl -X GET http://localhost:8000/api/v1/equipment/1/accessories/
```

### Create new equipment:
```bash
curl -X POST http://localhost:8000/api/v1/equipment/ \
  -H "Content-Type: application/json" \
  -d '{
    "name": "GPS Receiver (Base)",
    "supplier": "Hi Target",
    "serial_number": "GPS123456",
    "condition": "Good",
    "status": "In Store"
  }'
```

### Create new accessory:
```bash
curl -X POST http://localhost:8000/api/v1/accessories/ \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Tripod",
    "manufacturer": "Hi Target",
    "condition": "Good",
    "status": "Good",
    "return_status": "In Store"
  }'
```

## Response Format
All API responses are in JSON format with the following structure:

### Success Response:
```json
{
  "id": 1,
  "name": "GPS Receiver (Base)",
  "supplier": "Hi Target",
  "serial_number": "GPS123456",
  "condition": "Good",
  "status": "In Store",
  "chief_surveyor": null,
  "chief_surveyor_detail": null
}
```

### List Response:
```json
[
  {
    "id": 1,
    "name": "GPS Receiver (Base)",
    "supplier": "Hi Target",
    "serial_number": "GPS123456",
    "condition": "Good",
    "status": "In Store"
  },
  {
    "id": 2,
    "name": "Total Station",
    "supplier": "Topcon",
    "serial_number": "TS789012",
    "condition": "New",
    "status": "In Field"
  }
]
```

### Error Response:
```json
{
  "field_name": ["This field is required."]
}
```

## Authentication
Currently, no authentication is required for API access. All endpoints are publicly accessible.

## Filtering and Pagination
The API supports Django REST Framework's built-in filtering and pagination features. You can use query parameters like:
- `?page=2` for pagination
- `?search=term` for searching (where supported)
- `?ordering=field_name` for ordering results
