#!/usr/bin/env python3
"""
Create a mock SQLite database for SoftwareOne employees.
This script creates a realistic employee database for a technology consulting company.
"""

import sqlite3
import random
from datetime import datetime, timedelta
import os

# Database path
DB_PATH = "database/softwareone_employees.db"

# Sample data
DEPARTMENTS = [
    ("IT Services", "Information Technology Services"),
    ("Cloud Solutions", "Cloud Computing and Migration"),
    ("Cybersecurity", "Security and Risk Management"),
    ("Digital Transformation", "Business Process Optimization"),
    ("Data Analytics", "Business Intelligence and Analytics"),
    ("Software Development", "Custom Software Development"),
    ("HR", "Human Resources"),
    ("Finance", "Financial Operations"),
    ("Sales", "Sales and Business Development"),
    ("Marketing", "Marketing and Communications")
]

POSITIONS = [
    ("Software Engineer", "Entry-level developer", 45000),
    ("Senior Software Engineer", "Experienced developer", 75000),
    ("Principal Engineer", "Senior technical lead", 95000),
    ("Engineering Manager", "Team management", 85000),
    ("Senior Engineering Manager", "Multiple team leadership", 110000),
    ("Director of Engineering", "Department leadership", 135000),
    ("VP of Engineering", "Executive leadership", 165000),
    ("Cloud Architect", "Cloud infrastructure design", 85000),
    ("DevOps Engineer", "CI/CD and infrastructure", 70000),
    ("Data Scientist", "Data analysis and ML", 80000),
    ("Data Engineer", "Data pipeline development", 75000),
    ("Security Analyst", "Security monitoring", 65000),
    ("Security Engineer", "Security implementation", 80000),
    ("Project Manager", "Project coordination", 70000),
    ("Senior Project Manager", "Complex project management", 85000),
    ("Business Analyst", "Requirements analysis", 60000),
    ("Product Manager", "Product strategy", 90000),
    ("UX Designer", "User experience design", 65000),
    ("UI Designer", "User interface design", 60000),
    ("QA Engineer", "Quality assurance", 55000),
    ("HR Specialist", "Human resources", 55000),
    ("HR Manager", "HR operations", 75000),
    ("Financial Analyst", "Financial planning", 65000),
    ("Accountant", "Accounting operations", 60000),
    ("Sales Representative", "Sales operations", 55000),
    ("Account Executive", "Enterprise sales", 75000),
    ("Marketing Specialist", "Marketing campaigns", 55000),
    ("Marketing Manager", "Marketing strategy", 75000)
]

FIRST_NAMES = [
    "Nguyen", "Tran", "Le", "Pham", "Ho", "Vu", "Vo", "Dang", "Bui", "Do",
    "Hoang", "Phan", "Truong", "Ngo", "Duong", "Ly", "Vuong", "Trinh", "Dinh", "Lai",
    "Tong", "Chu", "Thai", "Chu", "Ta", "Kim", "Cao", "Mai", "Dam", "Lam",
    "An", "Quach", "Ha", "Huynh", "Giang", "Tu", "Uong", "Kieu", "Luu", "Dong"
]

LAST_NAMES = [
    "Anh", "Minh", "Hoa", "Lan", "Linh", "Huong", "Mai", "Tuyen", "Trang", "Hien",
    "Thao", "Phuong", "Yen", "Nga", "Ha", "Hong", "Ly", "Tram", "Lien", "Diep",
    "Quyen", "Thu", "Hue", "Van", "Nhi", "My", "Kieu", "Tuyet", "Oanh", "Hang",
    "Ngan", "Chau", "Lam", "Ngoc", "Bich", "Diem", "Loan", "Anh", "Tuan", "Dung"
]

CITIES = [
    ("Ho Chi Minh City", "Vietnam"),
    ("Hanoi", "Vietnam"),
    ("Da Nang", "Vietnam"),
    ("Hai Phong", "Vietnam"),
    ("Can Tho", "Vietnam"),
    ("Singapore", "Singapore"),
    ("Bangalore", "India"),
    ("Mumbai", "India"),
    ("Zurich", "Switzerland"),
    ("Geneva", "Switzerland"),
    ("London", "United Kingdom"),
    ("Manchester", "United Kingdom"),
    ("New York", "United States"),
    ("San Francisco", "United States"),
    ("Austin", "United States")
]

