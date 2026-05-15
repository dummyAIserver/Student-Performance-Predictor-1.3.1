# Student Performance Predictor 🎓

A web-based machine learning application that predicts student academic performance using Linear Regression. Built with Flask, featuring role-based authentication, analytics dashboard, and data export capabilities.

## 🌟 Features

- **ML-Powered Predictions**: Uses Linear Regression to predict final exam marks based on attendance, assignment scores, and internal marks
- **Role-Based Access Control**: Three user roles with different permissions:
  - **Students**: Make predictions and view their own history
  - **Teachers**: View all predictions and access analytics dashboard
  - **Admins**: Full access including user management
- **Analytics Dashboard**: Visual insights into student performance with charts and statistics
- **Data Export**: Export prediction history to Excel (.xlsx) and PDF formats
- **Secure Authentication**: 
  - CSRF protection
  - Rate limiting on login/register
  - Strong password validation
  - Timing-safe password verification
- **Prediction History**: Track and manage all predictions with filtering options
- **Responsive UI**: Clean, modern interface with real-time validation

## 🚀 Tech Stack

- **Backend**: Flask 2.3.3
- **Database**: SQLite with SQLAlchemy 2.0.23
- **Authentication**: Flask-Login 0.6.3
- **Machine Learning**: scikit-learn 1.3.0 (Linear Regression)
- **Data Processing**: pandas 2.0.3, numpy 1.23.5
- **Security**: Flask-WTF 1.1.1 (CSRF), Flask-Limiter 3.5.0
- **Export**: openpyxl (Excel), reportlab (PDF)
- **Server**: gunicorn (production)

## 📋 Prerequisites

- Python 3.10 or higher
- pip package manager

## 🔧 Installation

1. **Clone the repository**
```bash
git clone <repository-url>
cd Student-Performance-Predictor-1.3.1
```

2. **Create a virtual environment** (recommended)
```bash
python -m venv venv
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Train the ML model** (if model.pkl doesn't exist)
```bash
python model_train.py
```

5. **Run the application**
```bash
python app.py
```

The application will be available at `http://localhost:5000`

## 👤 Default Users

The application creates default users on first run:

| Role    | Username | Password |
|---------|----------|----------|
| Admin   | admin    | admin123 |
| Teacher | teacher  | teacher123 |
| Student | student  | student123 |

**⚠️ Important**: Change these default passwords in production!

## 📊 Model Details

The Linear Regression model is trained on student performance data with the following features:

- **Attendance** (0-100%)
- **Assignment Score** (0-20)
- **Internal Marks** (0-30)

The model predicts **Final Marks** (0-100) with an R² score of 0.90+.

### Grade Calculation

| Score Range | Grade |
|-------------|-------|
| 90-100      | A+    |
| 80-89       | A     |
| 70-79       | B     |
| 60-69       | C     |
| 50-59       | D     |
| Below 50    | F     |

### Performance Categories

- **Excellent**: 80+
- **Good**: 60-79
- **Average**: 40-59
- **Needs Improvement**: Below 40

## 📁 Project Structure

```
Student-Performance-Predictor-1.3.1/
├── app.py                 # Main Flask application
├── auth.py                # Authentication module
├── models.py              # SQLAlchemy database models
├── model_train.py         # ML model training script
├── export_utils.py        # Excel/PDF export utilities
├── requirements.txt       # Python dependencies
├── model.pkl              # Trained ML model
├── student_performance_dataset.csv  # Training dataset
├── static/
│   └── style.css          # Application styles
├── templates/
│   ├── index.html         # Prediction form
│   ├── dashboard.html     # Analytics dashboard
│   ├── history.html       # Prediction history
│   ├── login.html         # Login page
│   ├── register.html      # Registration page
│   ├── profile.html       # User profile
│   └── admin_users.html   # Admin user management
└── tests/                 # Test files
```

## 🔐 Security Features

- **CSRF Protection**: All forms protected with CSRF tokens
- **Rate Limiting**: 5 requests per minute on login/register endpoints
- **Password Validation**: Requires uppercase, lowercase, numbers, and special characters
- **SQL Injection Prevention**: Parameterized queries via SQLAlchemy ORM
- **XSS Protection**: Flask's built-in XSS protection
- **Timing-Safe Password Comparison**: Prevents user enumeration attacks

## 🌐 API Endpoints

### Public
- `GET /` - Home page
- `GET /auth/login` - Login page
- `GET /auth/register` - Registration page

### Authenticated
- `POST /predict` - Make a prediction
- `GET /history` - View prediction history
- `POST /clear-history` - Clear prediction history
- `POST /delete-entry/<id>` - Delete specific entry
- `GET /export/excel` - Export to Excel
- `GET /export/pdf` - Export to PDF
- `GET /dashboard` - Analytics dashboard (teachers/admins only)
- `GET /api/analytics` - Analytics data API
- `GET /api/model-info` - Model information

### Admin Only
- `GET /auth/admin/users` - User management
- `POST /auth/admin/user/<id>/delete` - Delete user
- `POST /auth/admin/user/<id>/role` - Change user role

## 🧪 Testing

Test files are included in the `tests/` directory:
- `test_csrf.py` - CSRF protection tests
- `test_conflicts.py` - Conflict resolution tests
- `test_email_simple.py` - Email validation tests
- `debug_csrf.py` - CSRF debugging utilities

## 🚀 Deployment

For production deployment:

1. **Set environment variables**:
```bash
export SECRET_KEY='your-secret-key-here'
```

2. **Use a production WSGI server**:
```bash
gunicorn -w 4 -b 0.0.0.0:5000 app:app
```

3. **Configure a reverse proxy** (nginx/Apache) for SSL termination

4. **Change default passwords** immediately

5. **Set up database backups** for the SQLite database

## 📝 License

This project is provided as-is for educational purposes.

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📧 Support

For issues or questions, please open an issue on the GitHub repository.

---

**Built with ❤️ using Flask and Machine Learning**
