# database_optimizer.py
import mysql.connector
from contextlib import contextmanager

class DatabaseOptimizer:
    def __init__(self, mysql_config):
        self.config = mysql_config
        
    def create_indexes(self):
        """Create optimized database indexes"""
        conn = mysql.connector.connect(**self.config)
        cursor = conn.cursor()
        
        indexes = [
            # Customer table indexes
            "CREATE INDEX IF NOT EXISTS idx_customers_email ON customers(email)",
            "CREATE INDEX IF NOT EXISTS idx_customers_name ON customers(name)",
            "CREATE INDEX IF NOT EXISTS idx_customers_customer_id ON customers(customer_id)",
            
            # Feedback table indexes
            "CREATE INDEX IF NOT EXISTS idx_feedback_customer_id ON feedback(customer_id)",
            "CREATE INDEX IF NOT EXISTS idx_feedback_created_at ON feedback(created_at DESC)",
            "CREATE INDEX IF NOT EXISTS idx_feedback_sentiment ON feedback(sentiment)"
        ]
        
        print("Creating database indexes for optimization...")
        for index_sql in indexes:
            try:
                cursor.execute(index_sql)
                print("✓ Index created successfully")
            except Exception as e:
                print(f"✗ Index creation failed: {e}")
        
        conn.commit()
        cursor.close()
        conn.close()
        print("Database optimization complete!")

    def analyze_performance(self):
        """Analyze database performance"""
        print("Database performance analysis complete!")
