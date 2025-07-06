from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
import mysql.connector
from mysql.connector import Error
import json
import hashlib
from random import choice, sample, randint
import re
import string

app = Flask(__name__)
# IMPORTANT: Use an environment variable and a more secure key in a real application
app.secret_key = "a-very-strong-and-random-secret-key-for-rewards"

# MySQL Configuration
MYSQL_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': 'Kaviguru_1',
    'database': 'feedback_db',
    'charset': 'utf8mb4',
    'autocommit': True
}

def get_mysql_connection():
    """Get MySQL connection"""
    try:
        connection = mysql.connector.connect(**MYSQL_CONFIG)
        return connection
    except Error as e:
        print(f"Error connecting to MySQL: {e}")
        return None

def test_mysql_connection():
    """Test MySQL connection and print status"""
    try:
        connection = get_mysql_connection()
        if connection and connection.is_connected():
            cursor = connection.cursor()
            cursor.execute("SELECT 1")
            result = cursor.fetchone()
            cursor.close()
            connection.close()
            print("✅ MySQL connection successful!")
            return True
        else:
            print("❌ MySQL connection failed: Could not establish connection")
            return False
    except Exception as e:
        print(f"❌ MySQL connection failed: {e}")
        return False

# --- User and Admin Data (Hardcoded for Demo - Backward Compatibility) ---
valid_users = {
    "person1": {"id": "1", "password": "pass1"},
    "person2": {"id": "2", "password": "pass2"},
    "person3": {"id": "3", "password": "pass3"},
    "person4": {"id": "4", "password": "pass4"},
    "person5": {"id": "5", "password": "pass5"},
    "person6": {"id": "6", "password": "pass6"},
    "person7": {"id": "7", "password": "pass7"},
    "person8": {"id": "8", "password": "pass8"},
    "person9": {"id": "9", "password": "pass9"},
    "person10": {"id": "10", "password": "pass10"}
}

admin_user = {
    "username": "admin",
    "password": "admin1"
}

# Department list for reference
DEPARTMENTS = ["Product", "UX_UI", "Delivery", "Logistics", "Sales", "Marketing", "Engineering", "Customer_Service", "QA", "Billing"]

# Department display names
DEPARTMENT_NAMES = {
    "Product": "Product Management",
    "UX_UI": "UX/UI Design", 
    "Delivery": "Delivery Services",
    "Logistics": "Logistics & Supply Chain",
    "Sales": "Sales Department",
    "Marketing": "Marketing Team",
    "Engineering": "Engineering Team",
    "Customer_Service": "Customer Service",
    "QA": "Quality Assurance",
    "Billing": "Billing & Finance"
}

# MODIFIED: Department keywords with the standardized "Customer_Service" key.
department_keywords = {
    "Product": ["product", "feature", "design", "item", "goods", "merchandise", "usability", "quality", "prototype", "innovation", "functionality", "manufacture", "materials", "components", "assembly", "release", "customization", "performance", "version", "catalog", "stock", "availability", "brand", "consumer", "durability", "warranty", "testing", "feedback", "launch", "upgrade", "refinement", "attributes"],
    "UX_UI": ["interface", "usability", "navigation", "ui", "ux", "layout", "experience", "flow", "user", "design", "accessibility", "interaction", "visual", "prototype", "responsiveness", "usability testing", "button", "feedback", "screen", "elements", "aesthetics", "user-friendly", "workflow", "intuitiveness", "prototyping", "animations", "icons", "colors", "structure", "consistency", "scalability"],
    "Delivery": ["shipping", "delivery", "courier", "package", "shipment", "received", "arrived", "dispatch", "tracking", "freight", "postal", "shipping label", "order", "shipment status", "return", "handling", "courier service", "logistics", "route", "box", "customs", "delivery date", "address", "arrival", "dispatch", "delivery time", "cost", "service", "parcel", "shipment number", "box size", "carrier"],
    "Logistics": ["logistic", "transport", "warehouse", "supply", "stock", "inventory", "storage", "distribution", "route", "delivery", "shipment", "packing", "tracking", "supply chain", "fulfillment", "order", "transportation", "load", "stockpile", "shipping", "wholesale", "transport", "outbound", "facility", "carrier", "cargo", "delivery", "inventory system", "supplier", "demand", "pallet", "coordination"],
    "Sales": ["sale", "buy", "price", "discount", "deal", "offer", "pricing", "cost", "promotion", "customer", "invoice", "bargain", "market", "negotiation", "upsell", "campaign", "conversion", "lead", "product bundle", "sales pitch", "discounted", "retail", "wholesale", "strategy", "closing", "forecast", "outreach", "target", "referral", "value", "transaction", "negotiation"],
    "Marketing": ["advertise", "campaign", "marketing", "promotion", "ad", "brand", "social media", "content", "strategy", "targeting", "seo", "social", "influencer", "newsletter", "branding", "lead generation", "outreach", "creative", "event", "sponsorship", "audience", "engagement", "public relations", "media", "analytics", "visibility", "e-mail", "conversion", "funnel", "inbound", "online", "advertisement"],
    "Engineering": ["bug", "error", "crash", "glitch", "code", "server", "app", "software", "debugging", "architecture", "api", "database", "network", "infrastructure", "deployment", "algorithm", "repository", "version control", "security", "performance", "coding", "integration", "testing", "framework", "platform", "build", "ci/cd", "continuous integration", "maintenance", "technical debt", "refactor", "scalability", "deployment pipeline"],
    "Customer_Service": ["support", "service", "help", "agent", "representative", "call center", "response", "issue", "assistance", "care", "communication", "ticket", "feedback", "customer experience", "satisfaction", "resolution", "service desk", "follow-up", "helpdesk", "care team", "inquiry", "problem", "solution", "guidance", "response time", "service level", "customer satisfaction", "complaint", "feedback", "request", "interaction"],
    "QA": ["quality", "test", "testing", "issue", "problem", "defect", "fault", "glitch", "bug", "verification", "validation", "quality control", "audit", "assessment", "regression", "automation", "performance", "usability", "integration", "standards", "criteria", "monitoring", "review", "iteration", "test case", "debugging", "user acceptance", "test plan", "system", "test suite", "defect tracking", "evaluation"],
    "Billing": ["bill", "payment", "charge", "invoice", "receipt", "refund", "credit", "debit", "transaction", "amount", "statement", "balance", "due", "collection", "subscription", "account", "payment method", "fee", "cost", "electronic", "billing cycle", "payment gateway", "invoice number", "payment history", "chargeback", "adjustment", "tax", "dispute", "payment terms", "billing address", "processing", "remittance"]
}

# --- Core Logic Functions ---

