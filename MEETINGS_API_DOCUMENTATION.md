# Meetings API Documentation

## Overview
This API provides comprehensive meeting management functionality for the WellFound clone application. It handles meeting creation, scheduling, attendee management, and provides various filtering and statistics capabilities.

## Base URL
```
http://localhost:8000/api/meetings/
```

## Authentication
All endpoints require authentication. Include the JWT token in the Authorization header:
```
Authorization: Bearer <your_jwt_token>
```

## Endpoints

### 1. List and Create Meetings
**GET/POST** `/api/meetings/`

#### GET - List Meetings
Returns a list of meetings with advanced filtering options.

**Query Parameters:**
- `status`: Filter by meeting status (scheduled, completed, cancelled, rescheduled)
- `meeting_type`: Filter by meeting type (hr_screening, technical_interview, final_interview, team_discussion)
- `application`: Filter by application ID
- `created_by`: Filter by creator ID
- `search`: Search in title and description
- `ordering`: Order by field (start_time, end_time, created_at, title)
- `upcoming`: Filter upcoming meetings (true/false)
- `past`: Filter past meetings (true/false)
- `today`: Filter today's meetings (true/false)
- `this_week`: Filter this week's meetings (true/false)

**Example Request:**
```bash
GET /api/meetings/?upcoming=true&meeting_type=technical_interview&ordering=-start_time
```

**Example Response:**
```json
{
  "count": 2,
  "next": null,
  "previous": null,
  "results": [
    {
      "id": 1,
      "title": "DevOps Technical Interview",
      "meeting_type": "technical_interview",
      "start_time": "2025-08-28T05:00:00Z",
      "end_time": "2025-08-28T05:30:00Z",
      "status": "scheduled",
      "attendees_count": 3,
      "application_details": {
        "id": 2,
        "job_title": "DevOps Engineer",
        "applicant_name": "John Doe",
        "status": "shortlisted"
      },
      "duration_minutes": 30,
      "is_upcoming": true,
      "created_at": "2025-08-27T05:02:46Z"
    }
  ]
}
```

#### POST - Create Meeting
Creates a new meeting.

**Request Body:**
```json
{
  "application": 2,
  "title": "DevOps Technical Interview",
  "description": "Technical interview for DevOps position",
  "meeting_type": "technical_interview",
  "start_time": "2025-08-28T05:00:00.000Z",
  "end_time": "2025-08-28T05:30:00.000Z",
  "meeting_link": "https://meet.google.com/fuw-arba-ikd?pli=1",
  "attendee_ids": [5, 6, 7]
}
```

**Required Fields:**
- `application`: Application ID
- `title`: Meeting title
- `meeting_type`: Type of meeting
- `start_time`: Start time (ISO format)
- `end_time`: End time (ISO format)

**Optional Fields:**
- `description`: Meeting description
- `meeting_link`: Meeting URL
- `attendee_ids`: Array of user IDs to invite

**Example Response:**
```json
{
  "id": 1,
  "application": 2,
  "application_details": {
    "id": 2,
    "job_title": "DevOps Engineer",
    "applicant_name": "John Doe",
    "status": "shortlisted"
  },
  "title": "DevOps Technical Interview",
  "description": "Technical interview for DevOps position",
  "meeting_type": "technical_interview",
  "start_time": "2025-08-28T05:00:00Z",
  "end_time": "2025-08-28T05:30:00Z",
  "meeting_link": "https://meet.google.com/fuw-arba-ikd?pli=1",
  "status": "scheduled",
  "attendees": [
    {
      "id": 5,
      "email": "interviewer@company.com",
      "first_name": "Jane",
      "last_name": "Smith",
      "full_name": "Jane Smith"
    }
  ],
  "created_by": 1,
  "created_by_details": {
    "id": 1,
    "email": "hr@company.com",
    "first_name": "HR",
    "last_name": "Manager",
    "full_name": "HR Manager"
  },
  "created_at": "2025-08-27T05:02:46Z",
  "updated_at": "2025-08-27T05:02:46Z",
  "duration_minutes": 30,
  "is_upcoming": true,
  "is_past": false
}
```

### 2. Meeting Detail
**GET/PUT/PATCH/DELETE** `/api/meetings/{id}/`

#### GET - Retrieve Meeting
Returns detailed information about a specific meeting.

**Example Response:**
```json
{
  "id": 1,
  "application": 2,
  "application_details": {
    "id": 2,
    "job_title": "DevOps Engineer",
    "applicant_name": "John Doe",
    "status": "shortlisted"
  },
  "title": "DevOps Technical Interview",
  "description": "Technical interview for DevOps position",
  "meeting_type": "technical_interview",
  "start_time": "2025-08-28T05:00:00Z",
  "end_time": "2025-08-28T05:30:00Z",
  "meeting_link": "https://meet.google.com/fuw-arba-ikd?pli=1",
  "status": "scheduled",
  "attendees": [
    {
      "id": 5,
      "email": "interviewer@company.com",
      "first_name": "Jane",
      "last_name": "Smith",
      "full_name": "Jane Smith"
    }
  ],
  "created_by": 1,
  "created_by_details": {
    "id": 1,
    "email": "hr@company.com",
    "first_name": "HR",
    "last_name": "Manager",
    "full_name": "HR Manager"
  },
  "created_at": "2025-08-27T05:02:46Z",
  "updated_at": "2025-08-27T05:02:46Z",
  "duration_minutes": 30,
  "is_upcoming": true,
  "is_past": false
}
```

