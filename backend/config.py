"""
Configuration for Robotics Lab Inventory System.
Set MySQL values via environment variables for deployment.
"""

import os


class Config:
    SECRET_KEY      = "robotics_lab_secret_key_2024_change_in_production"
    MYSQL_HOST      = os.getenv("MYSQLHOST", os.getenv("MYSQL_HOST", "localhost"))
    MYSQL_PORT      = int(os.getenv("MYSQLPORT", os.getenv("MYSQL_PORT", "3306")))
    MYSQL_USER      = os.getenv("MYSQLUSER", os.getenv("MYSQL_USER", "root"))
    MYSQL_PASSWORD  = os.getenv("MYSQLPASSWORD", os.getenv("MYSQL_ROOT_PASSWORD", os.getenv("MYSQL_PASSWORD", "")))
    MYSQL_DB        = os.getenv("MYSQLDATABASE", os.getenv("MYSQL_DATABASE", "robotics_inventory"))
    SESSION_COOKIE_SAMESITE = "Lax"
    SESSION_COOKIE_HTTPONLY = True