def hash_password(password):
    """Simple password hashing (use bcrypt in production)"""
    return hashlib.sha256(password.encode()).hexdigest()

def verify_password(password, hashed):
    """Verify password against hash"""
    return hashlib.sha256(password.encode()).hexdigest() == hashed

def safe_json_loads(s):
    """Safely parse JSON string, return empty list if invalid"""
    if s and s.strip() and s.lower() != 'null':
        try:
            return json.loads(s)
        except json.JSONDecodeError:
            print(f"safe_json_loads: Failed to decode: {s!r}")
            return []
    return []

def clear_all_sessions():
    """Clear all session data for security"""
    session.pop('user', None)
    session.pop('admin', None)
    session.pop('department_admin', None)
    session.pop('current_department', None)

def verify_department_access(required_department):
    """Verify user has access to specific department"""
    if 'department_admin' not in session:
        return False
    
    admin_dept = session['department_admin'].get('department')
    return admin_dept == required_department

def generate_customer_id():
    """Generate next available customer ID"""
    connection = get_mysql_connection()
    if connection:
        cursor = connection.cursor()
        cursor.execute("SELECT MAX(CAST(customer_id AS UNSIGNED)) FROM customers")
        result = cursor.fetchone()
        cursor.close()
        connection.close()
        
        if result[0] is None:
            return "1001"  # Start from 1001 for new signups
        else:
            return str(int(result[0]) + 1)
    else:
        return "1001"  # Fallback if connection fails

def get_customer_by_credentials(name, customer_id, password):
    try:
        connection = get_mysql_connection()
        if connection:
            cursor = connection.cursor()
            cursor.execute("""
                SELECT id, name, customer_id, email, phone 
                FROM customers 
                WHERE name = %s AND customer_id = %s AND password = %s
            """, (name, customer_id, hash_password(password)))
            result = cursor.fetchone()
            cursor.close()
            connection.close()
            return result
        return None
    except Exception as e:
        print(f"Database connection error: {e}")
        # Fallback to hardcoded users for demo purposes
        return None


def get_department_admin_by_credentials(username, password, department):
    """Get department admin by login credentials - STRICT department checking"""
    try:
        connection = get_mysql_connection()
        if connection:
            cursor = connection.cursor()
            cursor.execute("""
                SELECT id, username, full_name, email, department 
                FROM department_admins 
                WHERE username = %s AND password = %s AND department = %s
            """, (username, hash_password(password), department))
            result = cursor.fetchone()
            cursor.close()
            connection.close()
            
            # Double-check department match for security
            if result and result[4] == department:
                return result
        return None
    except Exception as e:
        print(f"Error accessing department_admins table: {e}")
        return None

def get_admin_by_credentials(username, password):
    """Get admin by login credentials (super admin)"""
    try:
        connection = get_mysql_connection()
        if connection:
            cursor = connection.cursor()
            cursor.execute("""
                SELECT id, username, full_name, email, department 
                FROM admins 
                WHERE username = %s AND password = %s
            """, (username, hash_password(password)))
            result = cursor.fetchone()
            cursor.close()
            connection.close()
            return result
        return None
    except Exception as e:
        print(f"Error accessing admins table: {e}")
        return None

def get_sentiment(text):
    words = re.findall(r'\b\w+\b', text.lower())
    positive_words = {"good", "great", "love", "happy", "excellent", "amazing", "best", "superb", "wonderful", "fantastic", "awesome", "perfect", "liked", "loved", "impressed", "satisfied", "smooth", "fast", "efficient", "pleased", "outstanding", "brilliant"}
    negative_words = {"bad", "poor", "worst", "slow", "broken", "crappy", "awful", "terrible", "horrible", "lame", "disappointed", "useless", "ugly", "buggy", "glitchy", "annoying", "frustrating", "pain", "hate", "suck", "sucks", "crap", "junk"}
    pos_count = sum(1 for word in words if word in positive_words)
    neg_count = sum(1 for word in words if word in negative_words)
    if pos_count > neg_count:
        return "Positive"
    elif neg_count > pos_count:
        return "Negative"
    else:
        return "Neutral"

def assign_department(text):
    text_lower = text.lower()
    matched_departments = []
    for dept, keywords in department_keywords.items():
        if any(re.search(r'\b' + re.escape(keyword) + r'\b', text_lower, re.IGNORECASE) for keyword in keywords):
            matched_departments.append(dept)
    if matched_departments:
        return list(set(matched_departments))  # Return unique departments
    return [choice(DEPARTMENTS)]  # Fallback to a random department

