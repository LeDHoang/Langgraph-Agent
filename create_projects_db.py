#!/usr/bin/env python3
"""
Create a comprehensive mock SQLite database for SoftwareOne projects.
This script creates a realistic project management database for a technology consulting company.
"""

import sqlite3
import random
from datetime import datetime, timedelta
import os

# Database path
DB_PATH = "database/softwareone_projects.db"

# Sample data
CLIENTS = [
    ("Global Bank Corp", "Banking", "New York", "USA", "Fortune 500 bank", "Enterprise"),
    ("TechFlow Solutions", "Technology", "San Francisco", "USA", "SaaS company", "Mid-Market"),
    ("MediCare Plus", "Healthcare", "Zurich", "Switzerland", "Healthcare provider", "Enterprise"),
    ("RetailMax", "Retail", "London", "UK", "International retailer", "Enterprise"),
    ("AutoTech Industries", "Manufacturing", "Munich", "Germany", "Automotive supplier", "Large"),
    ("EduLearn Global", "Education", "Singapore", "Singapore", "Online education platform", "Mid-Market"),
    ("GreenEnergy Corp", "Energy", "Oslo", "Norway", "Renewable energy company", "Enterprise"),
    ("LogiChain", "Logistics", "Rotterdam", "Netherlands", "Supply chain management", "Large"),
    ("InsureTech Solutions", "Insurance", "Sydney", "Australia", "Insurance technology", "Mid-Market"),
    ("FoodCorp International", "Food & Beverage", "Toronto", "Canada", "Food manufacturing", "Large"),
    ("PharmaInnovate", "Pharmaceuticals", "Basel", "Switzerland", "Pharmaceutical research", "Enterprise"),
    ("TeleCom Plus", "Telecommunications", "Paris", "France", "Telecom services", "Enterprise"),
    ("FinanceFlow", "Financial Services", "Hong Kong", "China", "Financial technology", "Mid-Market"),
    ("SmartCity Solutions", "Government", "Vienna", "Austria", "Smart city initiatives", "Enterprise"),
    ("TravelHub", "Travel & Hospitality", "Amsterdam", "Netherlands", "Travel booking platform", "Large")
]

PROJECT_TYPES = [
    "Cloud Migration", "Digital Transformation", "ERP Implementation", "Cybersecurity Assessment",
    "Data Analytics Platform", "Mobile App Development", "AI/ML Implementation", "Infrastructure Modernization",
    "DevOps Transformation", "Legacy System Modernization", "API Integration", "Business Intelligence",
    "IoT Platform", "Microservices Architecture", "Blockchain Implementation"
]

TECHNOLOGIES = [
    ("AWS", "Amazon Web Services", "Cloud Platform"),
    ("Azure", "Microsoft Azure", "Cloud Platform"),
    ("GCP", "Google Cloud Platform", "Cloud Platform"),
    ("Docker", "Container Platform", "DevOps"),
    ("Kubernetes", "Container Orchestration", "DevOps"),
    ("Terraform", "Infrastructure as Code", "DevOps"),
    ("Jenkins", "CI/CD Pipeline", "DevOps"),
    ("GitLab CI", "CI/CD Pipeline", "DevOps"),
    ("Python", "Programming Language", "Development"),
    ("Java", "Programming Language", "Development"),
    ("JavaScript", "Programming Language", "Development"),
    (".NET", "Framework", "Development"),
    ("React", "Frontend Framework", "Development"),
    ("Angular", "Frontend Framework", "Development"),
    ("Node.js", "Runtime Environment", "Development"),
    ("SAP S/4HANA", "ERP System", "Enterprise Software"),
    ("Oracle Cloud", "ERP System", "Enterprise Software"),
    ("Microsoft Dynamics", "ERP System", "Enterprise Software"),
    ("Salesforce", "CRM Platform", "Enterprise Software"),
    ("Tableau", "Business Intelligence", "Analytics"),
    ("Power BI", "Business Intelligence", "Analytics"),
    ("Snowflake", "Data Warehouse", "Analytics"),
    ("Databricks", "Data Analytics", "Analytics"),
    ("TensorFlow", "Machine Learning", "AI/ML"),
    ("PyTorch", "Machine Learning", "AI/ML"),
    ("OpenAI GPT", "AI Language Models", "AI/ML"),
    ("MongoDB", "NoSQL Database", "Database"),
    ("PostgreSQL", "Relational Database", "Database"),
    ("Redis", "In-Memory Database", "Database"),
    ("Elasticsearch", "Search Engine", "Database")
]