#### PUT/PATCH - Update Meeting
Updates meeting information. If start_time or end_time is changed, status automatically becomes 'rescheduled'.

**Request Body:**
```json
{
  "title": "Updated DevOps Technical Interview",
  "description": "Updated description",
  "start_time": "2025-08-29T05:00:00.000Z",
  "end_time": "2025-08-29T05:30:00.000Z",
  "attendee_ids": [5, 6, 8]
}
```

### 3. Meeting Management

#### Reschedule Meeting
**POST** `/api/meetings/{id}/reschedule/`

Reschedules a meeting with new start and end times or scheduled date.

**Request Body (Option 1 - Start/End Times):**
```json
{
  "start_time": "2025-08-29T05:00:00.000Z",
  "end_time": "2025-08-29T05:30:00.000Z",
  "notes": "Rescheduled due to interviewer availability"
}
```

**Request Body (Option 2 - Scheduled Date):**
```json
{
  "scheduled_date": "2025-08-30T06:48:00.000Z",
  "notes": "Rescheduled due to interviewer availability"
}
```

**Note:** When using `scheduled_date`, the system automatically sets a default 30-minute duration. You can also provide optional `notes` for reschedule reasons.

**Example Response:**
```json
{
  "message": "Meeting rescheduled successfully",
  "meeting": {
    "id": 1,
    "status": "rescheduled",
    "start_time": "2025-08-29T05:00:00Z",
    "end_time": "2025-08-29T05:30:00Z"
  }
}
```

#### Cancel Meeting
**POST** `/api/meetings/{id}/cancel/`

Cancels a meeting.

**Example Response:**
```json
{
  "message": "Meeting cancelled successfully",
  "meeting": {
    "id": 1,
    "status": "cancelled"
  }
}
```

#### Complete Meeting
**POST** `/api/meetings/{id}/complete/`

Marks a meeting as completed.

**Example Response:**
```json
{
  "message": "Meeting marked as completed",
  "meeting": {
    "id": 1,
    "status": "completed"
  }
}
```

### 4. Attendee Management

#### Add Attendee
**POST** `/api/meetings/{id}/add-attendee/`

Adds a new attendee to the meeting.

**Request Body:**
```json
{
  "attendee_id": 8
}
```

**Example Response:**
```json
{
  "message": "John Doe added to meeting",
  "meeting": {
    "id": 1,
    "attendees": [...]
  }
}
```

#### Remove Attendee
**POST** `/api/meetings/{id}/remove-attendee/`

Removes an attendee from the meeting (cannot remove applicant or creator).

**Request Body:**
```json
{
  "attendee_id": 8
}
```

**Example Response:**
```json
{
  "message": "John Doe removed from meeting",
  "meeting": {
    "id": 1,
    "attendees": [...]
  }
}
```

### 5. Statistics
**GET** `/api/meetings/stats/`

Returns meeting statistics for the authenticated user.

**Example Response:**
```json
{
  "total_meetings": 15,
  "upcoming_meetings": 5,
  "past_meetings": 8,
  "today_meetings": 2,
  "this_week_meetings": 7,
  "by_status": {
    "scheduled": 5,
    "completed": 8,
    "cancelled": 1,
    "rescheduled": 1
  },
  "by_type": {
    "hr_screening": 3,
    "technical_interview": 8,
    "final_interview": 3,
    "team_discussion": 1
  }
}
```

## Meeting Types
- `hr_screening`: HR Screening
- `technical_interview`: Technical Interview
- `final_interview`: Final Interview
- `team_discussion`: Team Discussion

## Meeting Statuses
- `scheduled`: Scheduled
- `completed`: Completed
- `cancelled`: Cancelled
- `rescheduled`: Rescheduled

## Validation Rules
1. End time must be after start time
2. Start time cannot be in the past
3. Applicant and creator are automatically added as attendees
4. Cannot remove applicant or creator from attendees
5. Meeting status automatically changes to 'rescheduled' when times are modified

## Error Responses

### 400 Bad Request
```json
{
  "error": "End time must be after start time"
}
```

### 404 Not Found
```json
{
  "error": "Meeting not found"
}
```

### 403 Forbidden
```json
{
  "detail": "You do not have permission to perform this action."
}
```

## Usage Examples

### Create a Technical Interview
```bash
curl -X POST http://localhost:8000/api/meetings/ \
  -H "Authorization: Bearer <your_token>" \
  -H "Content-Type: application/json" \
  -d '{
    "application": 2,
    "title": "DevOps Technical Interview",
    "description": "Technical interview for DevOps position",
    "meeting_type": "technical_interview",
    "start_time": "2025-08-28T05:00:00.000Z",
    "end_time": "2025-08-28T05:30:00.000Z",
    "meeting_link": "https://meet.google.com/fuw-arba-ikd?pli=1",
    "attendee_ids": [5, 6, 7]
  }'
```

### Get Upcoming Meetings
```bash
curl -X GET "http://localhost:8000/api/meetings/?upcoming=true&ordering=-start_time" \
  -H "Authorization: Bearer <your_token>"
```

### Reschedule a Meeting
```bash
curl -X POST http://localhost:8000/api/meetings/1/reschedule/ \
  -H "Authorization: Bearer <your_token>" \
  -H "Content-Type: application/json" \
  -d '{
    "start_time": "2025-08-29T05:00:00.000Z",
    "end_time": "2025-08-29T05:30:00.000Z"
  }'
```

This API provides a complete solution for meeting management with proper validation, error handling, and comprehensive functionality.