def generate_ai_feedback_responses(feedback_text, sentiment, departments):
    if sentiment == "Positive":
        return ["Thank you for your positive feedback! We're glad you had a great experience and appreciate you sharing it."]

    department_responses = {
        "Product": [
            "We're sorry for the inconvenience. You can return the product at your nearest retail store, and we'll gladly provide a replacement.",
            "We've received similar feedback about this item. If you'd like to exchange it for a more suitable version, visit our nearest location.",
            "Thank you for your insight. Our product development team has noted your suggestion for our next design iteration.",
            "That's not the experience we intended. We'll pass this on to our product engineers for review.",
            "Appreciate the details! We'll evaluate this feature and see how it fits into our upcoming update roadmap.",
            "We take product feedback seriously—yours has been shared directly with our QA and design leads.",
            "We're actively refining this model. Your experience will help us build a better version.",
            "Could you share the batch or serial number? It'll help us trace any potential production issues.",
            "If you've encountered defects, you may initiate a warranty claim online or via our partner outlets.",
            "Thanks for flagging this—we're reviewing this product line for possible enhancements based on customer reviews like yours."
        ],
        "UX_UI": [
            "Your experience matters. We're forwarding this to our UX lead for review in our next usability audit.",
            "We understand that ease of use is crucial. We're redesigning parts of the interface based on this type of feedback.",
            "Thanks for pointing this out. Could you share screenshots or specific pain points you noticed?",
            "We've logged your concern—our UI designers are already exploring ways to simplify navigation.",
            "We'll use your input during our next user testing round. Would you be open to participating?",
            "Your feedback will help us prioritize accessibility and responsiveness in the next version.",
            "We agree—consistency is key. We'll review the area you mentioned for alignment with our design standards.",
            "Appreciate your honesty. We're reviewing this screen layout for visual clutter and usability.",
            "The feature may need a visual cue. Thanks for helping us catch that.",
            "You're right—first impressions matter. We're reworking onboarding flows to make them more intuitive."
        ],
        "Delivery": [
            "We apologize for the delivery delay. Our logistics partner has been notified, and we're tracking your shipment.",
            "Thank you for your patience—we're coordinating with our courier to expedite your delivery.",
            "We understand your frustration. Please allow us 24 hours to investigate and respond with a resolution.",
            "We're sorry the order didn't arrive on time. We'll credit your delivery fee as a token of apology.",
            "Our delivery team has been alerted. You'll receive a follow-up email with tracking updates shortly.",
            "Thanks for alerting us. We're revalidating delivery routes and timelines to prevent this in the future.",
            "A support ticket has been created. Our team will be in touch with delivery status and options.",
            "You can pick up a replacement at our store while we trace your original shipment—just show your order ID.",
            "We've shared your feedback with the courier supervisor to investigate any service lapses.",
            "We sincerely regret the delay. Expect a callback from our dispatch team within the next 2 business hours."
        ],
        "Logistics": [
            "Thank you for raising this. Our logistics team is analyzing your route to improve delivery accuracy.",
            "Your concern has been forwarded to our warehouse operations to check for handling delays.",
            "We're currently evaluating our storage and dispatch timing based on feedback like yours.",
            "We've escalated your report to our supply chain lead. We'll get back with an update soon.",
            "This may be related to a stock imbalance. We're syncing inventory and restocking critical areas.",
            "We're revising our packaging flow to minimize future delays like the one you faced.",
            "Appreciate the heads-up! We're auditing this fulfillment center for bottlenecks.",
            "Please allow us 48 hours—we're checking with our outbound logistics team for full traceability.",
            "We take logistical feedback seriously. Your case is being reviewed by our regional manager.",
            "A fulfillment issue may have caused this. You'll be notified as soon as a corrective shipment is dispatched."
        ],
        "Sales": [
            "We appreciate your interest—our sales rep will reach out shortly with tailored options.",
            "Thanks for considering our offerings. A personalized deal will be shared via email soon.",
            "We're sorry if your sales experience was underwhelming. Let's get you in touch with a senior advisor.",
            "A product specialist will review your inquiry and connect to clarify the next steps.",
            "We're offering a new bundle this week—you might find something better suited to your needs.",
            "We'll investigate any miscommunication and follow up with better pricing clarity.",
            "Our apologies if pricing was confusing. Here's our direct line to a sales associate: 1800-XXX-XXXX.",
            "Thank you for your feedback. We're updating our product comparison tools for clearer visibility.",
            "We regret any upselling pressure you felt—that's not our standard. The matter is being reviewed.",
            "Your concerns have been shared with the sales leadership to improve team training and transparency."
        ],
        "Marketing": [
            "Thank you for your kind words about our campaign! We're glad it resonated with you.",
            "We're constantly evolving our brand messaging. Your feedback helps us stay relevant.",
            "If the messaging felt unclear, we're taking steps to simplify future promotions.",
            "You've given us a great insight—we'll factor this into our next social rollout.",
            "Your thoughts on the ad visuals are helpful. We've sent them to our creative director.",
            "We're adjusting our outreach frequency based on feedback like yours—thank you.",
            "We appreciate your honesty—sometimes our ads miss the mark, and we're learning from it.",
            "We'd love to hear more about your marketing experience. Want to join our focus group?",
            "Thanks for noticing! That campaign was a pilot—we'll refine it further for the main launch.",
            "Your thoughts have inspired a fresh idea for our next newsletter. Stay tuned!"
        ],
        "Engineering": [
            "Thanks for reporting this. Our engineering team has already started a bug investigation.",
            "We've added this to our active issue tracker. You'll receive updates via email.",
            "This sounds like a backend sync problem. We're looking into server logs to confirm.",
            "Could you share your device/browser details? It'll help replicate the issue more accurately.",
            "A patch is being tested to resolve the glitch you encountered—thanks for catching it.",
            "We're rolling out a stability fix in the next release, which should address your concern.",
            "Our tech lead is reviewing the module you flagged for performance dips.",
            "Thanks for your patience. A detailed technical ticket has been filed with engineering.",
            "We've deployed a hotfix and will monitor for further issues over the next 24 hours.",
            "We've confirmed the bug and are working on a sustainable long-term solution."
        ],
        "Customer_Service": [
            "We deeply apologize for your experience. Our support manager will personally follow up with you.",
            "You deserve better service—we're addressing this with the agent involved.",
            "We're issuing a goodwill credit to your account while we resolve this issue.",
            "Our senior support lead is looking into the situation and will reach out soon.",
            "This falls short of our standards. We've started a full review of your case.",
            "We're expediting this request—expect a resolution email within 12 hours.",
            "Thanks for staying calm. We're grateful for your feedback and will improve from it.",
            "We understand your frustration. Let's fix this quickly and ensure it doesn't happen again.",
            "You're a valued customer, and we're committed to making things right.",
            "Thank you for speaking up. Your message has been heard and action is underway."
        ],
        "QA": [
            "Thanks for flagging this—it's been escalated to our QA analyst team for replication.",
            "We've entered this into our defect tracking system and prioritized it.",
            "We're verifying this across environments to ensure consistency before rollout.",
            "Your experience will help shape future testing coverage—thank you.",
            "Could you help us reproduce this issue? Any steps or screenshots would be helpful.",
            "We're testing this scenario under controlled conditions right now.",
            "Appreciate the detail—your report will be included in our next test suite.",
            "We're comparing your version with baseline builds to isolate the problem.",
            "This will undergo regression testing before the next release window.",
            "Our QA team has confirmed the defect, and it's queued for engineering review."
        ],
        "Billing": [
            "We're sorry for the billing issue. Please share your invoice number so we can investigate immediately.",
            "We've initiated a refund review and will notify you of the outcome shortly.",
            "Your transaction history is being checked to verify the discrepancy.",
            "We understand billing mistakes are frustrating—this will be prioritized.",
            "Please expect a call from our accounts team today to resolve this directly.",
            "We've flagged this for internal reconciliation and will follow up with confirmation.",
            "We're issuing a provisional credit while we validate the charge.",
            "You may download a corrected statement from your account dashboard soon.",
            "We've shared this with our billing software provider to rule out system errors.",
            "Thank you for your patience—we'll have this resolved with full transparency."
        ]
    }

    # Collect responses from all assigned departments
    all_suggestions = []
    for dept in departments:
        if dept in department_responses:
            dept_responses = department_responses[dept]
            if sentiment == "Negative":
                # For negative feedback, prioritize apologetic and solution-focused responses
                relevant_responses = [r for r in dept_responses if any(word in r.lower() for word in ['sorry', 'apologize', 'resolve', 'fix', 'investigate', 'address'])]
                if relevant_responses:
                    # If we have relevant responses, take up to 4 from this department
                    num_to_take = min(4, len(relevant_responses))
                    all_suggestions.extend(sample(relevant_responses, num_to_take))
                else:
                    # If no relevant responses, take up to 4 from all responses
                    num_to_take = min(4, len(dept_responses))
                    all_suggestions.extend(sample(dept_responses, num_to_take))
            else:
                # For neutral/positive feedback, select up to 4 responses
                num_to_take = min(4, len(dept_responses))
                all_suggestions.extend(sample(dept_responses, num_to_take))

    # Remove duplicates
    unique_suggestions = list(set(all_suggestions))
    
    # If we have 4 or more unique suggestions, return exactly 4
    if len(unique_suggestions) >= 4:
        return sample(unique_suggestions, 4)
    
    # If we have less than 4, try to get more from other departments
    if len(unique_suggestions) < 4:
        remaining_needed = 4 - len(unique_suggestions)
        
        # Get responses from other departments that weren't assigned
        other_departments = [dept for dept in DEPARTMENTS if dept not in departments]
        
        for dept in other_departments:
            if dept in department_responses and remaining_needed > 0:
                dept_responses = department_responses[dept]
                if sentiment == "Negative":
                    # For negative feedback, prioritize apologetic responses
                    relevant_responses = [r for r in dept_responses if any(word in r.lower() for word in ['sorry', 'apologize', 'resolve', 'fix', 'investigate', 'address'])]
                    if relevant_responses:
                        num_to_take = min(remaining_needed, len(relevant_responses))
                        additional_suggestions = sample(relevant_responses, num_to_take)
                    else:
                        num_to_take = min(remaining_needed, len(dept_responses))
                        additional_suggestions = sample(dept_responses, num_to_take)
                else:
                    num_to_take = min(remaining_needed, len(dept_responses))
                    additional_suggestions = sample(dept_responses, num_to_take)
                
                # Add new suggestions that aren't duplicates
                for suggestion in additional_suggestions:
                    if suggestion not in unique_suggestions:
                        unique_suggestions.append(suggestion)
                        remaining_needed -= 1
                        if remaining_needed <= 0:
                            break
        
        # If we still don't have 4, just return what we have
        return unique_suggestions[:4] if len(unique_suggestions) > 4 else unique_suggestions
    
    return unique_suggestions

