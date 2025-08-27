# HR Dashboard API Documentation

## Overview
This API provides comprehensive HR Dashboard functionality for managing job postings, applications, and interviews with detailed statistics and analytics.

## Base URL
```
http://localhost:8000/api/
```

## Authentication
All endpoints require authentication. Include the JWT token in the Authorization header:
```
Authorization: Bearer <your_jwt_token>
```

## Endpoints

### 1. HR Dashboard Statistics
**GET** `/api/hr/dashboard/stats/`

Returns comprehensive statistics for the HR dashboard including overview metrics, recent activity, and breakdowns.

**Example Response:**
```json
{
  "overview": {
    "active_jobs": 12,
    "total_jobs": 25,
    "total_applications": 156,
    "scheduled_interviews": 15,
    "response_rate": 68.5,
    "response_rate_change": 5.2,
    "interviews_change": 3
  },
  "recent_activity": {
    "recent_applications": [
      {
        "id": 45,
        "job": {
          "id": 8,
          "title": "Senior Frontend Developer",
          "department": "Engineering"
        },
        "applicant": {
          "id": 23,
          "first_name": "Sarah",
          "last_name": "Johnson",
          "email": "sarah.johnson@email.com"
        },
        "status": "shortlisted",
        "applied_at": "2025-08-27T10:30:00Z"
      }
    ],
    "recent_meetings": [
      {
        "id": 12,
        "title": "Technical Interview - Sarah Johnson",
        "meeting_type": "technical_interview",
        "start_time": "2025-08-28T14:00:00Z",
        "status": "scheduled",
        "applicant_name": "Sarah Johnson",
        "job_title": "Senior Frontend Developer",
        "created_by": "Jane Smith"
      }
    ]
  },
  "breakdowns": {
    "application_status": [
      {"status": "pending", "count": 45},
      {"status": "reviewing", "count": 23},
      {"status": "shortlisted", "count": 18},
      {"status": "interview_scheduled", "count": 12},
      {"status": "selected", "count": 8},
      {"status": "rejected", "count": 50}
    ],
    "job_status": [
      {"status": "draft", "count": 5},
      {"status": "active", "count": 12},
      {"status": "closed", "count": 8}
    ],
    "meeting_type": [
      {"meeting_type": "hr_screening", "count": 8},
      {"meeting_type": "technical_interview", "count": 12},
      {"meeting_type": "final_interview", "count": 5},
      {"meeting_type": "team_discussion", "count": 2}
    ]
  },
  "trends": {
    "applications_this_month": 45,
    "applications_last_month": 38,
    "this_week_interviews": 8,
    "last_week_interviews": 5
  }
}
```

### 2. HR Dashboard Jobs
**GET** `/api/hr/dashboard/jobs/`

Returns jobs with application statistics and filtering options.

**Query Parameters:**
- `status`: Filter by job status (draft, active, closed)
- `department`: Filter by department

**Example Response:**
```json
{
  "summary": {
    "total_jobs": 25,
    "active_jobs": 12,
    "draft_jobs": 5,
    "closed_jobs": 8,
    "total_applications": 156
  },
  "jobs": [
    {
      "id": 8,
      "title": "Senior Frontend Developer",
      "department": "Engineering",
      "location": "San Francisco, CA",
      "employment_type": "full_time",
      "status": "active",
      "created_at": "2025-07-15T09:00:00Z",
      "application_count": 23,
      "recent_applications": [
        {
          "id": 45,
          "applicant": {
            "first_name": "Sarah",
            "last_name": "Johnson",
            "email": "sarah.johnson@email.com"
          },
          "status": "shortlisted",
          "applied_at": "2025-08-27T10:30:00Z"
        }
      ]
    }
  ]
}
```

### 3. HR Dashboard Applications
**GET** `/api/hr/dashboard/applications/`

Returns applications with filtering and summary statistics.

**Query Parameters:**
- `status`: Filter by application status
- `job`: Filter by job ID

