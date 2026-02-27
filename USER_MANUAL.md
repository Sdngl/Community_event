# CrowdConnect - User Manual

A comprehensive guide for users of the CrowdConnect Event Management System.

---

## Table of Contents

1. [Introduction](#1-introduction)
2. [Getting Started](#2-getting-started)
3. [User Roles](#3-user-roles)
4. [Registration & Login](#4-registration--login)
5. [Event Discovery](#5-event-discovery)
6. [Event Registration](#6-event-registration)
7. [Managing Your Events](#7-managing-your-events)
8. [User Dashboard](#8-user-dashboard)
9. [Administrator Features](#9-administrator-features)
10. [Troubleshooting](#10-troubleshooting)

---

## 1. Introduction

**CrowdConnect** is a web-based Event Management System that allows users to:

- Browse and discover community events
- Register for events they're interested in
- Create and manage their own events (for organizers)
- Administer the platform (for administrators)

---

## 2. Getting Started

### 2.1 System Requirements

| Requirement | Specification                                      |
| ----------- | -------------------------------------------------- |
| Browser     | Modern web browser (Chrome, Firefox, Safari, Edge) |
| Internet    | Active internet connection                         |
| JavaScript  | Must be enabled                                    |
| Cookies     | Must be enabled for session management             |

### 2.2 Accessing the Application

1. Open your web browser
2. Navigate to: `http://localhost:8000` (development) or your deployed URL
3. You will see the home page with upcoming events

---

## 3. User Roles

CrowdConnect uses a role-based access control system with three user types:

| Role          | Permissions                                                   |
| ------------- | ------------------------------------------------------------- |
| **User**      | Browse events, register for events, view dashboard            |
| **Organizer** | All User permissions + Create events, edit/delete own events  |
| **Admin**     | Full access: manage users, manage all events, view statistics |

---

## 4. Registration & Login

### 4.1 Creating an Account

1. Click **Register** in the navigation menu
2. Fill in the registration form:
   - **Username**: 3-80 characters (must be unique)
   - **Email**: Valid email address (must be unique)
   - **Password**: At least 6 characters
   - **Confirm Password**: Must match password
   - **First Name**: (Optional)
   - **Last Name**: (Optional)
3. Click **Register**
4. You will be redirected to the login page
5. Log in with your new credentials

### 4.2 Logging In

1. Click **Login** in the navigation menu
2. Enter your **Username or Email**
3. Enter your **Password**
4. Optionally check **Remember Me** to stay logged in
5. Click **Login**

### 4.3 Logging Out

1. Click your username in the navigation bar
2. Click **Logout**
3. You will be logged out and redirected to the home page

---

## 5. Event Discovery

### 5.1 Browsing Events

The **Events** page (`/events`) displays all upcoming published events.

**Features:**

- Events are shown in a card format with:
  - Event image
  - Event title
  - Date and time
  - Location
  - Category badge
  - Available spots indicator

### 5.2 Filtering Events

You can filter events using the search bar on the Events page:

| Filter         | How to Use                                                               |
| -------------- | ------------------------------------------------------------------------ |
| **Search**     | Type in the search box to find events by title or description            |
| **Category**   | Select a category from the dropdown (Workshop, Conference, Meetup, etc.) |
| **Location**   | Filter by venue/location                                                 |
| **Date Range** | Set start and end dates                                                  |

### 5.3 Viewing Event Details

Click on any event card to view its full details:

- Full description
- Organizer information
- Registration deadline
- Capacity and availability
- Location map (if available)

---

## 6. Event Registration

### 6.1 Registering for an Event

1. Log in to your account
2. Navigate to the event you want to attend
3. Click **Register** button
4. You will see a confirmation message
5. The event will appear in your **Registered Events**

### 6.2 Registration Rules

| Rule                  | Description                                  |
| --------------------- | -------------------------------------------- |
| **Login Required**    | You must be logged in to register            |
| **Registration Open** | Registration must be before the deadline     |
| **Capacity**          | Event must have available spots              |
| **Not Your Event**    | You cannot register for your own event       |
| **No Duplicates**     | You cannot register twice for the same event |

### 6.3 Cancelling Registration

1. Go to **My Events** → **Registered Events**
2. Find the event you want to cancel
3. Click **Cancel Registration**
4. Confirm the cancellation
5. Your spot will be released

---

## 7. Managing Your Events

### 7.1 Creating an Event (Organizers Only)

> **Note:** Only users with the Organizer or Admin role can create events.

1. Log in as an organizer
2. Navigate to **Events** → **Create Event**
3. Fill in the event form:

| Field                 | Description            | Required |
| --------------------- | ---------------------- | -------- |
| Title                 | Event name             | Yes      |
| Description           | Full event details     | Yes      |
| Location              | Venue or "Online"      | Yes      |
| Event Date            | Date and time of event | Yes      |
| Registration Deadline | Last date to register  | No       |
| Capacity              | Maximum attendees      | Yes      |
| Category              | Event type             | Yes      |
| Status                | Draft or Published     | Yes      |

4. Click **Create Event**
5. Your event will be created (as Draft or Published based on status)

### 7.2 Editing an Event

1. Go to **My Events** (for organizers)
2. Find the event you created
3. Click **Edit**
4. Modify the details
5. Click **Update Event**

### 7.3 Deleting an Event

1. Go to **My Events**
2. Find your event
3. Click **Delete**
4. Confirm deletion
5. The event will be permanently removed

---

## 8. User Dashboard

### 8.1 Accessing Your Dashboard

Click on your username in the navigation bar, then select **Dashboard**.

### 8.2 Dashboard Features

Your dashboard shows:

| Section               | Description                        |
| --------------------- | ---------------------------------- |
| **Profile Overview**  | Your account information           |
| **Registered Events** | Events you've registered for       |
| **My Events**         | Events you've created (organizers) |
| **Statistics**        | Your activity summary              |

### 8.3 Editing Your Profile

1. Go to **Dashboard** → **Edit Profile**
2. Update your information:
   - First Name
   - Last Name
3. Click **Update Profile**

### 8.4 Changing Your Password

1. Go to **Dashboard** → **Change Password**
2. Enter your current password
3. Enter your new password
4. Confirm your new password
5. Click **Change Password**

---

## 9. Administrator Features

> **Note:** Only users with Admin role can access these features.

### 9.1 Admin Dashboard

Navigate to **Admin** in the navigation menu to access:

- **Statistics Overview**: Total users, events, registrations
- **Recent Registrations**: Latest event sign-ups
- **Recent Events**: Newly created events
- **User Distribution**: Users by role
- **Event Status**: Published/Draft/Cancelled events

### 9.2 Managing Users

1. Go to **Admin** → **Manage Users**
2. View all registered users
3. Actions available:
   - **Edit**: Change user details or role
   - **Delete**: Remove user account

### 9.3 Managing Events

1. Go to **Admin** → **Manage Events**
2. View all events in the system
3. Actions available:
   - **Edit**: Modify any event
   - **Delete**: Remove any event
   - **View Registrations**: See who's registered

### 9.4 Viewing All Registrations

1. Go to **Admin** → **All Registrations**
2. See every event registration in the system
3. Filter by event or user

---

## 10. Troubleshooting

### 10.1 Common Issues

| Issue                        | Solution                                                                |
| ---------------------------- | ----------------------------------------------------------------------- |
| **Can't register for event** | Check that you're logged in, event isn't full, and registration is open |
| **Can't create event**       | Ensure you have Organizer or Admin role                                 |
| **Can't access admin panel** | Only Admin users can access admin features                              |
| **Password not working**     | Use the password you set during registration                            |
| **Email already registered** | Use a different email or login with existing account                    |

### 10.2 Password Recovery

Currently, password recovery is not implemented. Contact your administrator if you forget your password.

### 10.3 Contact Support

For additional help:

- Email: [Your support email]
- Use the **Contact** page on the website

---

## Appendix: Test Accounts

The following test accounts are available (if seeded):

| Username  | Password     | Role      | Description           |
| --------- | ------------ | --------- | --------------------- |
| admin     | admin123     | Admin     | Full system access    |
| organizer | organizer123 | Organizer | Can create events     |
| user      | user123      | User      | Standard user account |
| alice     | alice123     | User      | Test user             |
| bob       | bob123       | User      | Test user             |

---

## Quick Reference

### Navigation Routes

| Page         | URL                  |
| ------------ | -------------------- |
| Home         | `/`                  |
| Events       | `/events`            |
| Register     | `/auth/register`     |
| Login        | `/auth/login`        |
| Dashboard    | `/dashboard`         |
| My Events    | `/events/my-events`  |
| Registered   | `/events/registered` |
| Create Event | `/events/create`     |
| Admin        | `/admin`             |

---

_CrowdConnect User Manual_
_Version 1.0_
_February 2026_