def update_department_points(departments, points_to_add):
    """Update department points in database"""
    try:
        connection = get_mysql_connection()
        if connection:
            cursor = connection.cursor()
            for dept in departments:
                cursor.execute("""
                    INSERT INTO department_points (department, points) 
                    VALUES (%s, %s) 
                    ON DUPLICATE KEY UPDATE points = points + %s
                """, (dept, points_to_add, points_to_add))
            connection.commit()
            cursor.close()
            connection.close()
    except Exception as e:
        print(f"Error updating department points: {e}")
        # Continue without updating points if database fails

def get_department_points():
    """Get all department points from database"""
    try:
        connection = get_mysql_connection()
        if connection:
            cursor = connection.cursor()
            cursor.execute("SELECT department, points FROM department_points")
            results = cursor.fetchall()
            cursor.close()
            connection.close()
            return {row[0]: row[1] for row in results}
        return {}
    except Exception as e:
        print(f"Error getting department points: {e}")
        return {}

def generate_voucher_code():
    """Generate a random 8-character voucher code"""
    characters = string.ascii_uppercase + string.digits
    return ''.join(choice(characters) for _ in range(8))

def get_random_voucher_amount():
    """Get a random voucher amount (100, 200, or 500 Rs)"""
    amounts = [100, 200, 500]
    return choice(amounts)

def create_customer_voucher(customer_id, feedback_id, voucher_code, amount):
    """Create a voucher record in the database"""
    try:
        connection = get_mysql_connection()
        if connection:
            cursor = connection.cursor()
            cursor.execute("""
                INSERT INTO customer_vouchers (customer_id, feedback_id, voucher_code, amount, is_used)
                VALUES (%s, %s, %s, %s, %s)
            """, (customer_id, feedback_id, voucher_code, amount, False))
            connection.commit()
            cursor.close()
            connection.close()
            return True
        return False
    except Exception as e:
        print(f"Error creating voucher: {e}")
        return False

def get_customer_vouchers(customer_id):
    """Get all vouchers for a customer"""
    try:
        connection = get_mysql_connection()
        if connection:
            cursor = connection.cursor()
            cursor.execute("""
                SELECT cv.voucher_code, cv.amount, cv.is_used, cv.created_at
                FROM customer_vouchers cv
                WHERE cv.customer_id = %s
                ORDER BY cv.created_at DESC
            """, (customer_id,))
            results = cursor.fetchall()
            cursor.close()
            connection.close()
            return results
        return []
    except Exception as e:
        print(f"Error getting customer vouchers: {e}")
        return []

# --- Flask Routes ---

@app.route('/')
def home():
    return render_template('main.html', departments=DEPARTMENTS, department_names=DEPARTMENT_NAMES)

# --- Customer-Facing Routes ---

@app.route('/customer_signup', methods=['GET', 'POST'])
def customer_signup():
    if request.method == 'POST':
        name = request.form['name'].strip()
        email = request.form['email'].strip()
        phone = request.form.get('phone', '').strip()
        password = request.form['password']
        confirm_password = request.form['confirm_password']

        # Validation
        if not name or not email or not password:
            flash("All required fields must be filled.", "error")
            return render_template('customer_signup.html')

        if len(password) < 6:
            flash("Password must be at least 6 characters long.", "error")
            return render_template('customer_signup.html')

        if password != confirm_password:
            flash("Passwords do not match.", "error")
            return render_template('customer_signup.html')

        # Check if email already exists
        connection = get_mysql_connection()
        if connection:
            cursor = connection.cursor()
            cursor.execute("SELECT id FROM customers WHERE email = %s", (email,))
            if cursor.fetchone():
                flash("An account with this email already exists.", "error")
                cursor.close()
                connection.close()
                return render_template('customer_signup.html')

            # Check if name already exists
            cursor.execute("SELECT id FROM customers WHERE name = %s", (name,))
            if cursor.fetchone():
                flash("This username is already taken. Please choose another.", "error")
                cursor.close()
                connection.close()
                return render_template('customer_signup.html')

            # Create new customer
            try:
                customer_id = generate_customer_id()
                hashed_password = hash_password(password)
                
                cursor.execute("""
                    INSERT INTO customers (name, customer_id, email, phone, password)
                    VALUES (%s, %s, %s, %s, %s)
                """, (name, customer_id, email, phone, hashed_password))
                
                connection.commit()
                cursor.close()
                connection.close()

                flash(f"Account created successfully! Your Customer ID is: {customer_id}", "success")
                flash("Please login with your username and Customer ID.", "success")
                return redirect(url_for('customer_login'))

            except Exception as e:
                connection.rollback()
                cursor.close()
                connection.close()
                flash("Error creating account. Please try again.", "error")
                return render_template('customer_signup.html')
        else:
            flash("Database connection error. Please try again.", "error")
            return render_template('customer_signup.html')

    return render_template('customer_signup.html')

