#!/usr/bin/env python3
"""
Create a comprehensive mock SQLite database for SoftwareOne projects.
This script creates a detailed project management database with multiple related tables.
"""

import sqlite3
import random
from datetime import datetime, timedelta
import os

# Database path
DB_PATH = "database/softwareone_projects.db"

# Sample data
PROJECTS = [
    ("Cloud Migration AWS", "Large-scale migration of legacy systems to AWS cloud infrastructure", "Cloud Solutions", "In Progress", 1850000),
    ("Digital Workplace Transformation", "Implementing Microsoft 365 and collaboration tools across enterprise", "Digital Transformation", "In Progress", 950000),
    ("Cybersecurity Assessment & Remediation", "Comprehensive security audit and implementation of zero-trust model", "Cybersecurity", "Planning", 750000),
    ("Data Lake Modernization", "Building enterprise data lake on Azure with real-time analytics", "Data Analytics", "In Progress", 1450000),
    ("SAP S/4HANA Implementation", "ERP modernization project for manufacturing client", "IT Services", "In Progress", 2200000),
    ("Mobile Application Suite", "Cross-platform mobile applications for healthcare client", "Software Development", "Development", 680000),
    ("AI-Powered Chatbot Platform", "Conversational AI for customer service automation", "Data Analytics", "Testing", 420000),
    ("DevOps Pipeline Automation", "Infrastructure as Code and CI/CD implementation", "Cloud Solutions", "Completed", 380000),
    ("GDPR Compliance Program", "Data privacy and compliance implementation for EU clients", "Cybersecurity", "In Progress", 890000),
    ("Executive Dashboard BI", "Real-time business intelligence reporting platform", "Data Analytics", "Development", 295000),
    ("Microservices Architecture", "Application modernization from monolith to microservices", "Software Development", "Planning", 1200000),
    ("IoT Data Platform", "Internet of Things data collection and analytics platform", "Data Analytics", "In Progress", 1650000),
    ("API Gateway Implementation", "Centralized API management and security layer", "IT Services", "Testing", 340000),
    ("Machine Learning Operations", "ML model development and deployment platform", "Data Analytics", "Planning", 980000),
    ("Legacy System Decommissioning", "Safe retirement of outdated systems and data migration", "IT Services", "In Progress", 560000)
]

PROJECT_PHASES = [
    ("Planning", "Project planning and requirements gathering"),
    ("Design", "Architecture and technical design"),
    ("Development", "Implementation and coding"),
    ("Testing", "Quality assurance and testing"),
    ("Deployment", "Production deployment and rollout"),
    ("Support", "Post-deployment support and maintenance")
]

TECHNOLOGIES = [
    # Cloud Platforms
    ("AWS", "Amazon Web Services", "Cloud Platform"),
    ("Azure", "Microsoft Azure", "Cloud Platform"),
    ("GCP", "Google Cloud Platform", "Cloud Platform"),

    # Programming Languages
    ("Python", "Python programming language", "Programming Language"),
    ("Java", "Java programming language", "Programming Language"),
    ("JavaScript", "JavaScript programming language", "Programming Language"),
    ("C#", ".NET C# programming language", "Programming Language"),
    ("Go", "Go programming language", "Programming Language"),

    # Frameworks
    ("React", "React JavaScript framework", "Frontend Framework"),
    ("Angular", "Angular JavaScript framework", "Frontend Framework"),
    ("Spring Boot", "Spring Boot Java framework", "Backend Framework"),
    ("Django", "Django Python framework", "Backend Framework"),
    ("FastAPI", "FastAPI Python framework", "Backend Framework"),

    # Databases
    ("PostgreSQL", "PostgreSQL database", "Database"),
    ("MongoDB", "MongoDB NoSQL database", "Database"),
    ("Redis", "Redis in-memory database", "Database"),
    ("SQL Server", "Microsoft SQL Server", "Database"),

    # DevOps Tools
    ("Docker", "Containerization platform", "DevOps"),
    ("Kubernetes", "Container orchestration", "DevOps"),
    ("Jenkins", "CI/CD automation server", "DevOps"),
    ("Terraform", "Infrastructure as Code", "DevOps"),
    ("Ansible", "Configuration management", "DevOps"),

    # AI/ML
    ("TensorFlow", "Machine learning framework", "AI/ML"),
    ("PyTorch", "Deep learning framework", "AI/ML"),
    ("Scikit-learn", "Machine learning library", "AI/ML"),
    ("OpenAI GPT", "Large language model API", "AI/ML"),

    # Monitoring
    ("Prometheus", "Monitoring and alerting", "Monitoring"),
    ("Grafana", "Visualization platform", "Monitoring"),
    ("ELK Stack", "Elasticsearch, Logstash, Kibana", "Monitoring"),

    # Security
    ("OAuth 2.0", "Authorization framework", "Security"),
    ("JWT", "JSON Web Tokens", "Security"),
    ("SSL/TLS", "Secure communication", "Security")
]

