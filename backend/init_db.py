"""
init_db.py — Run this ONCE to:
  1. Create all tables
  2. Insert sample data (categories, items, teams, projects, statuses)
  3. Create default users with hashed passwords

Usage:
    cd backend
    python init_db.py
"""

import sys
import os
import mysql.connector
from werkzeug.security import generate_password_hash
from datetime import date, timedelta

# ── Connection settings (mirrors config.py) ──────────────────────────────────
DB_HOST     = os.getenv("MYSQLHOST", os.getenv("MYSQL_HOST", "localhost"))
DB_PORT     = int(os.getenv("MYSQLPORT", os.getenv("MYSQL_PORT", "3306")))
DB_USER     = os.getenv("MYSQLUSER", os.getenv("MYSQL_USER", "root"))
DB_PASSWORD = os.getenv("MYSQLPASSWORD", os.getenv("MYSQL_ROOT_PASSWORD", os.getenv("MYSQL_PASSWORD", "")))
DB_NAME     = os.getenv("MYSQLDATABASE", os.getenv("MYSQL_DATABASE", "robotics_inventory"))


def run(cursor, sql, params=None):
    cursor.execute(sql, params or ())


def setup():
    # Connect without specifying a database first
    conn = mysql.connector.connect(
        host=DB_HOST, port=DB_PORT, user=DB_USER, password=DB_PASSWORD
    )
    cursor = conn.cursor()

    # Create DB
    cursor.execute(
        f"CREATE DATABASE IF NOT EXISTS {DB_NAME} CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci"
    )
    cursor.execute(f"USE {DB_NAME}")

    # ── Tables ────────────────────────────────────────────────────────────────
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS Status (
        StatusID   INT         PRIMARY KEY AUTO_INCREMENT,
        StatusName VARCHAR(50) NOT NULL UNIQUE
    )""")

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS Category (
        CategoryID   INT          PRIMARY KEY AUTO_INCREMENT,
        CategoryName VARCHAR(100) NOT NULL,
        Description  VARCHAR(255)
    )""")

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS Item (
        ItemID            INT          PRIMARY KEY AUTO_INCREMENT,
        ItemName          VARCHAR(150) NOT NULL,
        CategoryID        INT          NOT NULL,
        TotalQuantity     INT          NOT NULL DEFAULT 0,
        AvailableQuantity INT          NOT NULL DEFAULT 0,
        StorageLocation   VARCHAR(100),
        FOREIGN KEY (CategoryID) REFERENCES Category(CategoryID)
    )""")

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS ExternalTeam (
        TeamID        INT          PRIMARY KEY AUTO_INCREMENT,
        TeamName      VARCHAR(150) NOT NULL,
        ContactPerson VARCHAR(100)
    )""")

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS Project (
        ProjectID   INT          PRIMARY KEY AUTO_INCREMENT,
        ProjectName VARCHAR(150) NOT NULL,
        LeadStudent VARCHAR(100)
    )""")

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS Usage_Record (
        UsageID    INT  PRIMARY KEY AUTO_INCREMENT,
        ItemID     INT  NOT NULL,
        StatusID   INT  NOT NULL,
        ProjectID  INT,
        TeamID     INT,
        Quantity   INT  NOT NULL DEFAULT 1,
        IssueDate  DATE NOT NULL,
        ReturnDate DATE,
        FOREIGN KEY (ItemID)    REFERENCES Item(ItemID),
        FOREIGN KEY (StatusID)  REFERENCES Status(StatusID),
        FOREIGN KEY (ProjectID) REFERENCES Project(ProjectID),
        FOREIGN KEY (TeamID)    REFERENCES ExternalTeam(TeamID)
    )""")

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS Users (
        UserID   INT          PRIMARY KEY AUTO_INCREMENT,
        Username VARCHAR(100) NOT NULL UNIQUE,
        Password VARCHAR(255) NOT NULL,
        FullName VARCHAR(150),
        Role     ENUM('admin','lab_incharge','student','guest') NOT NULL DEFAULT 'student',
        TeamID   INT,
        FOREIGN KEY (TeamID) REFERENCES ExternalTeam(TeamID)
    )""")

    conn.commit()
    print("Tables created.")

    # ── Status ────────────────────────────────────────────────────────────────
    for s in ["Available", "In Use", "Borrowed"]:
        cursor.execute(
            "INSERT IGNORE INTO Status (StatusName) VALUES (%s)", (s,)
        )

    # ── Categories ────────────────────────────────────────────────────────────
    categories = [
        ("Electronics",      "Arduino boards, Raspberry Pi, microcontrollers"),
        ("Sensors",          "Ultrasonic, IR, temperature, gas, color sensors"),
        ("Motors & Actuators","DC motors, servo motors, stepper motors, ESCs"),
        ("Tools",            "Soldering iron, multimeter, wire cutter, pliers"),
        ("Mechanical Parts", "Chassis, wheels, gears, bearings, brackets"),
    ]
    for name, desc in categories:
        cursor.execute(
            "INSERT IGNORE INTO Category (CategoryName, Description) VALUES (%s, %s)",
            (name, desc),
        )

    # ── Items ─────────────────────────────────────────────────────────────────
    # We need category IDs — fetch after insert
    conn.commit()
    cursor.execute("SELECT CategoryID, CategoryName FROM Category")
    cat_map = {row[1]: row[0] for row in cursor.fetchall()}

    items = [
        ("Arduino Uno R3",          "Electronics",       10, 10, "Shelf A1"),
        ("Raspberry Pi 4B",         "Electronics",        5,  5, "Shelf A2"),
        ("ESP32 Dev Board",         "Electronics",        8,  8, "Shelf A3"),
        ("Ultrasonic Sensor HC-SR04","Sensors",           15, 15, "Shelf B1"),
        ("IR Sensor Module",        "Sensors",           12, 12, "Shelf B2"),
        ("Temperature Sensor DHT22","Sensors",           10, 10, "Shelf B3"),
        ("DC Motor 12V",            "Motors & Actuators", 8,  8, "Shelf C1"),
        ("Servo Motor SG90",        "Motors & Actuators",20, 20, "Shelf C2"),
        ("Stepper Motor NEMA17",    "Motors & Actuators", 6,  6, "Shelf C3"),
        ("Digital Multimeter",      "Tools",              5,  5, "Tool Rack D1"),
        ("Soldering Iron 60W",      "Tools",              4,  4, "Tool Rack D2"),
        ("Wire Stripper",           "Tools",              6,  6, "Tool Rack D3"),
        ("Robot Chassis Kit",       "Mechanical Parts",   6,  6, "Shelf E1"),
        ("Plastic Wheels (set of 4)","Mechanical Parts", 10, 10, "Shelf E2"),
        ("Aluminium Brackets",      "Mechanical Parts",  30, 30, "Shelf E3"),
    ]
    for name, cat, total, avail, loc in items:
        cursor.execute(
            """INSERT IGNORE INTO Item (ItemName, CategoryID, TotalQuantity, AvailableQuantity, StorageLocation)
               VALUES (%s, %s, %s, %s, %s)""",
            (name, cat_map[cat], total, avail, loc),
        )

    # ── External Teams ────────────────────────────────────────────────────────
    teams = [
        ("Team Alpha",   "Riya Joshi"),
        ("Team Beta",    "Karan Mehta"),
        ("Team Gamma",   "Priya Singh"),
    ]
    for tname, contact in teams:
        cursor.execute(
            "INSERT IGNORE INTO ExternalTeam (TeamName, ContactPerson) VALUES (%s, %s)",
            (tname, contact),
        )

    # ── Projects ──────────────────────────────────────────────────────────────
    projects = [
        ("Line Following Robot",     "Aashvi Budia"),
        ("Obstacle Avoidance Bot",   "Dhruv Sharma"),
        ("Smart Plant Monitor",      "Muhir Kapoor"),
        ("Wireless Gesture Control", "Riya Joshi"),
    ]
    for pname, lead in projects:
        cursor.execute(
            "INSERT IGNORE INTO Project (ProjectName, LeadStudent) VALUES (%s, %s)",
            (pname, lead),
        )

    conn.commit()

    # ── Sample Usage Records ──────────────────────────────────────────────────
    cursor.execute("SELECT ItemID, ItemName, AvailableQuantity FROM Item")
    item_map = {row[1]: (row[0], row[2]) for row in cursor.fetchall()}

    cursor.execute("SELECT StatusID, StatusName FROM Status")
    stat_map = {row[1]: row[0] for row in cursor.fetchall()}

    cursor.execute("SELECT ProjectID, ProjectName FROM Project")
    proj_map = {row[1]: row[0] for row in cursor.fetchall()}

    cursor.execute("SELECT TeamID, TeamName FROM ExternalTeam")
    team_map = {row[1]: row[0] for row in cursor.fetchall()}

    today = date.today()

    usage_records = [
        # (ItemName, qty, status, project, team, issue_offset, return_offset_or_None)
        ("Arduino Uno R3",           2, "In Use",  "Line Following Robot",     None,         -10, None),
        ("Ultrasonic Sensor HC-SR04",3, "In Use",  "Obstacle Avoidance Bot",   None,         -5,  None),
        ("Servo Motor SG90",         4, "In Use",  "Wireless Gesture Control", None,         -3,  None),
        ("DC Motor 12V",             2, "Borrowed", None, "Team Alpha",         -8,  None),
        ("Robot Chassis Kit",        1, "Borrowed", None, "Team Beta",          -15, None),  # overdue
        ("IR Sensor Module",         2, "Borrowed", None, "Team Gamma",         -12, None),  # overdue
        ("Digital Multimeter",       1, "In Use",  "Smart Plant Monitor",      None,         -2,  None),
        # Returned records (for history)
        ("Raspberry Pi 4B",          1, "Available","Line Following Robot",    None,         -20, -10),
        ("Temperature Sensor DHT22", 2, "Available", None, "Team Alpha",       -18, -5),
        ("Wire Stripper",            1, "Available","Smart Plant Monitor",     None,         -7,  -1),
    ]

    for item_name, qty, status_lbl, proj_name, team_name, issue_off, ret_off in usage_records:
        item_id, avail = item_map.get(item_name, (None, 0))
        if not item_id:
            continue
        status_id = stat_map.get(status_lbl)
        proj_id   = proj_map.get(proj_name) if proj_name else None
        team_id   = team_map.get(team_name) if team_name else None
        issue_dt  = today + timedelta(days=issue_off)
        ret_dt    = (today + timedelta(days=ret_off)) if ret_off is not None else None

        cursor.execute(
            """INSERT INTO Usage_Record (ItemID, StatusID, ProjectID, TeamID, Quantity, IssueDate, ReturnDate)
               VALUES (%s, %s, %s, %s, %s, %s, %s)""",
            (item_id, status_id, proj_id, team_id, qty, issue_dt, ret_dt),
        )
        # Deduct from available if still out
        if ret_dt is None:
            cursor.execute(
                "UPDATE Item SET AvailableQuantity = AvailableQuantity - %s WHERE ItemID=%s",
                (qty, item_id),
            )

    conn.commit()
    print("Sample data inserted.")

    # ── Default Users ─────────────────────────────────────────────────────────
    users = [
        ("admin",    "admin123",    "Lab Administrator",   "admin",       None),
        ("incharge", "incharge123", "Dr. Ramesh Kumar",    "lab_incharge",None),
        ("student1", "student123",  "Aashvi Budia",        "student",     None),
        ("student2", "student123",  "Dhruv Sharma",        "student",     None),
        ("guest",    "guest123",    "Guest User",          "guest",       None),
    ]
    for uname, pwd, full, role, tid in users:
        hashed = generate_password_hash(pwd)
        cursor.execute(
            """INSERT IGNORE INTO Users (Username, Password, FullName, Role, TeamID)
               VALUES (%s, %s, %s, %s, %s)""",
            (uname, hashed, full, role, tid),
        )

    conn.commit()
    print("✅  Default users created.")
    print()
    print("  USERNAME    PASSWORD       ROLE")
    print("  ──────────────────────────────────────")
    print("  admin       admin123       admin")
    print("  incharge    incharge123    lab_incharge")
    print("  student1    student123     student")
    print("  student2    student123     student")
    print("  guest       guest123       guest")

    cursor.close()
    conn.close()
    print()
    print("Database setup complete! Run:  python app.py")


if __name__ == "__main__":
    try:
        setup()
    except mysql.connector.Error as e:
        print(f"MySQL error: {e}")
        sys.exit(1)