@app.route('/customer_login', methods=['GET', 'POST'])
def customer_login():
    if request.method == 'POST':
        name = request.form['name']
        cust_id = request.form['id']
        password = request.form['password']

        # First check database
        customer = get_customer_by_credentials(name, cust_id, password)
        
        if customer:
            session['user'] = {
                'id': customer[0],
                'name': customer[1], 
                'customer_id': customer[2],
                'email': customer[3]
            }
            return redirect(url_for('dashboard'))
        
        # Fallback to hardcoded users (for backward compatibility)
        elif name in valid_users:
            user = valid_users[name]
            if user['id'] == cust_id and user['password'] == password:
                session['user'] = {'name': name, 'id': cust_id}
                return redirect(url_for('dashboard'))

        flash("Invalid name, ID, or password.")
    return render_template('customer_login.html')

@app.route('/dashboard')
def dashboard():
    if 'user' not in session:
        return redirect(url_for('customer_login'))
    return render_template('dashboard.html', user=session['user'])

@app.route('/submit_feedback', methods=['GET', 'POST'])
def submit_feedback():
    if 'user' not in session:
        return redirect(url_for('customer_login'))
    
    if request.method == 'POST':
        feedback_text = request.form['feedback']
        if not feedback_text.strip():
            flash("Feedback cannot be empty.")
            return render_template('submit_feedback.html')

        user = session['user']
        sentiment = get_sentiment(feedback_text)
        departments = assign_department(feedback_text)
        suggestions = generate_ai_feedback_responses(feedback_text, sentiment, departments)

        # Award points to departments based on sentiment
        points_to_add = 0
        if sentiment == "Positive": 
            points_to_add = 10
        elif sentiment == "Neutral": 
            points_to_add = 5
        
        # Update department points
        if points_to_add > 0:
            update_department_points(departments, points_to_add)

        # Insert feedback into database
        try:
            connection = get_mysql_connection()
            if connection:
                cursor = connection.cursor()
                
                # Use customer_id from session (could be database ID or legacy string ID)
                customer_identifier = user.get('customer_id', user.get('id'))
                
                cursor.execute("""
                    INSERT INTO feedback (name, customer_id, feedback, sentiment, departments, suggestions)
                    VALUES (%s, %s, %s, %s, %s, %s)
                """, (user['name'], customer_identifier, feedback_text, sentiment, 
                      json.dumps(departments), json.dumps(suggestions)))
                
                # Get the feedback ID for voucher creation
                feedback_id = cursor.lastrowid
                
                # Generate voucher for customer
                voucher_code = generate_voucher_code()
                voucher_amount = get_random_voucher_amount()
                
                # Create voucher record
                create_customer_voucher(customer_identifier, feedback_id, voucher_code, voucher_amount)
                
                connection.commit()
                cursor.close()
                connection.close()
                
                # Success message with voucher details
                flash(f"Feedback submitted! Assigned to: {', '.join(d.replace('_', '/') for d in departments)}")
                flash(f"🎉 Congratulations! You've earned a ₹{voucher_amount} voucher! Code: {voucher_code}", "success")
                flash("Use this code to redeem your voucher at any of our partner stores.", "info")
            else:
                raise Exception("Could not establish database connection")
        except Exception as e:
            print(f"Error inserting feedback: {e}")
            flash("Feedback submitted but there was an issue saving to database. Please try again later.")
            return redirect(url_for('dashboard'))

        return redirect(url_for('dashboard'))
    
    return render_template('submit_feedback.html')

@app.route('/view_feedback')
def view_feedback():
    if 'user' not in session:
        return redirect(url_for('customer_login'))
    
    try:
        user = session['user']
        customer_identifier = user.get('customer_id', user.get('id'))
        
        connection = get_mysql_connection()
        if connection:
            cursor = connection.cursor()
            cursor.execute("""
                SELECT f.id, f.name, f.customer_id, f.feedback, f.sentiment, f.departments, 
                       f.suggestions, f.created_at,
                       GROUP_CONCAT(DISTINCT ar.department SEPARATOR ',') as response_departments,
                       GROUP_CONCAT(DISTINCT ar.response SEPARATOR '|||') as responses
                FROM feedback f
                LEFT JOIN admin_responses ar ON f.id = ar.feedback_id
                WHERE f.customer_id = %s
                GROUP BY f.id
                ORDER BY f.created_at DESC
            """, (customer_identifier,))
            
            feedback_rows = cursor.fetchall()
            
            # Get existing ratings for all feedback
            cursor.execute("""
                SELECT feedback_id, department, rating
                FROM customer_ratings
                WHERE feedback_id IN (SELECT id FROM feedback WHERE customer_id = %s)
            """, (customer_identifier,))
            
            ratings_rows = cursor.fetchall()
            cursor.close()
            connection.close()
        else:
            feedback_rows = []
            ratings_rows = []

        # Convert to list of dictionaries for template compatibility
        user_feedback = []
        for row in feedback_rows:
            feedback_dict = {
                'id': row[0],
                'name': row[1],
                'customer_id': row[2],
                'feedback': row[3],
                'sentiment': row[4],
                'departments': safe_json_loads(row[5]),
                'suggestions': safe_json_loads(row[6]),
                'created_at': row[7],
                'admin_responses': {},
                'ratings': {}
            }
            
            # Parse admin responses
            if row[8] and row[9]:
                response_depts = row[8].split(',')
                responses = row[9].split('|||')
                for dept, response in zip(response_depts, responses):
                    feedback_dict['admin_responses'][dept] = response
            
            user_feedback.append(feedback_dict)

        # Add ratings to feedback
        for rating_row in ratings_rows:
            feedback_id, department, rating = rating_row
            for feedback in user_feedback:
                if feedback['id'] == feedback_id:
                    feedback['ratings'][department] = rating
                    break

        return render_template('view_feedback.html', feedbacks=user_feedback)
    except Exception as e:
        print(f"Error loading feedback: {e}")
        flash("Error loading feedback. Please try again.", "error")
        return render_template('view_feedback.html', feedbacks=[])