**Example Response:**
```json
{
  "summary": {
    "total_applications": 156,
    "pending": 45,
    "reviewing": 23,
    "shortlisted": 18,
    "interview_scheduled": 12,
    "selected": 8,
    "rejected": 50
  },
  "applications": [
    {
      "id": 45,
      "job": {
        "id": 8,
        "title": "Senior Frontend Developer",
        "department": "Engineering"
      },
      "applicant": {
        "id": 23,
        "first_name": "Sarah",
        "last_name": "Johnson",
        "email": "sarah.johnson@email.com"
      },
      "cover_letter": "I am excited to apply for the Senior Frontend Developer position...",
      "status": "shortlisted",
      "applied_at": "2025-08-27T10:30:00Z",
      "updated_at": "2025-08-27T15:45:00Z"
    }
  ]
}
```

## Dashboard Cards Data Mapping

### Active Jobs Card
```javascript
// From overview.active_jobs and overview.total_jobs
const activeJobs = response.overview.active_jobs;
const totalJobs = response.overview.total_jobs;
```

### Total Applications Card
```javascript
// From overview.total_applications
const totalApplications = response.overview.total_applications;
```

### Interviews Scheduled Card
```javascript
// From overview.scheduled_interviews and overview.interviews_change
const scheduledInterviews = response.overview.scheduled_interviews;
const interviewsChange = response.overview.interviews_change;
```

### Response Rate Card
```javascript
// From overview.response_rate and overview.response_rate_change
const responseRate = response.overview.response_rate;
const responseRateChange = response.overview.response_rate_change;
```

## Usage Examples

### Get Dashboard Statistics
```bash
curl -X GET http://localhost:8000/api/hr/dashboard/stats/ \
  -H "Authorization: Bearer <your_token>"
```

### Get Jobs with Filtering
```bash
curl -X GET "http://localhost:8000/api/hr/dashboard/jobs/?status=active&department=Engineering" \
  -H "Authorization: Bearer <your_token>"
```

### Get Applications with Filtering
```bash
curl -X GET "http://localhost:8000/api/hr/dashboard/applications/?status=shortlisted" \
  -H "Authorization: Bearer <your_token>"
```

## Frontend Integration

### React/Next.js Example
```javascript
import { useState, useEffect } from 'react';

const HRDashboard = () => {
  const [dashboardStats, setDashboardStats] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchDashboardStats = async () => {
      try {
        const response = await fetch('/api/hr/dashboard/stats/', {
          headers: {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json',
          },
        });
        const data = await response.json();
        setDashboardStats(data);
      } catch (error) {
        console.error('Error fetching dashboard stats:', error);
      } finally {
        setLoading(false);
      }
    };

    fetchDashboardStats();
  }, []);

  if (loading) return <div>Loading...</div>;

  return (
    <div className="space-y-6">
      <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-6">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Active Jobs</CardTitle>
            <Briefcase className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{dashboardStats.overview.active_jobs}</div>
            <p className="text-xs text-muted-foreground">
              out of {dashboardStats.overview.total_jobs} total jobs
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Total Applications</CardTitle>
            <Users className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{dashboardStats.overview.total_applications}</div>
            <p className="text-xs text-muted-foreground">across all job postings</p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Interviews Scheduled</CardTitle>
            <Calendar className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{dashboardStats.overview.scheduled_interviews}</div>
            <p className="text-xs text-muted-foreground">
              {dashboardStats.overview.interviews_change > 0 ? '+' : ''}
              {dashboardStats.overview.interviews_change} this week
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Response Rate</CardTitle>
            <TrendingUp className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{dashboardStats.overview.response_rate}%</div>
            <p className="text-xs text-muted-foreground">
              {dashboardStats.overview.response_rate_change > 0 ? '+' : ''}
              {dashboardStats.overview.response_rate_change}% from last month
            </p>
          </CardContent>
        </Card>
      </div>
    </div>
  );
};
```

## Error Responses

### 403 Forbidden
```json
{
  "detail": "You do not have permission to perform this action."
}
```

### 401 Unauthorized
```json
{
  "detail": "Authentication credentials were not provided."
}
```

This API provides a complete solution for HR dashboard functionality with comprehensive statistics, filtering, and real-time data for effective HR management.
