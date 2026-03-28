"""
Configuration for Robotics Lab Inventory System.
Set MySQL values via environment variables for deployment.
"""

from env_utils import env_first


class Config:
    SECRET_KEY      = env_first(
        "FLASK_SECRET_KEY",
        "SECRET_KEY",
        required=True,
        required_message=(
            "Missing Flask secret key. Set FLASK_SECRET_KEY (preferred) or SECRET_KEY "
            "to a long random value before starting the app."
        ),
    )
    MYSQL_HOST      = env_first("MYSQLHOST", "MYSQL_HOST", default="localhost")
    MYSQL_PORT      = int(env_first("MYSQLPORT", "MYSQL_PORT", default="3306"))
    MYSQL_USER      = env_first("MYSQLUSER", "MYSQL_USER", default="root")
    MYSQL_PASSWORD  = env_first(
        "MYSQLPASSWORD",
        "MYSQL_ROOT_PASSWORD",
        "MYSQL_PASSWORD",
        required=True,
        required_message=(
            "Missing MySQL password. Set MYSQLPASSWORD (preferred), MYSQL_ROOT_PASSWORD, "
            "or MYSQL_PASSWORD before starting the app."
        ),
    )
    MYSQL_DB        = env_first("MYSQLDATABASE", "MYSQL_DATABASE", default="robotics_inventory")
    SESSION_COOKIE_SAMESITE = "Lax"
    SESSION_COOKIE_HTTPONLY = True