@app.route('/rate_response', methods=['POST'])
def rate_response():
    if 'user' not in session:
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return jsonify({'success': False, 'message': 'Please log in to rate responses.'})
        return redirect(url_for('customer_login'))
    
    try:
        feedback_id = request.form.get('feedback_id')
        department_key = request.form.get('department_key')
        rating = int(request.form.get('rating'))

        connection = get_mysql_connection()
        if connection:
            cursor = connection.cursor()
            
            # Check if already rated
            cursor.execute("""
                SELECT id FROM customer_ratings 
                WHERE feedback_id = %s AND department = %s
            """, (feedback_id, department_key))
            
            if cursor.fetchone():
                if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                    return jsonify({'success': False, 'message': 'You have already rated this response.'})
                flash("You have already rated this response.", "error")
            else:
                # Insert rating
                cursor.execute("""
                    INSERT INTO customer_ratings (feedback_id, department, rating)
                    VALUES (%s, %s, %s)
                """, (feedback_id, department_key, rating))
                
                # Award points based on rating
                points_from_rating = rating * 2
                update_department_points([department_key], points_from_rating)
                
                if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                    return jsonify({'success': True, 'message': f'Thank you for rating the response from {department_key.replace("_","/")}!'})
                flash(f"Thank you for rating the response from {department_key.replace('_','/')}!")
            
            connection.commit()
            cursor.close()
            connection.close()
        else:
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return jsonify({'success': False, 'message': 'Database connection error. Please try again.'})
            flash("Database connection error. Please try again.", "error")
        
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return jsonify({'success': True})
        return redirect(url_for('view_feedback'))
    except Exception as e:
        print(f"Error rating response: {e}")
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return jsonify({'success': False, 'message': 'Error saving rating. Please try again.'})
        flash("Error saving rating. Please try again.", "error")
        return redirect(url_for('view_feedback'))

@app.route('/my_vouchers')
def my_vouchers():
    if 'user' not in session:
        return redirect(url_for('customer_login'))
    
    try:
        user = session['user']
        customer_identifier = user.get('customer_id', user.get('id'))
        
        vouchers = get_customer_vouchers(customer_identifier)
        
        # Convert to list of dictionaries for template
        voucher_list = []
        for voucher in vouchers:
            voucher_list.append({
                'code': voucher[0],
                'amount': voucher[1],
                'is_used': voucher[2],
                'created_at': voucher[3]
            })
        
        return render_template('my_vouchers.html', vouchers=voucher_list)
    except Exception as e:
        print(f"Error loading vouchers: {e}")
        flash("Error loading vouchers. Please try again.", "error")
        return render_template('my_vouchers.html', vouchers=[])

# --- Department-Specific Routes with Enhanced Security ---

@app.route('/department/<department_key>/signup', methods=['GET', 'POST'])
def department_signup(department_key):
    if department_key not in DEPARTMENTS:
        flash("Invalid department.", "error")
        return redirect(url_for('home'))
    
    # Clear any existing sessions for security
    clear_all_sessions()
    
    department_name = DEPARTMENT_NAMES.get(department_key, department_key)
    
    if request.method == 'POST':
        full_name = request.form['full_name'].strip()
        username = request.form['username'].strip()
        email = request.form['email'].strip()
        password = request.form['password']
        confirm_password = request.form['confirm_password']

        # Validation
        if not full_name or not username or not email or not password:
            flash("All required fields must be filled.", "error")
            return render_template('department_signup.html', 
                                 department_key=department_key, 
                                 department_name=department_name)

        if len(password) < 8:
            flash("Password must be at least 8 characters long.", "error")
            return render_template('department_signup.html', 
                                 department_key=department_key, 
                                 department_name=department_name)

        if password != confirm_password:
            flash("Passwords do not match.", "error")
            return render_template('department_signup.html', 
                                 department_key=department_key, 
                                 department_name=department_name)

        connection = get_mysql_connection()
        if connection:
            cursor = connection.cursor()
            
            # Check if username exists in ANY department (should be unique globally)
            cursor.execute("SELECT id, department FROM department_admins WHERE username = %s", (username,))
            existing_user = cursor.fetchone()
            if existing_user:
                flash(f"Username '{username}' already exists in {existing_user[1]} department. Please choose another.", "error")
                cursor.close()
                connection.close()
                return render_template('department_signup.html', 
                                     department_key=department_key, 
                                     department_name=department_name)

            # Check if email exists in ANY department
            cursor.execute("SELECT id, department FROM department_admins WHERE email = %s", (email,))
            existing_email = cursor.fetchone()
            if existing_email:
                flash(f"Email already registered in {existing_email[1]} department.", "error")
                cursor.close()
                connection.close()
                return render_template('department_signup.html', 
                                     department_key=department_key, 
                                     department_name=department_name)

            # Create new department admin
            try:
                hashed_password = hash_password(password)
                
                cursor.execute("""
                    INSERT INTO department_admins (username, full_name, email, department, password)
                    VALUES (%s, %s, %s, %s, %s)
                """, (username, full_name, email, department_key, hashed_password))
                
                connection.commit()
                cursor.close()
                connection.close()

                flash(f"Account created successfully for {department_name}!", "success")
                flash("Please login with your credentials.", "success")
                return redirect(url_for('department_login', department_key=department_key))

            except Exception as e:
                connection.rollback()
                cursor.close()
                connection.close()
                flash("Error creating account. Please try again.", "error")
                return render_template('department_signup.html', 
                                     department_key=department_key, 
                                     department_name=department_name)
        else:
            flash("Database connection error. Please try again.", "error")
            return render_template('department_signup.html', 
                                 department_key=department_key, 
                                 department_name=department_name)

    return render_template('department_signup.html', 
                         department_key=department_key, 
                         department_name=department_name)

@app.route('/department/<department_key>/login', methods=['GET', 'POST'])
def department_login(department_key):
    if department_key not in DEPARTMENTS:
        flash("Invalid department.", "error")
        return redirect(url_for('home'))
    
    # Clear any existing sessions for security
    clear_all_sessions()
    
    department_name = DEPARTMENT_NAMES.get(department_key, department_key)
    
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')

        if not username or not password:
            flash("Please enter both username and password.", "error")
            return render_template('department_login.html', 
                                 department_key=department_key, 
                                 department_name=department_name)

        # STRICT department credential checking
        admin = get_department_admin_by_credentials(username, password, department_key)
        
        if admin:
            # Verify department match one more time for extra security
            if admin[4] != department_key:
                flash("Access denied for this department.", "error")
                return render_template('department_login.html', 
                                     department_key=department_key, 
                                     department_name=department_name)
            
            # Set session with department verification
            session['department_admin'] = {
                'id': admin[0],
                'username': admin[1],
                'full_name': admin[2],
                'email': admin[3],
                'department': admin[4]
            }
            session['current_department'] = department_key  # Extra security check
            
            flash(f"Welcome to {department_name}!", "success")
            return redirect(url_for('department_dashboard', department_key=department_key))
        else:
            flash(f"Invalid credentials for {department_name}.", "error")
    
    return render_template('department_login.html', 
                         department_key=department_key, 
                         department_name=department_name)

