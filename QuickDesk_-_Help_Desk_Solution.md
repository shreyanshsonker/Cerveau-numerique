# QuickDesk - Help Desk Solution

## Overview

QuickDesk is a comprehensive help desk solution built for the Odoox CGC Mohali Hackathon 2025. It provides a simple, easy-to-use platform for managing support tickets with role-based access control and modern web technologies.

## Features

### Core Functionality
- **User Authentication**: Secure registration and login system with role-based access
- **Ticket Management**: Create, view, update, and track support tickets
- **File Attachments**: Support for file uploads with tickets (up to 16MB)
- **Voting System**: Users can upvote/downvote tickets for prioritization
- **Comments**: Threaded conversations on tickets
- **Search & Filtering**: Advanced search and filtering options
- **Responsive Design**: Mobile-friendly interface

### User Roles
- **End Users**: Can create and track their own tickets
- **Support Agents**: Can view, assign, and resolve tickets
- **Administrators**: Full system management including users and categories

### Ticket Workflow
1. **Open** → **In Progress** → **Resolved** → **Closed**
2. Real-time status updates and notifications
3. Assignment to support agents
4. Comment threads for communication

## Technology Stack

### Backend
- **Framework**: Flask (Python)
- **Database**: SQLite with SQLAlchemy ORM
- **Authentication**: JWT tokens with bcrypt password hashing
- **File Storage**: Local filesystem with secure upload handling
- **API**: RESTful API design

### Frontend
- **Framework**: React 18 with Vite
- **Styling**: Tailwind CSS
- **Icons**: Lucide React
- **Routing**: React Router
- **State Management**: Context API

## Project Structure

```
quickdesk-backend/
├── src/
│   ├── main.py              # Flask application entry point
│   ├── models/              # Database models
│   │   ├── user.py         # User model with authentication
│   │   ├── ticket.py       # Ticket model
│   │   ├── category.py     # Category model
│   │   ├── comment.py      # Comment model
│   │   └── vote.py         # Vote model
│   ├── routes/             # API endpoints
│   │   ├── auth.py         # Authentication routes
│   │   ├── tickets.py      # Ticket management
│   │   ├── categories.py   # Category management
│   │   └── users.py        # User management
│   ├── static/             # Frontend build files
│   └── uploads/            # File attachments
├── requirements.txt        # Python dependencies
└── venv/                   # Virtual environment

quickdesk-frontend/
├── src/
│   ├── components/         # React components
│   │   ├── auth/          # Login/Register components
│   │   ├── tickets/       # Ticket-related components
│   │   ├── admin/         # Admin panel components
│   │   └── ui/            # Reusable UI components
│   ├── contexts/          # React contexts
│   ├── lib/               # Utility functions and API client
│   └── App.jsx            # Main application component
├── dist/                  # Production build
└── package.json           # Node.js dependencies
```

## Installation & Setup

### Prerequisites
- Python 3.11+
- Node.js 20+
- npm or pnpm

### Backend Setup
1. Navigate to the backend directory:
   ```bash
   cd quickdesk-backend
   ```

2. Activate the virtual environment:
   ```bash
   source venv/bin/activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Run the Flask application:
   ```bash
   python src/main.py
   ```

The backend will be available at `http://localhost:5000`

### Frontend Setup
1. Navigate to the frontend directory:
   ```bash
   cd quickdesk-frontend
   ```

2. Install dependencies:
   ```bash
   pnpm install
   ```

3. Build for production:
   ```bash
   pnpm run build
   ```

4. Copy build files to Flask static directory:
   ```bash
   cp -r dist/* ../quickdesk-backend/src/static/
   ```

### Full-Stack Deployment
The application is configured as a full-stack solution where Flask serves the React frontend from its static directory. Simply run the Flask backend and access the application at `http://localhost:5000`.

## API Endpoints

### Authentication
- `POST /api/auth/register` - User registration
- `POST /api/auth/login` - User login
- `POST /api/auth/logout` - User logout
- `POST /api/auth/change-password` - Change password

### Tickets
- `GET /api/tickets` - List tickets with filtering
- `POST /api/tickets` - Create new ticket
- `GET /api/tickets/<id>` - Get ticket details
- `PUT /api/tickets/<id>` - Update ticket
- `POST /api/tickets/<id>/comments` - Add comment
- `POST /api/tickets/<id>/vote` - Vote on ticket

### Categories
- `GET /api/categories` - List categories
- `POST /api/categories` - Create category (Admin only)
- `PUT /api/categories/<id>` - Update category (Admin only)
- `DELETE /api/categories/<id>` - Delete category (Admin only)

### Users
- `GET /api/users` - List users (Admin only)
- `GET /api/users/agents` - List support agents
- `PUT /api/users/<id>` - Update user
- `POST /api/users/<id>/activate` - Activate user (Admin only)
- `POST /api/users/<id>/deactivate` - Deactivate user (Admin only)

## Security Features

- **Password Hashing**: bcrypt with salt
- **JWT Authentication**: Secure token-based authentication
- **Input Validation**: Server-side validation for all inputs
- **File Upload Security**: Type and size validation
- **SQL Injection Protection**: Parameterized queries with SQLAlchemy
- **XSS Protection**: Input sanitization and output encoding
- **CORS Configuration**: Proper cross-origin resource sharing

## Database Schema

### Users Table
- `id` (Primary Key)
- `username` (Unique)
- `email` (Unique)
- `password_hash`
- `role` (end_user, support_agent, admin)
- `is_active`
- `created_at`

### Tickets Table
- `id` (Primary Key)
- `subject`
- `description`
- `status` (open, in_progress, resolved, closed)
- `priority` (low, medium, high, urgent)
- `user_id` (Foreign Key)
- `assigned_to` (Foreign Key)
- `category_id` (Foreign Key)
- `attachment_path`
- `created_at`
- `updated_at`

### Categories Table
- `id` (Primary Key)
- `name`
- `description`
- `color`
- `is_active`
- `created_at`

### Comments Table
- `id` (Primary Key)
- `ticket_id` (Foreign Key)
- `user_id` (Foreign Key)
- `content`
- `created_at`

### Votes Table
- `id` (Primary Key)
- `ticket_id` (Foreign Key)
- `user_id` (Foreign Key)
- `is_upvote`
- `created_at`