STAKEHOLDER_TYPES = ["Client Executive", "Client IT Manager", "Client Business Analyst", "Project Sponsor", "Technical Lead", "Business Analyst"]

RISK_LEVELS = ["Low", "Medium", "High", "Critical"]
RISK_STATUSES = ["Open", "Mitigated", "Closed", "Monitoring"]

CLIENTS = [
    ("TechCorp Solutions", "Global technology consulting firm"),
    ("MediHealth Systems", "Healthcare technology provider"),
    ("FinanceFirst Bank", "International banking institution"),
    ("AutoMotive Inc", "Automotive manufacturing company"),
    ("RetailMax", "Large retail chain"),
    ("EnergyPlus", "Energy sector company"),
    ("EduLearn University", "Educational institution"),
    ("LogiTrans", "Logistics and transportation"),
    ("PharmaInnovate", "Pharmaceutical company"),
    ("CityGov Services", "Municipal government")
]

def create_database():
    """Create the SoftwareOne projects database with all tables and data."""

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
    insert_clients(cursor)
    insert_technologies(cursor)
    insert_projects(cursor)
    insert_project_phases(cursor)
    insert_project_technologies(cursor)
    insert_project_stakeholders(cursor)
    insert_project_risks(cursor)
    insert_project_financials(cursor)
    insert_project_resources(cursor)

    conn.commit()
    conn.close()

    print(f"Mock projects database created successfully at {DB_PATH}")
    print(f"Database contains:")
    print("- Clients: 10")
    print("- Technologies: 30+")
    print("- Projects: 15")
    print("- Project phases: 90+")
    print("- Project technologies: 200+")
    print("- Stakeholders: 150+")
    print("- Risks: 100+")
    print("- Financial records: 225+")
    print("- Resource allocations: 300+")