@app.route('/department/<department_key>/dashboard')
def department_dashboard(department_key):
    if 'department_admin' not in session:
        flash("Please log in to access this department.", "error")
        return redirect(url_for('department_login', department_key=department_key))
    if not verify_department_access(department_key):
        flash("Access denied. You don't have permission for this department.", "error")
        clear_all_sessions()
        return redirect(url_for('department_login', department_key=department_key))
    if session.get('current_department') != department_key:
        flash("Session security violation. Please log in again.", "error")
        clear_all_sessions()
        return redirect(url_for('department_login', department_key=department_key))
    department_name = DEPARTMENT_NAMES.get(department_key, department_key)
    try:
        connection = get_mysql_connection()
        if connection:
            cursor = connection.cursor()
            cursor.execute("SELECT * FROM feedback ORDER BY created_at DESC")
            all_feedback = cursor.fetchall()
            cursor.close()
            connection.close()
        else:
            all_feedback = []
        department_feedback = []
        for row in all_feedback:
            departments = safe_json_loads(row[5])
            if department_key in departments:
                department_feedback.append({
                    'id': row[0],
                    'name': row[1],
                    'customer_id': row[2],
                    'feedback': row[3],
                    'sentiment': row[4],
                    'departments': departments,
                    'suggestions': safe_json_loads(row[6]),
                    'created_at': row[7],
                    'admin_responses': {},
                    'ratings': {}
                })
        connection = get_mysql_connection()
        if connection:
            cursor = connection.cursor()
            cursor.execute("SELECT points FROM department_points WHERE department = %s", (department_key,))
            result = cursor.fetchone()
            cursor.close()
            connection.close()
            department_score = result[0] if result else 0
        else:
            department_score = 0
    except Exception as e:
        print(f"Error loading department dashboard: {e}")
        department_feedback = []
        department_score = 0
    return render_template('department_dashboard.html', 
                         department_key=department_key,
                         department_name=department_name,
                         feedbacks=department_feedback,
                         department_score=department_score,
                         admin=session['department_admin'])

@app.route('/department/<department_key>/send_response', methods=['POST'])
def department_send_response(department_key):
    # Security checks
    if not verify_department_access(department_key):
        flash("Access denied.", "error")
        return redirect(url_for('department_login', department_key=department_key))

    # Additional check: verify current_department session
    if session.get('current_department') != department_key:
        flash("Session security violation. Please log in again.", "error")
        clear_all_sessions()
        return redirect(url_for('department_login', department_key=department_key))

    feedback_id = request.form.get('feedback_id')
    response_text = request.form.get('response', '').strip()

    if not response_text:
        flash("Response cannot be empty.", "error")
        return redirect(url_for('department_dashboard', department_key=department_key))

    connection = get_mysql_connection()
    if connection:
        cursor = connection.cursor()
        cursor.execute("""
            INSERT INTO admin_responses (feedback_id, department, response)
            VALUES (%s, %s, %s)
            ON DUPLICATE KEY UPDATE response = %s
        """, (feedback_id, department_key, response_text, response_text))
        
        connection.commit()
        cursor.close()
        connection.close()
    else:
        flash("Database connection error. Please try again.", "error")
        return redirect(url_for('department_dashboard', department_key=department_key))
    
    flash("Response sent successfully!", "success")
    return redirect(url_for('department_dashboard', department_key=department_key))

# --- Super Admin Routes (Original admin functionality) ---

@app.route('/admin_signup', methods=['GET', 'POST'])
def admin_signup():
    if request.method == 'POST':
        full_name = request.form['full_name'].strip()
        username = request.form['username'].strip()
        email = request.form['email'].strip()
        department = request.form.get('department', '').strip()
        password = request.form['password']
        confirm_password = request.form['confirm_password']

        # Validation
        if not full_name or not username or not email or not password:
            flash("All required fields must be filled.", "error")
            return render_template('admin_signup.html')

        if len(password) < 8:
            flash("Password must be at least 8 characters long.", "error")
            return render_template('admin_signup.html')

        if password != confirm_password:
            flash("Passwords do not match.", "error")
            return render_template('admin_signup.html')

        # Check if email already exists
        connection = get_mysql_connection()
        if connection:
            cursor = connection.cursor()
            cursor.execute("SELECT id FROM admins WHERE email = %s", (email,))
            if cursor.fetchone():
                flash("An admin account with this email already exists.", "error")
                cursor.close()
                connection.close()
                return render_template('admin_signup.html')

            # Check if username already exists
            cursor.execute("SELECT id FROM admins WHERE username = %s", (username,))
            if cursor.fetchone():
                flash("This username is already taken. Please choose another.", "error")
                cursor.close()
                connection.close()
                return render_template('admin_signup.html')

            # Create new admin
            try:
                hashed_password = hash_password(password)
                
                cursor.execute("""
                    INSERT INTO admins (username, full_name, email, department, password)
                    VALUES (%s, %s, %s, %s, %s)
                """, (username, full_name, email, department, hashed_password))
                
                connection.commit()
                cursor.close()
                connection.close()

                flash("Super admin account created successfully!", "success")
                flash("Please login with your username and password.", "success")
                return redirect(url_for('admin_login'))

            except Exception as e:
                connection.rollback()
                cursor.close()
                connection.close()
                flash("Error creating admin account. Please try again.", "error")
                return render_template('admin_signup.html')
        else:
            flash("Database connection error. Please try again.", "error")
            return render_template('admin_signup.html')

    return render_template('admin_signup.html')

