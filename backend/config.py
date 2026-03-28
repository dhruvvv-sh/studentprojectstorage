"""
Configuration for Robotics Lab Inventory System.
Update MYSQL_PASSWORD before running.
"""

class Config:
    SECRET_KEY      = "robotics_lab_secret_key_2024_change_in_production"
    MYSQL_HOST      = "localhost"
    MYSQL_PORT      = 3306
    MYSQL_USER      = "root"
    MYSQL_PASSWORD  = "$dhruv2005$"   # <-- change this
    MYSQL_DB        = "robotics_inventory"
    SESSION_COOKIE_SAMESITE = "Lax"
    SESSION_COOKIE_HTTPONLY = True