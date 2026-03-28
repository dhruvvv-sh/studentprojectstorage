"""
Configuration for Robotics Lab Inventory System.
Set MySQL values via environment variables for deployment.
"""

import os


def _env_first(*names, default=None, required=False):
    for name in names:
        value = os.getenv(name)
        if value not in (None, ""):
            return value
    if required:
        raise ValueError(f"Missing required environment variable. Set one of: {', '.join(names)}")
    return default


class Config:
    SECRET_KEY      = "robotics_lab_secret_key_2024_change_in_production"
    MYSQL_HOST      = _env_first("MYSQLHOST", "MYSQL_HOST", default="localhost")
    MYSQL_PORT      = int(_env_first("MYSQLPORT", "MYSQL_PORT", default="3306"))
    MYSQL_USER      = _env_first("MYSQLUSER", "MYSQL_USER", default="root")
    MYSQL_PASSWORD  = _env_first("MYSQLPASSWORD", "MYSQL_ROOT_PASSWORD", "MYSQL_PASSWORD", required=True)
    MYSQL_DB        = _env_first("MYSQLDATABASE", "MYSQL_DATABASE", default="robotics_inventory")
    SESSION_COOKIE_SAMESITE = "Lax"
    SESSION_COOKIE_HTTPONLY = True