PROJECT_PHASES = [
    ("Discovery", "Project initiation and requirements gathering", 1),
    ("Planning", "Detailed planning and resource allocation", 2),
    ("Design", "Architecture and solution design", 3),
    ("Development", "Implementation and coding", 4),
    ("Testing", "Quality assurance and testing", 5),
    ("Deployment", "Production deployment and go-live", 6),
    ("Support", "Post-deployment support and optimization", 7)
]

PROJECT_STATUSES = [
    ("Planning", "Project is in planning phase"),
    ("Active", "Project is currently in progress"),
    ("On Hold", "Project temporarily suspended"),
    ("Completed", "Project successfully completed"),
    ("Cancelled", "Project cancelled"),
    ("Delayed", "Project delayed due to issues")
]

RISK_LEVELS = ["Low", "Medium", "High", "Critical"]

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
    insert_project_teams(cursor)
    insert_project_milestones(cursor)
    insert_project_budgets(cursor)
    insert_project_risks(cursor)
    insert_project_status_updates(cursor)
    insert_project_technologies(cursor)

    conn.commit()
    conn.close()

    print(f"Mock projects database created successfully at {DB_PATH}")
    print(f"Database contains:")
    print("- Clients: 15")
    print("- Technologies: 30")
    print("- Projects: 25")
    print("- Project phases: ~100")
    print("- Project teams: ~200")
    print("- Project milestones: ~150")
    print("- Project budgets: ~75")
    print("- Project risks: ~50")
    print("- Status updates: ~200")
    print("- Technology assignments: ~150")

