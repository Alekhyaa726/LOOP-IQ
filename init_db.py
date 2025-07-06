#!/usr/bin/env python3
"""
Database initialization script for ZEPSI feedback system
"""

import mysql.connector
from mysql.connector import Error
import hashlib

def hash_password(password):
    """Simple password hashing (use bcrypt in production)"""
    return hashlib.sha256(password.encode()).hexdigest()

def init_database():
    """Initialize the database with all required tables"""
    try:
        # Create connection
        connection = mysql.connector.connect(
            host='localhost',
            user='root',
            password='Kaviguru_1',
            database='feedback_db'
        )
        
        if connection.is_connected():
            cursor = connection.cursor()
            
            # Create customers table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS customers (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    name VARCHAR(255) NOT NULL UNIQUE,
                    customer_id VARCHAR(50) NOT NULL UNIQUE,
                    email VARCHAR(255) NOT NULL UNIQUE,
                    phone VARCHAR(20),
                    password VARCHAR(255) NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            print("✅ Customers table created/verified")
            
            # Create admins table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS admins (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    username VARCHAR(255) NOT NULL UNIQUE,
                    full_name VARCHAR(255) NOT NULL,
                    email VARCHAR(255) NOT NULL UNIQUE,
                    department VARCHAR(100),
                    password VARCHAR(255) NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            print("✅ Admins table created/verified")
            
            # Create department_admins table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS department_admins (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    username VARCHAR(255) NOT NULL UNIQUE,
                    full_name VARCHAR(255) NOT NULL,
                    email VARCHAR(255) NOT NULL UNIQUE,
                    department VARCHAR(100) NOT NULL,
                    password VARCHAR(255) NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            print("✅ Department admins table created/verified")
            
            # Create feedback table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS feedback (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    name VARCHAR(255) NOT NULL,
                    customer_id VARCHAR(50) NOT NULL,
                    feedback TEXT NOT NULL,
                    sentiment VARCHAR(20) NOT NULL,
                    departments JSON NOT NULL,
                    suggestions JSON NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            print("✅ Feedback table created/verified")
            
            # Create admin_responses table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS admin_responses (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    feedback_id INT NOT NULL,
                    department VARCHAR(100) NOT NULL,
                    response TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (feedback_id) REFERENCES feedback(id) ON DELETE CASCADE,
                    UNIQUE KEY unique_response (feedback_id, department)
                )
            """)
            print("✅ Admin responses table created/verified")
            
            # Create customer_ratings table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS customer_ratings (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    feedback_id INT NOT NULL,
                    department VARCHAR(100) NOT NULL,
                    rating INT NOT NULL CHECK (rating >= 1 AND rating <= 5),
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (feedback_id) REFERENCES feedback(id) ON DELETE CASCADE,
                    UNIQUE KEY unique_rating (feedback_id, department)
                )
            """)
            print("✅ Customer ratings table created/verified")
            
            # Create department_points table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS department_points (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    department VARCHAR(100) NOT NULL UNIQUE,
                    points INT DEFAULT 0,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
                )
            """)
            print("✅ Department points table created/verified")
            
            # Insert default admin if not exists
            cursor.execute("SELECT id FROM admins WHERE username = 'admin'")
            if not cursor.fetchone():
                cursor.execute("""
                    INSERT INTO admins (username, full_name, email, department, password)
                    VALUES (%s, %s, %s, %s, %s)
                """, ('admin', 'Super Admin', 'admin@zepsi.com', 'All', hash_password('admin1')))
                print("✅ Default admin account created")
            
            connection.commit()
            cursor.close()
            connection.close()
            print("✅ Database initialization completed successfully!")
            return True
            
    except Error as e:
        print(f"❌ Error initializing database: {e}")
        return False

if __name__ == "__main__":
    init_database()
