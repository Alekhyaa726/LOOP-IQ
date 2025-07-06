# 🚀 Loop-IQ Feedback Management System

A modern, comprehensive feedback management platform built with Flask and MySQL. Loop-IQ enables organizations to collect, manage, and respond to customer feedback efficiently with AI-powered sentiment analysis and automated department routing.

![Loop-IQ Dashboard](https://img.shields.io/badge/Status-MVP%20Ready-brightgreen)
![Python](https://img.shields.io/badge/Python-3.8+-blue)
![Flask](https://img.shields.io/badge/Flask-3.0.0-red)
![MySQL](https://img.shields.io/badge/MySQL-8.0+-orange)

## 📋 Table of Contents

- [Overview](#-overview)
- [Features](#-features)
- [Technology Stack](#-technology-stack)
- [Installation](#-installation)
- [Configuration](#-configuration)
- [Usage](#-usage)
- [API Documentation](#-api-documentation)
- [Project Structure](#-project-structure)
- [Contributing](#-contributing)
- [License](#-license)

## 🎯 Overview

Loop-IQ is a SaaS-ready feedback management system that streamlines customer feedback collection, analysis, and response processes. The platform features:

- *Multi-role Access*: Customers, Department Admins, and Super Admins
- *AI-Powered Sentiment Analysis*: Automatic sentiment detection and department routing
- *Modern UI/UX*: Glass morphism design with responsive layouts
- *Rating System*: Customer feedback on department responses
- *Rewards System*: Voucher generation for customer engagement
- *Real-time Analytics*: Dashboard metrics and performance tracking

## ✨ Features

### 🎨 User Experience
- *Modern Glass Morphism Design*: Beautiful, professional UI with floating animations
- *Responsive Layout*: Works seamlessly on desktop, tablet, and mobile devices
- *Interactive Elements*: Smooth hover effects, animations, and real-time feedback
- *Dark Theme*: Easy on the eyes with consistent branding

### 🔐 Authentication & Security
- *Multi-role Authentication*: Separate login systems for customers, departments, and admins
- *Password Hashing*: Secure password storage using SHA-256
- *Session Management*: Secure session handling with automatic cleanup
- *Department Isolation*: Strict access control for department-specific data

### 🤖 AI & Automation
- *Sentiment Analysis*: Automatic detection of feedback sentiment (Positive/Negative/Neutral)
- *Smart Department Routing*: AI-powered assignment to relevant departments
- *Automated Response Generation*: Context-aware response suggestions
- *Priority Scoring*: Intelligent feedback prioritization

### 📊 Analytics & Reporting
- *Real-time Dashboards*: Live metrics for all user types
- *Department Performance*: Track response times and satisfaction scores
- *Customer Insights*: Feedback trends and sentiment analysis
- *Admin Analytics*: Comprehensive overview of system performance

### 🎁 Rewards System
- *Voucher Generation*: Automatic voucher creation for customer engagement
- *Points System*: Department-based point accumulation
- *Redemption Tracking*: Monitor voucher usage and customer satisfaction

## 🛠 Technology Stack

### Backend
- *Python 3.8+*: Core programming language
- *Flask 3.0.0*: Lightweight web framework
- *MySQL 8.0+*: Relational database management
- *mysql-connector-python*: Database connectivity

### Frontend
- *HTML5*: Semantic markup structure
- *CSS3*: Modern styling with glass morphism effects
- *JavaScript*: Interactive functionality and AJAX requests
- *Font Awesome*: Icon library for UI elements
- *Google Fonts (Inter)*: Professional typography

### Supporting Libraries
- *Werkzeug*: WSGI utilities and security helpers
- *Jinja2*: Template engine for dynamic content
- *itsdangerous*: Secure session signing
- *MarkupSafe*: Safe HTML handling

## 🚀 Installation

### Prerequisites
- Python 3.8 or higher
- MySQL 8.0 or higher
- pip (Python package installer)

### Step 1: Clone the Repository
bash
git clone https://github.com/yourusername/loop-iq.git
cd loop-iq/ZEPSI


### Step 2: Install Dependencies
bash
pip install -r requirements.txt


### Step 3: Database Setup
1. *Create MySQL Database*:
   sql
   CREATE DATABASE feedback_db;
   

2. *Run Database Initialization*:
   bash
   python3 create_database.py
   

3. *Create Admin User* (Optional):
   bash
   python3 create_admin.py
   

### Step 4: Configuration
Update the MySQL configuration in app.py:
python
MYSQL_CONFIG = {
    'host': 'localhost',
    'user': 'your_username',
    'password': 'your_password',
    'database': 'feedback_db',
    'charset': 'utf8mb4',
    'autocommit': True
}


### Step 5: Run the Application
bash
python3 app.py


The application will be available at http://localhost:5001

## ⚙ Configuration

### Environment Variables (Recommended for Production)
bash
export FLASK_SECRET_KEY="your-secret-key"
export MYSQL_HOST="localhost"
export MYSQL_USER="your_username"
export MYSQL_PASSWORD="your_password"
export MYSQL_DATABASE="feedback_db"


### Database Configuration
The system supports the following departments:
- Product Management
- UX/UI Design
- Delivery Services
- Logistics & Supply Chain
- Sales Department
- Marketing Team
- Engineering Team
- Customer Service
- Quality Assurance
- Billing & Finance

## 📖 Usage

### Customer Workflow
1. *Sign Up/Login*: Create account or login with existing credentials
2. *Submit Feedback*: Write detailed feedback with automatic sentiment analysis
3. *Track Responses*: View department responses and rate their quality
4. *Redeem Rewards*: Use earned vouchers for future purchases

### Department Admin Workflow
1. *Department Login*: Access department-specific dashboard
2. *Review Feedback*: View assigned feedback with sentiment analysis
3. *Generate Responses*: Create AI-powered response suggestions
4. *Send Responses*: Approve and send responses to customers
5. *Track Performance*: Monitor response times and customer ratings

### Super Admin Workflow
1. *Admin Login*: Access comprehensive admin dashboard
2. *System Overview*: View all feedback, departments, and metrics
3. *Department Management*: Monitor and manage all departments
4. *Analytics*: Access detailed reports and performance insights
5. *Rewards Management*: Oversee voucher generation and redemption

## 🔌 API Documentation

### Authentication Endpoints
- POST /customer_login - Customer authentication
- POST /admin_login - Admin authentication
- POST /department/<dept>/login - Department authentication

### Feedback Endpoints
- POST /submit_feedback - Submit new feedback
- GET /view_feedback - View feedback responses
- POST /rate_response - Rate department responses

### Admin Endpoints
- POST /approve_suggestion - Approve AI-generated responses
- GET /admin/feedback/<dept> - View department-specific feedback
- GET /rewards - Access rewards dashboard


## 🎨 Design System

### Color Palette
- *Primary*: #0f172a (Dark Blue)
- *Secondary*: #f59e0b (Amber)
- *Accent*: #10b981 (Emerald)
- *Light*: #f8fafc (Light Gray)
- *Dark*: #0f172a (Dark Blue)

### Typography
- *Font Family*: Inter (Google Fonts)
- *Weights*: 300, 400, 500, 600, 700
- *Responsive*: Scales appropriately across devices

### Components
- *Glass Morphism Cards*: Transparent backgrounds with backdrop blur
- *Gradient Buttons*: Modern gradient-styled interactive elements
- *Floating Icons*: Animated background elements for visual appeal
- *Responsive Grid*: Flexible layouts for all screen sizes

## 🚀 Deployment

### Local Development
bash
python3 app.py


### Production Deployment
1. *Set Environment Variables*
2. *Use Production WSGI Server* (Gunicorn/uWSGI)
3. *Configure Reverse Proxy* (Nginx)
4. *Set Up SSL Certificate*
5. *Configure Database Backups*

### Recommended Platforms
- *Render*: Easy deployment with automatic scaling
- *Railway*: Simple deployment with GitHub integration
- *Heroku*: Traditional platform with extensive add-ons
- *DigitalOcean*: VPS deployment with full control

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (git checkout -b feature/amazing-feature)
3. Commit your changes (git commit -m 'Add amazing feature')
4. Push to the branch (git push origin feature/amazing-feature)
5. Open a Pull Request

### Development Guidelines
- Follow PEP 8 Python style guidelines
- Add comments for complex logic
- Update documentation for new features
- Test thoroughly before submitting

## 📊 Performance

### Current Metrics
- *Startup Time*: < 1 second
- *Page Load Speed*: Instant on localhost
- *Database Queries*: Optimized for MVP scale
- *Responsive Design*: Works on all devices
- *Error Handling*: Comprehensive logging and user feedback

### Scalability Considerations
- *Database*: Add indexes for large datasets
- *Caching*: Implement Redis for session storage
- *Load Balancing*: Use multiple application instances
- *CDN*: Serve static assets from CDN

## 🔒 Security

### Current Security Features
- Password hashing with SHA-256
- Session management with secure cookies
- Input validation and sanitization
- SQL injection prevention
- XSS protection through template escaping

### Production Security Recommendations
- Use environment variables for secrets
- Implement HTTPS/SSL
- Add rate limiting
- Set up security monitoring
- Regular security audits


## 📞 Support

For support and questions:
- *Email*: support@loop-iq.com
- *Documentation*: [docs.loop-iq.com](https://docs.loop-iq.com)
- *Issues*: [GitHub Issues](https://github.com/yourusername/loop-iq/issues)

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- *Flask Community*: For the excellent web framework
- *Font Awesome*: For the beautiful icons
- *Google Fonts*: For the Inter font family
- *Open Source Community*: For inspiration and best practices

---

*Made with ❤ by the Loop-IQ Team*

Empowering organizations to build better customer relationships through intelligent feedback management.