def create_tables(cursor):
    """Create all database tables."""

    # Clients table
    cursor.execute('''
        CREATE TABLE clients (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE,
            industry TEXT NOT NULL,
            city TEXT,
            country TEXT,
            description TEXT,
            size_category TEXT,
            contact_email TEXT,
            contact_phone TEXT,
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
            project_type TEXT,
            client_id INTEGER NOT NULL,
            status TEXT DEFAULT 'Planning',
            priority TEXT DEFAULT 'Medium',
            start_date DATE,
            planned_end_date DATE,
            actual_end_date DATE,
            budget DECIMAL(12,2),
            currency TEXT DEFAULT 'USD',
            project_manager TEXT,
            technical_lead TEXT,
            delivery_manager TEXT,
            contract_type TEXT,
            sla_requirements TEXT,
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
            phase_order INTEGER,
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

    # Project teams table
    cursor.execute('''
        CREATE TABLE project_teams (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            project_id INTEGER NOT NULL,
            employee_id TEXT NOT NULL,
            employee_name TEXT,
            role TEXT NOT NULL,
            allocation_percentage REAL DEFAULT 100.0,
            start_date DATE,
            end_date DATE,
            hourly_rate DECIMAL(8,2),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (project_id) REFERENCES projects (id)
        )
    ''')

    # Project milestones table
    cursor.execute('''
        CREATE TABLE project_milestones (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            project_id INTEGER NOT NULL,
            milestone_name TEXT NOT NULL,
            description TEXT,
            planned_date DATE,
            actual_date DATE,
            status TEXT DEFAULT 'Pending',
            category TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (project_id) REFERENCES projects (id)
        )
    ''')

    # Project budgets table
    cursor.execute('''
        CREATE TABLE project_budgets (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            project_id INTEGER NOT NULL,
            category TEXT NOT NULL,
            subcategory TEXT,
            planned_amount DECIMAL(10,2),
            actual_amount DECIMAL(10,2),
            currency TEXT DEFAULT 'USD',
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
            impact TEXT,
            probability TEXT,
            risk_level TEXT,
            mitigation_plan TEXT,
            status TEXT DEFAULT 'Open',
            owner TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (project_id) REFERENCES projects (id)
        )
    ''')

    # Project status updates table
    cursor.execute('''
        CREATE TABLE project_status_updates (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            project_id INTEGER NOT NULL,
            update_date DATE NOT NULL,
            overall_progress REAL,
            phase_status TEXT,
            issues TEXT,
            next_steps TEXT,
            updated_by TEXT,
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
            primary_use TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (project_id) REFERENCES projects (id),
            FOREIGN KEY (technology_id) REFERENCES technologies (id),
            UNIQUE(project_id, technology_id)
        )
    ''')

def insert_clients(cursor):
    """Insert client data."""
    client_data = []
    for name, industry, city, country, desc, size in CLIENTS:
        email = f"contact@{name.lower().replace(' ', '')}.com"
        phone = "+1-555-" + "".join([str(random.randint(0,9)) for _ in range(7)])
        client_data.append((name, industry, city, country, desc, size, email, phone))

    cursor.executemany('''
        INSERT INTO clients (name, industry, country, city, description, size_category, contact_email, contact_phone)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    ''', client_data)

def insert_technologies(cursor):
    """Insert technology data."""
    cursor.executemany(
        "INSERT INTO technologies (name, description, category) VALUES (?, ?, ?)",
        TECHNOLOGIES
    )

def insert_projects(cursor):
    """Insert project data."""
    projects_data = []

    # Get client IDs
    cursor.execute("SELECT id FROM clients")
    client_ids = [row[0] for row in cursor.fetchall()]

    # Create 25 projects
    for i in range(1, 26):
        project_code = "05d"
        name = f"{random.choice(PROJECT_TYPES)} {random.choice(['Phase 1', 'Phase 2', 'Implementation', 'Migration', 'Transformation', 'Modernization'])}"

        # Create more realistic project names
        project_names = [
            "Cloud Migration to AWS", "Digital Workplace Implementation", "ERP System Upgrade",
            "Cybersecurity Framework Deployment", "Data Lake Architecture", "Mobile Banking App",
            "AI-Powered Customer Service", "Infrastructure Automation", "Legacy Application Retirement",
            "API Gateway Implementation", "Business Intelligence Dashboard", "IoT Asset Tracking",
            "Microservices Refactoring", "Blockchain Supply Chain", "DevOps Pipeline Setup",
            "Machine Learning Platform", "Container Orchestration", "Serverless Architecture",
            "Data Warehouse Modernization", "Multi-Cloud Strategy", "Security Compliance Audit",
            "Performance Optimization", "Integration Platform", "Analytics Platform", "Digital Transformation"
        ]
        name = random.choice(project_names)

        description = f"Implementation of {name.lower()} for enterprise client"
        project_type = random.choice(PROJECT_TYPES)
        client_id = random.choice(client_ids)
        status = random.choice(PROJECT_STATUSES)[0]
        priority = random.choice(["Low", "Medium", "High", "Critical"])

        # Date calculations
        start_date = datetime.now() - timedelta(days=random.randint(0, 365))
        duration_months = random.randint(3, 24)
        planned_end_date = start_date + timedelta(days=duration_months * 30)

        if status[0] == "Completed":
            actual_end_date = planned_end_date + timedelta(days=random.randint(-30, 30))
        else:
            actual_end_date = None

        # Budget calculations
        budget = random.uniform(100000, 5000000)

        # Team roles
        pm_names = ["Sarah Johnson", "Michael Chen", "Anna Schmidt", "David Kumar", "Maria Garcia"]
        tl_names = ["Robert Lee", "Jennifer Wu", "Thomas Anderson", "Lisa Brown", "James Wilson"]
        dm_names = ["Peter Novak", "Sophie Martin", "Carlos Rodriguez", "Emma Taylor", "Ahmed Hassan"]

        project_manager = random.choice(pm_names)
        technical_lead = random.choice(tl_names)
        delivery_manager = random.choice(dm_names)

        contract_type = random.choice(["Fixed Price", "Time & Materials", "Retainer"])
        sla_requirements = "99.9% uptime, 24/7 support, monthly reporting"

        projects_data.append((
            project_code, name, description, project_type, client_id, status, priority,
            start_date.strftime("%Y-%m-%d"), planned_end_date.strftime("%Y-%m-%d"),
            actual_end_date.strftime("%Y-%m-%d") if actual_end_date else None,
            budget, "USD", project_manager, technical_lead, delivery_manager,
            contract_type, sla_requirements
        ))

    cursor.executemany('''
        INSERT INTO projects (project_code, name, description, project_type, client_id, status, priority,
                             start_date, planned_end_date, actual_end_date, budget, currency,
                             project_manager, technical_lead, delivery_manager, contract_type, sla_requirements)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', projects_data)

def insert_project_phases(cursor):
    """Insert project phases data."""
    # Get all project IDs
    cursor.execute("SELECT id FROM projects")
    project_ids = [row[0] for row in cursor.fetchall()]

    phases_data = []

    for project_id in project_ids:
        # Get project dates
        cursor.execute("SELECT start_date, planned_end_date FROM projects WHERE id = ?", (project_id,))
        start_date, end_date = cursor.fetchone()
        start_dt = datetime.strptime(start_date, "%Y-%m-%d")
        end_dt = datetime.strptime(end_date, "%Y-%m-%d")

        # Calculate phase durations
        total_days = (end_dt - start_dt).days
        phase_days = total_days // len(PROJECT_PHASES)

        for i, (phase_name, desc, order) in enumerate(PROJECT_PHASES):
            phase_start = start_dt + timedelta(days=i * phase_days)
            phase_end = start_dt + timedelta(days=(i + 1) * phase_days)

            # Random status and progress
            if random.random() < 0.3:
                status = "Completed"
                progress = 100.0
                actual_start = phase_start
                actual_end = phase_end + timedelta(days=random.randint(-5, 5))
            elif random.random() < 0.6:
                status = "In Progress"
                progress = random.uniform(20, 80)
                actual_start = phase_start
                actual_end = None
            else:
                status = "Not Started"
                progress = 0.0
                actual_start = None
                actual_end = None

            phases_data.append((
                project_id, phase_name, desc, order,
                phase_start.strftime("%Y-%m-%d"), phase_end.strftime("%Y-%m-%d"),
                actual_start.strftime("%Y-%m-%d") if actual_start else None,
                actual_end.strftime("%Y-%m-%d") if actual_end else None,
                status, progress
            ))

    cursor.executemany('''
        INSERT INTO project_phases (project_id, phase_name, description, phase_order,
                                   planned_start_date, planned_end_date, actual_start_date, actual_end_date,
                                   status, progress_percentage)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', phases_data)

def insert_project_teams(cursor):
    """Insert project team data."""
    # Get all project IDs
    cursor.execute("SELECT id FROM projects")
    project_ids = [row[0] for row in cursor.fetchall()]

    team_data = []
    roles = ["Project Manager", "Technical Lead", "Senior Developer", "Developer", "QA Engineer",
             "DevOps Engineer", "Business Analyst", "UI/UX Designer", "Database Administrator",
             "Security Specialist", "Data Engineer", "Cloud Architect"]

    employee_names = [
        "Nguyen Van A", "Tran Thi B", "Le Van C", "Pham Thi D", "Ho Van E",
        "Vu Thi F", "Vo Van G", "Dang Thi H", "Bui Van I", "Do Thi J",
        "Hoang Van K", "Phan Thi L", "Truong Van M", "Ngo Thi N", "Duong Van O"
    ]

    for project_id in project_ids:
        # Assign 3-8 team members per project
        team_size = random.randint(3, 8)
        team_members = random.sample(employee_names, team_size)

        for i, member_name in enumerate(team_members):
            role = random.choice(roles)
            allocation = random.choice([25.0, 50.0, 75.0, 100.0])

            # Random start date within project timeframe
            cursor.execute("SELECT start_date, planned_end_date FROM projects WHERE id = ?", (project_id,))
            start_date, end_date = cursor.fetchone()
            start_dt = datetime.strptime(start_date, "%Y-%m-%d")
            end_dt = datetime.strptime(end_date, "%Y-%m-%d")

            team_start = start_dt + timedelta(days=random.randint(0, 30))
            team_end = random.choice([None, end_dt + timedelta(days=random.randint(-10, 10))])

            hourly_rate = random.uniform(50, 150)

            team_data.append((
                project_id, f"EMP{random.randint(1001, 1200):04d}", member_name, role,
                allocation, team_start.strftime("%Y-%m-%d"),
                team_end.strftime("%Y-%m-%d") if team_end else None, hourly_rate
            ))

    cursor.executemany('''
        INSERT INTO project_teams (project_id, employee_id, employee_name, role, allocation_percentage,
                                  start_date, end_date, hourly_rate)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    ''', team_data)

def insert_project_milestones(cursor):
    """Insert project milestones data."""
    # Get all project IDs
    cursor.execute("SELECT id FROM projects")
    project_ids = [row[0] for row in cursor.fetchall()]

    milestones_data = []
    milestone_templates = [
        ("Kickoff Meeting", "Project kickoff and team alignment", "Planning"),
        ("Requirements Sign-off", "Client requirements approval", "Planning"),
        ("Design Review", "Architecture and design approval", "Design"),
        ("Development Complete", "Core development finished", "Development"),
        ("Testing Complete", "All testing phases finished", "Testing"),
        ("UAT Complete", "User acceptance testing finished", "Testing"),
        ("Go-Live", "Production deployment", "Deployment"),
        ("Handover", "Project handover to operations", "Support"),
        ("Post-Implementation Review", "Project retrospective", "Support")
    ]

    for project_id in project_ids:
        # Get project dates
        cursor.execute("SELECT start_date, planned_end_date FROM projects WHERE id = ?", (project_id,))
        start_date, end_date = cursor.fetchone()
        start_dt = datetime.strptime(start_date, "%Y-%m-%d")
        end_dt = datetime.strptime(end_date, "%Y-%m-%d")

        # Select 4-7 milestones per project
        num_milestones = random.randint(4, 7)
        selected_milestones = random.sample(milestone_templates, num_milestones)

        for i, (name, desc, category) in enumerate(selected_milestones):
            # Distribute milestones across project timeline
            days_from_start = int((end_dt - start_dt).days * (i + 1) / (num_milestones + 1))
            planned_date = start_dt + timedelta(days=days_from_start)

            # Random actual date (may be delayed)
            if random.random() < 0.7:
                actual_date = planned_date + timedelta(days=random.randint(-7, 14))
                status = "Completed"
            else:
                actual_date = None
                status = random.choice(["Pending", "In Progress"])

            milestones_data.append((
                project_id, name, desc, planned_date.strftime("%Y-%m-%d"),
                actual_date.strftime("%Y-%m-%d") if actual_date else None, status, category
            ))

    cursor.executemany('''
        INSERT INTO project_milestones (project_id, milestone_name, description, planned_date,
                                       actual_date, status, category)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', milestones_data)

def insert_project_budgets(cursor):
    """Insert project budget breakdown data."""
    # Get all project IDs
    cursor.execute("SELECT id FROM projects")
    project_ids = [row[0] for row in cursor.fetchall()]

    budget_categories = [
        ("Labor", ["Senior Consultants", "Junior Consultants", "Project Management"]),
        ("Technology", ["Software Licenses", "Cloud Infrastructure", "Hardware"]),
        ("Travel", ["Team Travel", "Client Meetings"]),
        ("Training", ["Team Training", "Certifications"]),
        ("Contingency", ["Risk Mitigation", "Change Requests"])
    ]

    budget_data = []

    for project_id in project_ids:
        # Get total budget
        cursor.execute("SELECT budget FROM projects WHERE id = ?", (project_id,))
        total_budget = cursor.fetchone()[0]

        # Distribute budget across categories
        remaining_budget = total_budget

        for category, subcategories in budget_categories:
            if remaining_budget <= 0:
                break

            # Allocate 15-30% to each category
            allocation_pct = random.uniform(0.15, 0.30)
            category_budget = min(remaining_budget, total_budget * allocation_pct)
            remaining_budget -= category_budget

            # Split category across subcategories
            for subcategory in subcategories:
                sub_allocation = category_budget / len(subcategories)
                planned_amount = sub_allocation * random.uniform(0.9, 1.1)  # ±10% variance
                actual_amount = planned_amount * random.uniform(0.8, 1.2) if random.random() < 0.6 else None

                budget_data.append((
                    project_id, category, subcategory, planned_amount,
                    actual_amount, "USD"
                ))

    cursor.executemany('''
        INSERT INTO project_budgets (project_id, category, subcategory, planned_amount, actual_amount, currency)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', budget_data)

def insert_project_risks(cursor):
    """Insert project risks data."""
    # Get all project IDs
    cursor.execute("SELECT id FROM projects")
    project_ids = [row[0] for row in cursor.fetchall()]

    risk_templates = [
        ("Resource shortage", "High", "Medium", "Hire additional consultants or adjust timeline"),
        ("Technology complexity", "High", "Medium", "Conduct technical spike and training"),
        ("Client requirement changes", "Medium", "High", "Implement change control process"),
        ("Integration challenges", "Medium", "Medium", "Design comprehensive testing strategy"),
        ("Security compliance issues", "Critical", "Low", "Regular security assessments and audits"),
        ("Budget overruns", "High", "Medium", "Monthly budget reviews and forecasting"),
        ("Timeline delays", "Medium", "High", "Agile delivery approach with regular checkpoints"),
        ("Team knowledge gaps", "Medium", "Medium", "Knowledge transfer and mentoring program")
    ]

    risk_data = []

    for project_id in project_ids:
        # Assign 1-3 risks per project
        num_risks = random.randint(1, 3)
        selected_risks = random.sample(risk_templates, num_risks)

        for risk_desc, impact, probability, mitigation in selected_risks:
            risk_level = random.choice(RISK_LEVELS)
            status = random.choice(["Open", "Mitigated", "Closed"])
            owner = random.choice(["Project Manager", "Technical Lead", "Delivery Manager", "Team Lead"])

            risk_data.append((
                project_id, risk_desc, impact, probability, risk_level,
                mitigation, status, owner
            ))

    cursor.executemany('''
        INSERT INTO project_risks (project_id, risk_description, impact, probability, risk_level,
                                  mitigation_plan, status, owner)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    ''', risk_data)

def insert_project_status_updates(cursor):
    """Insert project status updates data."""
    # Get all project IDs
    cursor.execute("SELECT id FROM projects")
    project_ids = [row[0] for row in cursor.fetchall()]

    status_data = []

    for project_id in project_ids:
        # Generate 4-8 status updates per project
        num_updates = random.randint(4, 8)

        # Get project start date
        cursor.execute("SELECT start_date FROM projects WHERE id = ?", (project_id,))
        start_date = cursor.fetchone()[0]
        start_dt = datetime.strptime(start_date, "%Y-%m-%d")

        for i in range(num_updates):
            # Updates every 2-4 weeks
            update_date = start_dt + timedelta(days=i * random.randint(14, 28))

            overall_progress = min(100, i * (100 / num_updates) + random.uniform(-10, 10))
            overall_progress = max(0, overall_progress)

            phase_status = random.choice(["On Track", "Minor Delays", "Major Delays", "Ahead of Schedule"])

            issues = random.choice([
                "Minor integration issues resolved",
                "Resource allocation optimized",
                "Client feedback incorporated",
                "Testing phase extended slightly",
                "No major issues",
                "Budget tracking on target"
            ])

            next_steps = random.choice([
                "Continue development phase",
                "Prepare for testing phase",
                "Client UAT planning",
                "Deployment preparation",
                "Post-implementation support"
            ])

            updated_by = random.choice(["Project Manager", "Technical Lead", "Delivery Manager"])

            status_data.append((
                project_id, update_date.strftime("%Y-%m-%d"), overall_progress,
                phase_status, issues, next_steps, updated_by
            ))

    cursor.executemany('''
        INSERT INTO project_status_updates (project_id, update_date, overall_progress, phase_status,
                                           issues, next_steps, updated_by)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', status_data)

def insert_project_technologies(cursor):
    """Insert project technologies junction data."""
    # Get all project IDs and technology IDs
    cursor.execute("SELECT id FROM projects")
    project_ids = [row[0] for row in cursor.fetchall()]

    cursor.execute("SELECT id FROM technologies")
    technology_ids = [row[0] for row in cursor.fetchall()]

    tech_assignments = []

    for project_id in project_ids:
        # Assign 3-6 technologies per project
        num_tech = random.randint(3, 6)
        selected_tech = random.sample(technology_ids, num_tech)

        for tech_id in selected_tech:
            primary_use = random.choice([
                "Primary development platform",
                "Cloud infrastructure",
                "Database solution",
                "CI/CD pipeline",
                "Monitoring and logging",
                "Security implementation",
                "API development",
                "Data processing"
            ])

            tech_assignments.append((project_id, tech_id, primary_use))

    cursor.executemany('''
        INSERT INTO project_technologies (project_id, technology_id, primary_use)
        VALUES (?, ?, ?)
    ''', tech_assignments)

def test_database():
    """Run some test queries to verify the database."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    print("\n=== Projects Database Test Results ===")

    # Count records in each table
    tables = ["clients", "technologies", "projects", "project_phases", "project_teams",
              "project_milestones", "project_budgets", "project_risks", "project_status_updates",
              "project_technologies"]
    for table in tables:
        cursor.execute(f"SELECT COUNT(*) FROM {table}")
        count = cursor.fetchone()[0]
        print(f"{table}: {count} records")

    # Sample queries
    print("\n=== Sample Queries ===")

    # Active projects by client
    cursor.execute("""
        SELECT c.name as client, COUNT(p.id) as active_projects
        FROM clients c
        LEFT JOIN projects p ON c.id = p.client_id AND p.status = 'Active'
        GROUP BY c.id, c.name
        ORDER BY active_projects DESC
        LIMIT 5
    """)
    print("\nTop 5 clients by active projects:")
    for row in cursor.fetchall():
        print(f"  {row[0]}: {row[1]} active projects")

    # Project budget summary
    cursor.execute("""
        SELECT
            SUM(budget) as total_budget,
            AVG(budget) as avg_budget,
            COUNT(*) as total_projects
        FROM projects
        WHERE status IN ('Active', 'Completed')
    """)
    budget_stats = cursor.fetchone()
    print(".2f"
    # Technologies usage
    cursor.execute("""
        SELECT t.name, COUNT(pt.id) as usage_count
        FROM technologies t
        JOIN project_technologies pt ON t.id = pt.technology_id
        GROUP BY t.id, t.name
        ORDER BY usage_count DESC
        LIMIT 5
    """)
    print("\nTop 5 most used technologies:")
    for row in cursor.fetchall():
        print(f"  {row[0]}: used in {row[1]} projects")

    # Risk analysis
    cursor.execute("""
        SELECT risk_level, COUNT(*) as count
        FROM project_risks
        GROUP BY risk_level
        ORDER BY count DESC
    """)
    print("\nRisk distribution:")
    for row in cursor.fetchall():
        print(f"  {row[0]}: {row[1]} risks")

    conn.close()

if __name__ == "__main__":
    create_database()
    test_database()