def create_tables(cursor):
    """Create all database tables."""

    # Clients table
    cursor.execute('''
        CREATE TABLE clients (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE,
            description TEXT,
            industry TEXT,
            contact_email TEXT,
            contact_phone TEXT,
            address TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    # Technologies table
    cursor.execute('''
        CREATE TABLE technologies (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE,
            description TEXT,
            category TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    # Projects table
    cursor.execute('''
        CREATE TABLE projects (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            project_code TEXT NOT NULL UNIQUE,
            name TEXT NOT NULL,
            description TEXT,
            client_id INTEGER,
            department TEXT,
            status TEXT DEFAULT 'Planning',
            priority TEXT DEFAULT 'Medium',
            budget REAL,
            start_date DATE,
            planned_end_date DATE,
            actual_end_date DATE,
            project_manager TEXT,
            technical_lead TEXT,
            progress_percentage REAL DEFAULT 0.0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (client_id) REFERENCES clients (id)
        )
    ''')

    # Project phases table
    cursor.execute('''
        CREATE TABLE project_phases (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            project_id INTEGER NOT NULL,
            phase_name TEXT NOT NULL,
            description TEXT,
            planned_start_date DATE,
            planned_end_date DATE,
            actual_start_date DATE,
            actual_end_date DATE,
            status TEXT DEFAULT 'Not Started',
            progress_percentage REAL DEFAULT 0.0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (project_id) REFERENCES projects (id)
        )
    ''')

    # Project technologies junction table
    cursor.execute('''
        CREATE TABLE project_technologies (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            project_id INTEGER NOT NULL,
            technology_id INTEGER NOT NULL,
            usage_description TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (project_id) REFERENCES projects (id),
            FOREIGN KEY (technology_id) REFERENCES technologies (id),
            UNIQUE(project_id, technology_id)
        )
    ''')

    # Project stakeholders table
    cursor.execute('''
        CREATE TABLE project_stakeholders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            project_id INTEGER NOT NULL,
            name TEXT NOT NULL,
            role TEXT,
            organization TEXT,
            email TEXT,
            phone TEXT,
            influence_level TEXT DEFAULT 'Medium',
            interest_level TEXT DEFAULT 'Medium',
            communication_frequency TEXT DEFAULT 'Weekly',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (project_id) REFERENCES projects (id)
        )
    ''')

    # Project risks table
    cursor.execute('''
        CREATE TABLE project_risks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            project_id INTEGER NOT NULL,
            risk_description TEXT NOT NULL,
            risk_category TEXT,
            probability TEXT,
            impact TEXT,
            risk_level TEXT,
            mitigation_plan TEXT,
            owner TEXT,
            status TEXT DEFAULT 'Open',
            identified_date DATE,
            closed_date DATE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (project_id) REFERENCES projects (id)
        )
    ''')

    # Project financials table
    cursor.execute('''
        CREATE TABLE project_financials (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            project_id INTEGER NOT NULL,
            month_year TEXT NOT NULL,
            budgeted_amount REAL,
            actual_amount REAL,
            forecast_amount REAL,
            variance_amount REAL,
            variance_percentage REAL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (project_id) REFERENCES projects (id),
            UNIQUE(project_id, month_year)
        )
    ''')

    # Project resources table
    cursor.execute('''
        CREATE TABLE project_resources (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            project_id INTEGER NOT NULL,
            resource_type TEXT NOT NULL,
            resource_name TEXT NOT NULL,
            allocation_percentage REAL DEFAULT 100.0,
            start_date DATE,
            end_date DATE,
            hourly_rate REAL,
            total_hours REAL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (project_id) REFERENCES projects (id)
        )
    ''')

def insert_clients(cursor):
    """Insert client data."""
    client_data = []
    industries = ["Technology", "Healthcare", "Financial Services", "Manufacturing", "Retail", "Energy", "Education", "Logistics", "Pharmaceutical", "Government"]

    for i, (name, desc) in enumerate(CLIENTS):
        industry = industries[i % len(industries)]
        email = f"contact@{name.lower().replace(' ', '')}.com"
        phone = ""
        address = f"123 Business St, {['New York', 'London', 'Singapore', 'Zurich', 'Sydney'][i % 5]}"

        client_data.append((name, desc, industry, email, phone, address))

    cursor.executemany('''
        INSERT INTO clients (name, description, industry, contact_email, contact_phone, address)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', client_data)

def insert_technologies(cursor):
    """Insert technology data."""
    cursor.executemany(
        "INSERT INTO technologies (name, description, category) VALUES (?, ?, ?)",
        [(tech[0], tech[1], tech[2]) for tech in TECHNOLOGIES]
    )

def insert_projects(cursor):
    """Insert project data."""
    # Get client IDs
    cursor.execute("SELECT id FROM clients")
    client_ids = [row[0] for row in cursor.fetchall()]

    project_data = []

    for i, (name, desc, dept, status, budget) in enumerate(PROJECTS):
        project_code = f"PROJ-{2024 + (i // 3):02d}-{i+1:03d}"
        client_id = random.choice(client_ids)

        # Random dates
        start_date = datetime.now() - timedelta(days=random.randint(0, 365))
        start_date_str = start_date.strftime("%Y-%m-%d")

        # Planned end date (3-18 months from start)
        planned_end = start_date + timedelta(days=random.randint(90, 540))
        planned_end_str = planned_end.strftime("%Y-%m-%d")

        # Actual end date (only for completed projects)
        actual_end_str = None
        if status == "Completed":
            actual_end = planned_end + timedelta(days=random.randint(-30, 30))
            actual_end_str = actual_end.strftime("%Y-%m-%d")

        # Project manager and technical lead
        managers = ["Sarah Johnson", "Michael Chen", "David Rodriguez", "Emma Wilson", "James Brown", "Lisa Davis", "Robert Miller", "Jennifer Garcia"]
        project_manager = random.choice(managers)
        technical_lead = random.choice([m for m in managers if m != project_manager])

        # Progress percentage
        if status == "Completed":
            progress = 100.0
        elif status == "Planning":
            progress = random.uniform(5, 15)
        elif status == "Development" or "Testing":
            progress = random.uniform(30, 80)
        else:
            progress = random.uniform(15, 90)

        priority = random.choice(["Low", "Medium", "High", "Critical"])

        project_data.append((
            project_code, name, desc, client_id, dept, status, priority, budget,
            start_date_str, planned_end_str, actual_end_str, project_manager,
            technical_lead, progress
        ))

    cursor.executemany('''
        INSERT INTO projects (project_code, name, description, client_id, department, status,
                            priority, budget, start_date, planned_end_date, actual_end_date,
                            project_manager, technical_lead, progress_percentage)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', project_data)

def insert_project_phases(cursor):
    """Insert project phases for each project."""
    # Get project IDs
    cursor.execute("SELECT id FROM projects")
    project_ids = [row[0] for row in cursor.fetchall()]

    phase_data = []

    for project_id in project_ids:
        # Get project start date
        cursor.execute("SELECT start_date, status FROM projects WHERE id = ?", (project_id,))
        start_date_str, status = cursor.fetchone()
        start_date = datetime.strptime(start_date_str, "%Y-%m-%d")

        # Create phases for each project
        for i, (phase_name, description) in enumerate(PROJECT_PHASES):
            # Phase dates (each phase ~1-3 months)
            phase_start = start_date + timedelta(days=i * random.randint(30, 90))
            phase_end = phase_start + timedelta(days=random.randint(30, 90))

            planned_start_str = phase_start.strftime("%Y-%m-%d")
            planned_end_str = phase_end.strftime("%Y-%m-%d")

            # Determine status based on project status and phase position
            if status == "Completed":
                phase_status = "Completed"
                actual_start_str = planned_start_str
                actual_end_str = planned_end_str
                progress = 100.0
            elif status == "Planning" and i == 0:
                phase_status = "In Progress"
                actual_start_str = planned_start_str
                actual_end_str = None
                progress = random.uniform(20, 60)
            elif status in ["Development", "Testing"] and i <= 2:
                phase_status = "In Progress" if i == 2 else "Completed"
                actual_start_str = planned_start_str
                actual_end_str = None if phase_status == "In Progress" else planned_end_str
                progress = random.uniform(50, 90) if phase_status == "In Progress" else 100.0
            else:
                phase_status = "Not Started"
                actual_start_str = None
                actual_end_str = None
                progress = 0.0

            phase_data.append((
                project_id, phase_name, description, planned_start_str, planned_end_str,
                actual_start_str, actual_end_str, phase_status, progress
            ))

    cursor.executemany('''
        INSERT INTO project_phases (project_id, phase_name, description, planned_start_date,
                                  planned_end_date, actual_start_date, actual_end_date, status, progress_percentage)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', phase_data)

def insert_project_technologies(cursor):
    """Insert project-technology relationships."""
    # Get project and technology IDs
    cursor.execute("SELECT id FROM projects")
    project_ids = [row[0] for row in cursor.fetchall()]

    cursor.execute("SELECT id, category FROM technologies")
    tech_data = cursor.fetchall()

    tech_assignments = []

    for project_id in project_ids:
        # Assign 3-8 random technologies per project
        num_tech = random.randint(3, 8)
        selected_tech = random.sample(tech_data, num_tech)

        for tech_id, category in selected_tech:
            usage_desc = f"Used for {category.lower()} implementation"
            tech_assignments.append((project_id, tech_id, usage_desc))

    cursor.executemany('''
        INSERT INTO project_technologies (project_id, technology_id, usage_description)
        VALUES (?, ?, ?)
    ''', tech_assignments)

def insert_project_stakeholders(cursor):
    """Insert project stakeholders."""
    # Get project IDs
    cursor.execute("SELECT id, client_id FROM projects")
    project_data = cursor.fetchall()

    stakeholder_data = []
    stakeholder_names = [
        "John Smith", "Maria Garcia", "David Kim", "Sarah Wilson", "Robert Chen",
        "Lisa Anderson", "Michael Brown", "Emma Davis", "James Miller", "Jennifer Lee",
        "Christopher Taylor", "Amanda Johnson", "Daniel Rodriguez", "Jessica Martinez", "Matthew Thompson"
    ]

    # Create more names to avoid running out
    additional_names = [
        "Olivia White", "William Harris", "Sophia Clark", "Benjamin Lewis", "Isabella Robinson",
        "Alexander Walker", "Charlotte Young", "Ethan King", "Amelia Scott", "Mason Green",
        "Harper Adams", "Elijah Baker", "Ava Nelson", "Logan Carter", "Mia Mitchell",
        "Lucas Perez", "Ella Roberts", "Jackson Turner", "Scarlett Phillips", "Aiden Campbell"
    ]
    all_names = stakeholder_names + additional_names

    for project_id, client_id in project_data:
        # Get client name
        cursor.execute("SELECT name FROM clients WHERE id = ?", (client_id,))
        client_name = cursor.fetchone()[0]

        # Create 3-6 stakeholders per project
        num_stakeholders = random.randint(3, 6)

        for i in range(num_stakeholders):
            name = random.choice(all_names)

            role = random.choice(STAKEHOLDER_TYPES)
            organization = client_name if "Client" in role else "SoftwareOne"
            email = f"{name.lower().replace(' ', '.')}@{organization.lower().replace(' ', '')}.com"
            phone = ""

            influence = random.choice(["Low", "Medium", "High"])
            interest = random.choice(["Low", "Medium", "High"])
            frequency = random.choice(["Daily", "Weekly", "Bi-weekly", "Monthly"])

            stakeholder_data.append((
                project_id, name, role, organization, email, phone,
                influence, interest, frequency
            ))

    cursor.executemany('''
        INSERT INTO project_stakeholders (project_id, name, role, organization, email, phone,
                                        influence_level, interest_level, communication_frequency)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', stakeholder_data)

def insert_project_risks(cursor):
    """Insert project risks."""
    # Get project IDs
    cursor.execute("SELECT id FROM projects")
    project_ids = [row[0] for row in cursor.fetchall()]

    risk_descriptions = [
        "Technology complexity may cause delays",
        "Key team member availability",
        "Client requirement changes",
        "Third-party vendor dependencies",
        "Security compliance requirements",
        "Data migration challenges",
        "Integration with existing systems",
        "Budget constraints",
        "Resource allocation conflicts",
        "Technical skill gaps",
        "Scope creep potential",
        "Regulatory compliance changes",
        "Infrastructure limitations",
        "Testing environment availability",
        "Knowledge transfer issues"
    ]

    risk_categories = ["Technical", "Resource", "Schedule", "Budget", "Scope", "Compliance", "External"]

    risk_data = []

    for project_id in project_ids:
        # Create 2-5 risks per project
        num_risks = random.randint(2, 5)

        for _ in range(num_risks):
            description = random.choice(risk_descriptions)
            category = random.choice(risk_categories)
            probability = random.choice(["Low", "Medium", "High"])
            impact = random.choice(["Low", "Medium", "High"])

            # Calculate risk level
            prob_score = {"Low": 1, "Medium": 2, "High": 3}[probability]
            impact_score = {"Low": 1, "Medium": 2, "High": 3}[impact]
            total_score = prob_score * impact_score

            if total_score <= 2:
                risk_level = "Low"
            elif total_score <= 6:
                risk_level = "Medium"
            else:
                risk_level = "High"

            mitigation = f"Develop contingency plan and regular monitoring for {description.lower()}"
            owner = random.choice(["Project Manager", "Technical Lead", "Team Lead", "Risk Manager"])
            status = random.choice(RISK_STATUSES)

            # Risk identification date
            identified_date = datetime.now() - timedelta(days=random.randint(0, 180))
            identified_date_str = identified_date.strftime("%Y-%m-%d")

            closed_date_str = None
            if status == "Closed":
                closed_date = identified_date + timedelta(days=random.randint(30, 120))
                closed_date_str = closed_date.strftime("%Y-%m-%d")

            risk_data.append((
                project_id, description, category, probability, impact, risk_level,
                mitigation, owner, status, identified_date_str, closed_date_str
            ))

    cursor.executemany('''
        INSERT INTO project_risks (project_id, risk_description, risk_category, probability, impact,
                                 risk_level, mitigation_plan, owner, status, identified_date, closed_date)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', risk_data)

def insert_project_financials(cursor):
    """Insert project financial tracking data."""
    # Get project IDs and their budgets
    cursor.execute("SELECT id, budget, start_date FROM projects")
    project_data = cursor.fetchall()

    financial_data = []

    for project_id, budget, start_date_str in project_data:
        start_date = datetime.strptime(start_date_str, "%Y-%m-%d")

        # Create 3-9 months of financial data
        num_months = random.randint(3, 9)
        months_added = set()

        for i in range(num_months):
            month_date = start_date + timedelta(days=i * 30)
            month_year = month_date.strftime("%Y-%m")

            # Ensure unique month_year for this project
            if month_year in months_added:
                continue
            months_added.add(month_year)

            # Budgeted amount (monthly portion of total budget)
            budgeted = budget / num_months

            # Actual amount (with some variance)
            variance_factor = random.uniform(0.8, 1.2)
            actual = budgeted * variance_factor

            # Forecast (for future months)
            if i >= num_months - 2:
                forecast = budgeted * random.uniform(0.9, 1.1)
            else:
                forecast = actual

            # Calculate variance
            variance_amount = actual - budgeted
            variance_percentage = (variance_amount / budgeted) * 100 if budgeted > 0 else 0

            financial_data.append((
                project_id, month_year, budgeted, actual, forecast, variance_amount, variance_percentage
            ))

    cursor.executemany('''
        INSERT INTO project_financials (project_id, month_year, budgeted_amount, actual_amount,
                                      forecast_amount, variance_amount, variance_percentage)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', financial_data)

def insert_project_resources(cursor):
    """Insert project resource allocations."""
    # Get project IDs
    cursor.execute("SELECT id, start_date FROM projects")
    project_data = cursor.fetchall()

    resource_types = ["Developer", "Business Analyst", "Project Manager", "QA Engineer", "DevOps Engineer", "Architect", "Designer"]
    resource_names = [
        "Alice Johnson", "Bob Smith", "Carol Williams", "David Brown", "Eva Davis",
        "Frank Miller", "Grace Wilson", "Henry Moore", "Ivy Taylor", "Jack Anderson",
        "Kate Thomas", "Liam Jackson", "Maya White", "Nathan Harris", "Olivia Martin"
    ]

    resource_data = []

    for project_id, start_date_str in project_data:
        start_date = datetime.strptime(start_date_str, "%Y-%m-%d")

        # Assign 3-8 resources per project
        num_resources = random.randint(3, 8)

        for _ in range(num_resources):
            resource_type = random.choice(resource_types)
            resource_name = random.choice(resource_names)

            allocation = random.choice([25.0, 50.0, 75.0, 100.0])

            # Resource dates
            resource_start = start_date + timedelta(days=random.randint(0, 30))
            resource_end = resource_start + timedelta(days=random.randint(60, 365))

            start_date_str = resource_start.strftime("%Y-%m-%d")
            end_date_str = resource_end.strftime("%Y-%m-%d")

            # Hourly rate based on resource type
            rate_ranges = {
                "Developer": (80, 150),
                "Business Analyst": (70, 120),
                "Project Manager": (90, 160),
                "QA Engineer": (65, 110),
                "DevOps Engineer": (85, 145),
                "Architect": (100, 180),
                "Designer": (60, 100)
            }
            min_rate, max_rate = rate_ranges[resource_type]
            hourly_rate = random.uniform(min_rate, max_rate)

            # Total hours (based on allocation and duration)
            weeks = (resource_end - resource_start).days / 7
            weekly_hours = 40 * (allocation / 100)
            total_hours = weeks * weekly_hours

            resource_data.append((
                project_id, resource_type, resource_name, allocation,
                start_date_str, end_date_str, hourly_rate, total_hours
            ))

    cursor.executemany('''
        INSERT INTO project_resources (project_id, resource_type, resource_name, allocation_percentage,
                                     start_date, end_date, hourly_rate, total_hours)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    ''', resource_data)

def test_database():
    """Run some test queries to verify the database."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    print("\n=== Project Database Test Results ===")

    # Count records in each table
    tables = ["clients", "technologies", "projects", "project_phases", "project_technologies",
              "project_stakeholders", "project_risks", "project_financials", "project_resources"]
    for table in tables:
        cursor.execute(f"SELECT COUNT(*) FROM {table}")
        count = cursor.fetchone()[0]
        print(f"{table}: {count} records")

    # Sample queries
    print("\n=== Sample Project Queries ===")

    # Top projects by budget
    cursor.execute("""
        SELECT p.name, c.name as client, p.budget, p.status
        FROM projects p
        JOIN clients c ON p.client_id = c.id
        ORDER BY p.budget DESC
        LIMIT 3
    """)
    print("\nTop 3 projects by budget:")
    for row in cursor.fetchall():
        print(f"  {row[0]} - {row[1]}: ${row[2]:,.0f} ({row[3]})")

    # Projects by status
    cursor.execute("""
        SELECT status, COUNT(*) as count, ROUND(AVG(budget), 0) as avg_budget
        FROM projects
        GROUP BY status
        ORDER BY count DESC
    """)
    print("\nProjects by status:")
    for row in cursor.fetchall():
        print(f"  {row[0]}: {row[1]} projects, avg budget: ${row[2]:,.0f}")

    # High-risk projects
    cursor.execute("""
        SELECT p.name, COUNT(r.id) as risk_count
        FROM projects p
        LEFT JOIN project_risks r ON p.id = r.project_id AND r.risk_level IN ('High', 'Critical')
        GROUP BY p.id, p.name
        HAVING risk_count > 0
        ORDER BY risk_count DESC
        LIMIT 3
    """)
    print("\nProjects with most high/critical risks:")
    for row in cursor.fetchall():
        print(f"  {row[0]}: {row[1]} high/critical risks")

    # Technology usage
    cursor.execute("""
        SELECT t.name, COUNT(pt.id) as usage_count
        FROM technologies t
        JOIN project_technologies pt ON t.id = pt.technology_id
        GROUP BY t.id, t.name
        ORDER BY usage_count DESC
        LIMIT 5
    """)
    print("\nMost used technologies:")
    for row in cursor.fetchall():
        print(f"  {row[0]}: used in {row[1]} projects")

    conn.close()

if __name__ == "__main__":
    create_database()
    test_database()
