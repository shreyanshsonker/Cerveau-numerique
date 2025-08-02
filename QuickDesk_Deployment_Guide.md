# QuickDesk Deployment Guide

## Quick Start

The QuickDesk application is already set up and ready to run. Follow these simple steps:

### 1. Start the Application

```bash
cd quickdesk-backend
source venv/bin/activate
python src/main.py
```

The application will be available at: **http://localhost:5000**

### 2. Access the Application

Open your web browser and navigate to `http://localhost:5000`

### 3. Create Your First Account

1. Click "create a new account" on the login page
2. Fill in the registration form:
   - Username: Choose any username
   - Email: Enter a valid email address
   - Account Type: Select your role (End User, Support Agent, or Administrator)
   - Password: Create a secure password
   - Confirm Password: Re-enter your password
3. Click "Create Account"

### 4. Start Using QuickDesk

Once logged in, you can:
- **Dashboard**: View ticket statistics and recent activity
- **Create Ticket**: Submit new support requests
- **View Tickets**: Browse and manage existing tickets
- **Admin Panel**: Manage users and categories (Admin only)

## Application Features

### For End Users
- Create support tickets with attachments
- Track ticket status and progress
- Add comments to tickets
- Vote on tickets (upvote/downvote)
- Search and filter tickets

### For Support Agents
- View and manage assigned tickets
- Update ticket status (Open → In Progress → Resolved → Closed)
- Add comments and updates
- Assign tickets to other agents

### For Administrators
- Manage user accounts and roles
- Create and manage ticket categories
- View system-wide statistics
- Activate/deactivate users

## Technical Details

### Backend (Flask)
- **Port**: 5000
- **Database**: SQLite (automatically created)
- **File Uploads**: Stored in `src/uploads/` directory
- **Static Files**: React frontend served from `src/static/`

### Frontend (React)
- **Framework**: React 18 with Vite
- **Styling**: Tailwind CSS
- **Build**: Production build already integrated with Flask

### Database
- **Type**: SQLite
- **Location**: `quickdesk-backend/src/instance/quickdesk.db`
- **Auto-created**: Database and tables are created automatically on first run

## File Structure

```
quickdesk-backend/
├── src/
│   ├── main.py              # Application entry point
│   ├── models/              # Database models
│   ├── routes/              # API endpoints
│   ├── static/              # Frontend files (React build)
│   ├── uploads/             # File attachments
│   └── instance/            # Database file location
└── venv/                    # Python virtual environment
```

## Default Categories

The system comes pre-configured with these ticket categories:
- Account Issues
- Billing
- Feature Request
- General Inquiry
- Technical Support

Administrators can add, edit, or remove categories as needed.

## Security Features

- **Password Hashing**: All passwords are securely hashed using bcrypt
- **JWT Authentication**: Secure token-based authentication
- **File Upload Validation**: File type and size restrictions
- **Input Validation**: All user inputs are validated and sanitized
- **Role-Based Access**: Different permissions for different user roles

## Troubleshooting

### Application Won't Start
1. Ensure you're in the correct directory: `cd quickdesk-backend`
2. Activate the virtual environment: `source venv/bin/activate`
3. Check if all dependencies are installed: `pip install -r requirements.txt`

### Database Issues
- The SQLite database is created automatically
- If you encounter database errors, delete the `src/instance/` directory and restart the application

### File Upload Issues
- Ensure the `src/uploads/` directory exists and is writable
- Check file size limits (maximum 16MB)
- Verify file type restrictions (txt, pdf, png, jpg, gif, doc, docx)

### Port Already in Use
If port 5000 is already in use, you can modify the port in `src/main.py`:
```python
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001, debug=True)  # Change port here
```

## Production Deployment

For production deployment, consider:

1. **Environment Variables**: Set `FLASK_ENV=production`
2. **Database**: Use PostgreSQL or MySQL instead of SQLite
3. **Web Server**: Use Gunicorn or uWSGI with Nginx
4. **SSL/HTTPS**: Configure SSL certificates
5. **File Storage**: Use cloud storage for file attachments
6. **Email**: Configure SMTP for email notifications

## Support

For any issues or questions about the QuickDesk application, please refer to the README.md file or create a ticket within the application itself once it's running.

---

**Note**: This application was developed for the Odoox CGC Mohali Hackathon 2025 and demonstrates a complete help desk solution with modern web technologies.