@app.route('/admin_login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        # First check database
        admin = get_admin_by_credentials(username, password)
        
        if admin:
            session['admin'] = {
                'id': admin[0],
                'username': admin[1],
                'full_name': admin[2],
                'email': admin[3],
                'department': admin[4]
            }
            return redirect(url_for('admin_dashboard'))
        
        # Fallback to hardcoded admin (for backward compatibility)
        elif username == admin_user['username'] and password == admin_user['password']:
            session['admin'] = {'username': username}
            return redirect(url_for('admin_dashboard'))
        
        else:
            flash("Invalid admin credentials", "error")
    
    return render_template('admin_login.html')

@app.route('/admin_dashboard')
def admin_dashboard():
    if 'admin' not in session:
        return redirect(url_for('admin_login'))
    try:
        connection = get_mysql_connection()
        if connection:
            cursor = connection.cursor()
            cursor.execute("SELECT * FROM feedback ORDER BY created_at DESC")
            all_feedback = cursor.fetchall()
            cursor.close()
            connection.close()
        else:
            all_feedback = []
        feedback_by_dept = {dept: [] for dept in DEPARTMENTS}
        for row in all_feedback:
            departments = safe_json_loads(row[5])
            for dept in departments:
                if dept in feedback_by_dept:
                    feedback_by_dept[dept].append({
                        'id': row[0],
                        'name': row[1],
                        'customer_id': row[2],
                        'feedback': row[3],
                        'sentiment': row[4],
                        'departments': departments,
                        'suggestions': safe_json_loads(row[6]),
                        'created_at': row[7],
                        'admin_responses': {},
                        'ratings': {}
                    })
        return render_template('admin_dashboard.html', feedback_by_dept=feedback_by_dept)
    except Exception as e:
        print(f"Error loading admin dashboard: {e}")
        flash("Error loading dashboard data. Please try again.", "error")
        return render_template('admin_dashboard.html', feedback_by_dept={dept: [] for dept in DEPARTMENTS})

@app.route('/rewards')
def rewards():
    if 'admin' not in session:
        return redirect(url_for('admin_login'))
    
    try:
        department_points = get_department_points()
        
        # Calculate statistics
        total_points = sum(department_points.values())
        total_departments = len(department_points)
        avg_points = round(total_points / total_departments, 1) if total_departments > 0 else 0
        top_department_points = max(department_points.values()) if department_points else 0
        
        # Sort departments by points (descending)
        department_points_sorted = sorted(department_points.items(), key=lambda x: x[1], reverse=True)
        
        # Calculate percentages
        percentages = {}
        for dept, points in department_points.items():
            if total_points > 0:
                percentages[dept] = round((points / total_points) * 100, 1)
            else:
                percentages[dept] = 0
        
        # Get top 3 departments
        top_departments = department_points_sorted[:3]
        
        return render_template('rewards.html', 
                             department_points=department_points,
                             department_points_sorted=department_points_sorted,
                             percentages=percentages,
                             total_points=total_points,
                             total_departments=total_departments,
                             avg_points=avg_points,
                             top_department_points=top_department_points,
                             top_departments=top_departments)
    except Exception as e:
        print(f"Error loading rewards: {e}")
        flash("Error loading rewards data. Please try again.", "error")
        return render_template('rewards.html', 
                             department_points={},
                             department_points_sorted=[],
                             percentages={},
                             total_points=0,
                             total_departments=0,
                             avg_points=0,
                             top_department_points=0,
                             top_departments=[])

@app.route('/admin/feedback/<department_key>')
def admin_view_department(department_key):
    if 'admin' not in session:
        return redirect(url_for('admin_login'))
    try:
        connection = get_mysql_connection()
        if connection:
            cursor = connection.cursor()
            cursor.execute("""
                SELECT f.*, ar.response as admin_response
                FROM feedback f
                LEFT JOIN admin_responses ar ON f.id = ar.feedback_id AND ar.department = %s
                ORDER BY f.created_at DESC
            """, (department_key,))
            all_feedback_rows = cursor.fetchall()
            cursor.close()
            connection.close()
        else:
            all_feedback_rows = []
        feedbacks = []
        for row in all_feedback_rows:
            departments = safe_json_loads(row[5])
            if department_key in departments:
                feedbacks.append({
                    'id': row[0],
                    'name': row[1],
                    'customer_id': row[2],
                    'feedback': row[3],
                    'sentiment': row[4],
                    'departments': departments,
                    'suggestions': safe_json_loads(row[6]),
                    'created_at': row[7],
                    'admin_responses': {department_key: row[8]} if row[8] else {},
                    'ratings': {}
                })
        display_name = department_key.replace('_', '/')
        department_points = get_department_points()
        department_score = department_points.get(department_key, 0)
    except Exception as e:
        print(f"Error loading department feedback: {e}")
        feedbacks = []
        display_name = department_key.replace('_', '/')
        department_score = 0
    return render_template(
        'department_feedback.html',
        department_name=display_name,
        department_key=department_key,
        feedbacks=feedbacks,
        department_score=department_score
    )

@app.route('/send_response', methods=['POST'])
def send_response():
    if 'admin' not in session:
        return redirect(url_for('admin_login'))

    try:
        feedback_id = request.form.get('feedback_id')
        response_text = request.form.get('response')
        department_key = request.form.get('department_key')

        connection = get_mysql_connection()
        if connection:
            cursor = connection.cursor()
            cursor.execute("""
                INSERT INTO admin_responses (feedback_id, department, response)
                VALUES (%s, %s, %s)
                ON DUPLICATE KEY UPDATE response = %s
            """, (feedback_id, department_key, response_text, response_text))
            
            connection.commit()
            cursor.close()
            connection.close()
        else:
            flash("Database connection error. Please try again.", "error")
            return redirect(url_for('admin_view_department', department_key=department_key))
        
        flash(f"Response from {department_key.replace('_','/')} has been sent!")
        return redirect(url_for('admin_view_department', department_key=department_key))
    except Exception as e:
        print(f"Error sending response: {e}")
        flash("Error sending response. Please try again.", "error")
        return redirect(url_for('admin_view_department', department_key=department_key))

@app.route('/approve_suggestion', methods=['POST'])
def approve_suggestion():
    """Approve and send an AI suggestion as a response"""
    if 'admin' not in session and 'department_admin' not in session:
        flash("Access denied. Please log in.", "error")
        return redirect(url_for('home'))
    
    try:
        feedback_id = request.form.get('feedback_id')
        suggestion = request.form.get('suggestion')
        department_key = request.form.get('department_key')
        
        if not feedback_id or not suggestion or not department_key:
            flash("Missing required information.", "error")
            return redirect(url_for('admin_dashboard'))
        
        # Send the approved suggestion as a response
        connection = get_mysql_connection()
        if connection:
            cursor = connection.cursor()
            cursor.execute("""
                INSERT INTO admin_responses (feedback_id, department, response)
                VALUES (%s, %s, %s)
                ON DUPLICATE KEY UPDATE response = %s
            """, (feedback_id, department_key, suggestion, suggestion))
            
            connection.commit()
            cursor.close()
            connection.close()
            
            flash(f"Response from {department_key.replace('_','/')} has been sent successfully!", "success")
        else:
            flash("Database connection error. Please try again.", "error")
            
        # Redirect back to the appropriate page
        if 'admin' in session:
            return redirect(url_for('admin_view_department', department_key=department_key))
        else:
            return redirect(url_for('department_dashboard', department_key=department_key))
            
    except Exception as e:
        print(f"Error approving suggestion: {e}")
        flash("Error sending response. Please try again.", "error")
        return redirect(url_for('admin_dashboard'))

@app.route('/logout')
def logout():
    clear_all_sessions()
    flash("You have been logged out successfully.", "success")
    return redirect(url_for('home'))

if __name__ == '__main__':
    print("🔧 Testing MySQL connection...")
    test_mysql_connection()
    print("🚀 Starting Flask application...")
    app.run(debug=True, port=5001)
