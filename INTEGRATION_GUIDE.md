# Frontend-Backend Integration Guide

## Project Structure

```
studentprojectstorage/
├── backend/                    # Flask API server
│   ├── app.py                 # Main application (serves both API & frontend)
│   ├── config.py              # Configuration (MySQL credentials)
│   ├── db.py                  # Database connection
│   ├── init_db.py             # Database initialization script
│   ├── routes/                # API endpoints
│   │   ├── auth.py            # Authentication endpoints
│   │   ├── items.py           # Item & category management
│   │   ├── usage.py           # Usage tracking
│   │   └── dashboard.py       # Dashboard statistics
│   └── __pycache__/          # Python cache
│
└── frontend/                   # Web application (served by Flask)
    ├── js/                    # JavaScript modules
    │   ├── api.js             # API client & shared utilities
    │   └── sidebar.js         # Navigation & sidebar builder
    │
    ├── login.html             # Login page
    ├── dashboard.html         # Main dashboard
    ├── inventory.html         # Item management
    ├── usage.html             # Issue/return items
    ├── reports.html           # Analytics & reports
    ├── admin.html             # Admin panel
    ├── style.css              # Global styles
    └── [other static files]
```

## Setup Instructions

### 1. Backend Setup

#### Install Dependencies
```bash
cd backend
pip install flask flask-cors mysql-connector-python werkzeug
```

#### Configure Database Connection
Edit `backend/config.py` and update MySQL credentials:
```python
MYSQL_HOST      = "localhost"
MYSQL_PORT      = 3306
MYSQL_USER      = "root"
MYSQL_PASSWORD  = "your_password"  # Update this!
MYSQL_DB        = "robotics_inventory"
```

#### Initialize Database
```bash
python backend/init_db.py
```

### 2. Start the Server

The Flask app now serves both the API and frontend:
```bash
python backend/app.py
```

The server will run at `http://localhost:5000`

### 3. Access the Application

Open your browser and navigate to:
- **Main URL**: `http://localhost:5000`
- **Login Page**: `http://localhost:5000/login.html`
- **Dashboard**: `http://localhost:5000/dashboard.html`

## API Architecture

### What Changed

1. **Frontend Scripts Location**
   - Scripts moved from `frontend/` to `frontend/js/`
   - All HTML files reference: `<script src="js/api.js"></script>`

2. **API Base URL**
   - Updated from `http://localhost:5000/api` → `/api` (relative path)
   - Works whether frontend is served locally or from backend

3. **Flask Configuration**
   - `app.py` now includes static file serving
   - Frontend is served from `../frontend` directory
   - Root path `/` redirects to login page

### API Endpoints

#### Authentication
- `POST /api/auth/login` - User login
- `POST /api/auth/logout` - User logout
- `GET /api/auth/me` - Current user info

#### Items & Categories
- `GET /api/items` - List all items
- `POST /api/items` - Add new item
- `PUT /api/items/<id>` - Update item
- `DELETE /api/items/<id>` - Delete item
- `GET /api/categories` - List categories
- `POST /api/categories` - Add category
- `PUT /api/categories/<id>` - Update category
- `DELETE /api/categories/<id>` - Delete category

#### Usage Tracking
- `GET /api/usage` - List all usage records
- `POST /api/usage/issue` - Issue item to user
- `POST /api/usage/<id>/return` - Return item
- `GET /api/usage/overdue` - Get overdue items

#### Dashboard
- `GET /api/dashboard/stats` - Dashboard statistics
- `GET /api/dashboard/recent` - Recent activity
- `GET /api/dashboard/category-stats` - Category breakdown

#### Admin
- `GET /api/admin/users` - List all users
- `POST /api/admin/users` - Create new user
- `DELETE /api/admin/users/<id>` - Delete user
- `POST /api/admin/teams` - Create external team
- `POST /api/admin/projects` - Create project

## Frontend Pages

### login.html
- Entry point for authentication
- Redirects to dashboard if already logged in
- Demo credentials displayed

### dashboard.html
- Overview of inventory status
- Real-time statistics
- Recent activity log
- Quick action buttons

### inventory.html
- Browse all items
- Search & filter by category
- Add/edit/delete items (admin)
- Manage categories

### usage.html
- Issue items to users/projects
- Track borrowed items
- Return items
- View active issues

### reports.html
- **Overdue Items** - Items not returned on time
- **Low Stock Items** - Items below 20% availability
- **Usage Summary** - Historical usage patterns
- **User Activity** - User borrowing statistics

### admin.html
- User management (admin only)
- External team management
- Project management
- System configuration

## User Roles & Permissions

| Role | Capabilities |
|------|---|
| **Guest** | View-only (inventory, dashboard), no writes |
| **Student** | Issue/return items, view inventory |
| **Lab Incharge** | Full item management, user management, all admin features |
| **Admin** | Full system access, user management, configuration |

### Demo Credentials
```
Admin:        admin / admin123
Lab Incharge: incharge / incharge123
Student:      student1 / student123
Guest:        guest / guest123
```

## Integration Features

### ✅ Cross-Origin Resource Sharing (CORS)
- Configured in `backend/app.py`
- Allows requests from localhost:3000, 5500, and file:// protocol

### ✅ Session Management
- Cookie-based authentication
- `credentials: "include"` in all API calls
- Session validation on every protected endpoint

### ✅ Error Handling
- 401 Unauthorized → Redirect to login
- Toast notifications for user feedback
- Comprehensive error messages

### ✅ Responsive UI
- Mobile-friendly design
- Sidebar navigation
- Modal dialogs for forms
- Status badges and indicators

## Troubleshooting

### Issue: "Cannot GET /login.html"
**Solution**: Ensure Flask is running with the correct static folder configuration. The frontend folder should be at `../frontend` relative to the backend directory.

### Issue: API calls return 401 Unauthorized
**Solution**: 
1. Verify MySQL database is running
2. Check `MYSQL_PASSWORD` in `config.py`
3. Ensure session cookie is being sent with `credentials: "include"`

### Issue: CORS errors in browser console
**Solution**: Check that your frontend URL matches allowed origins in `CORS()` configuration in `app.py`.

### Issue: Images/styles not loading
**Solution**: Verify `frontend/` directory structure matches the project layout. Static files should be in `frontend/` root.

## Running in Development

```bash
# Terminal 1: Start backend
cd backend
python app.py

# Application is now available at http://localhost:5000
```

No separate frontend server needed - Flask serves everything!

## Production Deployment

For production:

1. Update `config.py` with production database credentials
2. Set `app.run(debug=False)` in `app.py`
3. Use a WSGI server (Gunicorn, Waitress) instead of Flask dev server
4. Configure proper database backups
5. Enable HTTPS with SSL certificates

Example with Gunicorn:
```bash
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 "app:create_app()"
```

## Key Files Summary

| File | Purpose |
|------|---------|
| `backend/app.py` | Flask app with API routes & static file serving |
| `frontend/js/api.js` | API client library with helper functions |
| `frontend/js/sidebar.js` | Navigation sidebar builder |
| `backend/config.py` | Database credentials & Flask config |
| `backend/routes/*.py` | Individual API endpoint blueprints |

---

**Status**: ✅ Frontend and backend fully integrated! The Flask server now serves both the API and the web application.