PROJECTS = [
    ("Cloud Migration AWS", "Migrating legacy systems to AWS cloud", "Cloud Solutions"),
    ("Digital Workplace", "Implementing Microsoft 365 and collaboration tools", "Digital Transformation"),
    ("Cybersecurity Assessment", "Comprehensive security audit and remediation", "Cybersecurity"),
    ("Data Lake Implementation", "Building enterprise data lake on Azure", "Data Analytics"),
    ("ERP Modernization", "SAP S/4HANA implementation", "IT Services"),
    ("Mobile App Development", "Cross-platform mobile application", "Software Development"),
    ("AI Chatbot", "Conversational AI for customer service", "Data Analytics"),
    ("Infrastructure Automation", "DevOps pipeline and infrastructure as code", "Cloud Solutions"),
    ("GDPR Compliance", "Data privacy and compliance implementation", "Cybersecurity"),
    ("Business Intelligence Dashboard", "Executive reporting and analytics", "Data Analytics"),
    ("Microservices Architecture", "Application modernization to microservices", "Software Development"),
    ("Zero Trust Security", "Implementing zero trust security model", "Cybersecurity"),
    ("IoT Platform", "Internet of Things data collection platform", "Data Analytics"),
    ("API Gateway", "Centralized API management and security", "IT Services"),
    ("Machine Learning Platform", "ML model development and deployment", "Data Analytics")
]

def create_database():
    """Create the SoftwareOne employees database with all tables and data."""

    # Ensure database directory exists
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)

    # Remove existing database if it exists
    if os.path.exists(DB_PATH):
        os.remove(DB_PATH)

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Create tables
    create_tables(cursor)

    # Insert data
    insert_departments(cursor)
    insert_positions(cursor)
    insert_employees(cursor)
    insert_projects(cursor)
    insert_employee_projects(cursor)

    conn.commit()
    conn.close()

    print(f"Mock database created successfully at {DB_PATH}")
    print(f"Database contains:")
    print("- Departments: 10")
    print("- Positions: 28")
    print("- Employees: 200")
    print("- Projects: 15")
    print("- Employee-Project assignments: ~400")

def create_tables(cursor):
    """Create all database tables."""

    # Departments table
    cursor.execute('''
        CREATE TABLE departments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE,
            description TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    # Positions table
    cursor.execute('''
        CREATE TABLE positions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL UNIQUE,
            description TEXT,
            base_salary REAL,
            department_id INTEGER,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (department_id) REFERENCES departments (id)
        )
    ''')

    # Employees table
    cursor.execute('''
        CREATE TABLE employees (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            employee_id TEXT NOT NULL UNIQUE,
            first_name TEXT NOT NULL,
            last_name TEXT NOT NULL,
            email TEXT NOT NULL UNIQUE,
            phone TEXT,
            hire_date DATE NOT NULL,
            position_id INTEGER NOT NULL,
            department_id INTEGER NOT NULL,
            manager_id INTEGER,
            city TEXT,
            country TEXT,
            salary REAL,
            status TEXT DEFAULT 'Active',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (position_id) REFERENCES positions (id),
            FOREIGN KEY (department_id) REFERENCES departments (id),
            FOREIGN KEY (manager_id) REFERENCES employees (id)
        )
    ''')

    # Projects table
    cursor.execute('''
        CREATE TABLE projects (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE,
            description TEXT,
            department_name TEXT,
            start_date DATE,
            end_date DATE,
            status TEXT DEFAULT 'Active',
            budget REAL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    # Employee-Projects junction table
    cursor.execute('''
        CREATE TABLE employee_projects (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            employee_id INTEGER NOT NULL,
            project_id INTEGER NOT NULL,
            role TEXT,
            start_date DATE,
            end_date DATE,
            allocation_percentage REAL DEFAULT 100.0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (employee_id) REFERENCES employees (id),
            FOREIGN KEY (project_id) REFERENCES projects (id),
            UNIQUE(employee_id, project_id, start_date)
        )
    ''')

def insert_departments(cursor):
    """Insert department data."""
    cursor.executemany(
        "INSERT INTO departments (name, description) VALUES (?, ?)",
        DEPARTMENTS
    )

def insert_positions(cursor):
    """Insert position data."""
    # Get department IDs
    cursor.execute("SELECT id, name FROM departments")
    dept_map = {name: id for id, name in cursor.fetchall()}

    position_data = []
    for title, desc, salary in POSITIONS:
        # Assign positions to appropriate departments
        if "Engineer" in title or "Architect" in title or "DevOps" in title:
            dept_id = dept_map["Software Development"]
        elif "Data" in title:
            dept_id = dept_map["Data Analytics"]
        elif "Security" in title:
            dept_id = dept_map["Cybersecurity"]
        elif "Cloud" in title:
            dept_id = dept_map["Cloud Solutions"]
        elif "Manager" in title or "Director" in title or "VP" in title:
            dept_id = random.choice([dept_map["IT Services"], dept_map["Software Development"], dept_map["Cloud Solutions"]])
        elif "HR" in title:
            dept_id = dept_map["HR"]
        elif "Financial" in title or "Accountant" in title:
            dept_id = dept_map["Finance"]
        elif "Sales" in title or "Account Executive" in title:
            dept_id = dept_map["Sales"]
        elif "Marketing" in title:
            dept_id = dept_map["Marketing"]
        elif "Project Manager" in title or "Business Analyst" in title:
            dept_id = dept_map["Digital Transformation"]
        elif "Product Manager" in title or "Designer" in title:
            dept_id = dept_map["Digital Transformation"]
        elif "QA" in title:
            dept_id = dept_map["Software Development"]
        else:
            dept_id = random.choice(list(dept_map.values()))

        position_data.append((title, desc, salary, dept_id))

    cursor.executemany(
        "INSERT INTO positions (title, description, base_salary, department_id) VALUES (?, ?, ?, ?)",
        position_data
    )

def insert_employees(cursor):
    """Insert employee data."""
    employees = []

    # Get positions and departments
    cursor.execute("SELECT id, title, department_id FROM positions")
    positions = cursor.fetchall()

    # Create 200 employees
    for i in range(1, 201):
        emp_id = f"EMP{i:04d}"
        first_name = random.choice(FIRST_NAMES)
        last_name = random.choice(LAST_NAMES)
        email = f"{first_name.lower()}.{last_name.lower()}{i}@softwareone.com"
        phone = ""

        # Random hire date between 2018 and 2024
        hire_date = datetime(2018, 1, 1) + timedelta(days=random.randint(0, 2555))
        hire_date_str = hire_date.strftime("%Y-%m-%d")

        # Assign position
        position = random.choice(positions)
        position_id = position[0]
        department_id = position[2]

        # Random city/country
        city, country = random.choice(CITIES)

        # Calculate salary (base ± 20%)
        base_salary = cursor.execute("SELECT base_salary FROM positions WHERE id = ?", (position_id,)).fetchone()[0]
        salary_variation = random.uniform(-0.2, 0.2)
        salary = base_salary * (1 + salary_variation)

        employees.append((
            emp_id, first_name, last_name, email, phone, hire_date_str,
            position_id, department_id, city, country, salary
        ))

    cursor.executemany('''
        INSERT INTO employees (employee_id, first_name, last_name, email, phone, hire_date,
                              position_id, department_id, city, country, salary)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', employees)

    # Assign managers (employees with manager positions)
    cursor.execute("SELECT id FROM positions WHERE title LIKE '%Manager%' OR title LIKE '%Director%' OR title LIKE '%VP%'")
    manager_positions = [row[0] for row in cursor.fetchall()]

    cursor.execute(f"SELECT id FROM employees WHERE position_id IN ({','.join('?' * len(manager_positions))})", manager_positions)
    manager_ids = [row[0] for row in cursor.fetchall()]

    # Assign random managers to non-manager employees
    cursor.execute(f"SELECT id FROM employees WHERE position_id NOT IN ({','.join('?' * len(manager_positions))})", manager_positions)
    non_manager_ids = [row[0] for row in cursor.fetchall()]

    for emp_id in non_manager_ids:
        if manager_ids and random.random() < 0.8:  # 80% have managers
            manager_id = random.choice(manager_ids)
            cursor.execute("UPDATE employees SET manager_id = ? WHERE id = ?", (manager_id, emp_id))

def insert_projects(cursor):
    """Insert project data."""
    project_data = []
    for name, desc, dept_name in PROJECTS:
        # Random start date in last 2 years
        start_date = datetime.now() - timedelta(days=random.randint(0, 730))
        start_date_str = start_date.strftime("%Y-%m-%d")

        # Random end date (start + 3-18 months)
        end_date = start_date + timedelta(days=random.randint(90, 540))
        end_date_str = end_date.strftime("%Y-%m-%d")

        # Random budget
        budget = random.uniform(50000, 2000000)

        project_data.append((name, desc, dept_name, start_date_str, end_date_str, budget))

    cursor.executemany('''
        INSERT INTO projects (name, description, department_name, start_date, end_date, budget)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', project_data)

def insert_employee_projects(cursor):
    """Insert employee-project assignments."""
    # Get all employees and projects
    cursor.execute("SELECT id FROM employees")
    employee_ids = [row[0] for row in cursor.fetchall()]

    cursor.execute("SELECT id FROM projects")
    project_ids = [row[0] for row in cursor.fetchall()]

    assignments = []

    # Assign each employee to 1-3 random projects
    for emp_id in employee_ids:
        num_projects = random.randint(1, 3)
        assigned_projects = random.sample(project_ids, num_projects)

        for proj_id in assigned_projects:
            # Random start date for assignment
            start_date = datetime.now() - timedelta(days=random.randint(0, 365))
            start_date_str = start_date.strftime("%Y-%m-%d")

            # Random end date or NULL (ongoing)
            if random.random() < 0.7:  # 70% chance of ongoing
                end_date_str = None
            else:
                end_date = start_date + timedelta(days=random.randint(30, 365))
                end_date_str = end_date.strftime("%Y-%m-%d")

            # Random allocation percentage
            allocation = random.choice([25.0, 50.0, 75.0, 100.0])

            # Random role
            role = random.choice(["Developer", "Lead Developer", "Architect", "Project Manager", "Business Analyst", "QA Engineer", "DevOps Engineer"])

            assignments.append((emp_id, proj_id, role, start_date_str, end_date_str, allocation))

    cursor.executemany('''
        INSERT INTO employee_projects (employee_id, project_id, role, start_date, end_date, allocation_percentage)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', assignments)

def test_database():
    """Run some test queries to verify the database."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    print("\n=== Database Test Results ===")

    # Count records in each table
    tables = ["departments", "positions", "employees", "projects", "employee_projects"]
    for table in tables:
        cursor.execute(f"SELECT COUNT(*) FROM {table}")
        count = cursor.fetchone()[0]
        print(f"{table}: {count} records")

    # Sample queries
    print("\n=== Sample Queries ===")

    # Top 5 departments by employee count
    cursor.execute("""
        SELECT d.name, COUNT(e.id) as employee_count
        FROM departments d
        LEFT JOIN employees e ON d.id = e.department_id
        GROUP BY d.id, d.name
        ORDER BY employee_count DESC
        LIMIT 5
    """)
    print("\nTop 5 departments by employee count:")
    for row in cursor.fetchall():
        print(f"  {row[0]}: {row[1]} employees")

    # Average salary by department
    cursor.execute("""
        SELECT d.name, ROUND(AVG(e.salary), 2) as avg_salary
        FROM departments d
        JOIN employees e ON d.id = e.department_id
        GROUP BY d.id, d.name
        ORDER BY avg_salary DESC
        LIMIT 5
    """)
    print("\nTop 5 departments by average salary:")
    for row in cursor.fetchall():
        print(f"  {row[0]}: ${row[1]:,.2f}")

    # Active projects count
    cursor.execute("SELECT COUNT(*) FROM projects WHERE status = 'Active'")
    active_projects = cursor.fetchone()[0]
    print(f"\nActive projects: {active_projects}")

    conn.close()

if __name__ == "__main__":
    create_database()
    test_database()
