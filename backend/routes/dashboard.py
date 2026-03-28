from flask import Blueprint, jsonify
from db import get_db
from routes.auth import login_required

dashboard_bp = Blueprint("dashboard", __name__)


@dashboard_bp.route("/dashboard/stats", methods=["GET"])
@login_required
def get_stats():
    conn   = get_db()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("SELECT COUNT(*) AS cnt FROM Item")
    total_items = cursor.fetchone()["cnt"]

    cursor.execute(
        "SELECT COALESCE(SUM(TotalQuantity),0) AS t, COALESCE(SUM(AvailableQuantity),0) AS a FROM Item"
    )
    qty = cursor.fetchone()

    cursor.execute(
        "SELECT COUNT(*) AS cnt FROM Usage_Record WHERE ReturnDate IS NULL"
    )
    active = cursor.fetchone()["cnt"]

    cursor.execute(
        """SELECT COUNT(*) AS cnt FROM Usage_Record
           WHERE ReturnDate IS NULL AND DATEDIFF(CURDATE(), IssueDate) > 7"""
    )
    overdue = cursor.fetchone()["cnt"]

    cursor.execute("SELECT COUNT(*) AS cnt FROM Category")
    categories = cursor.fetchone()["cnt"]

    cursor.execute("SELECT COUNT(*) AS cnt FROM ExternalTeam")
    teams = cursor.fetchone()["cnt"]

    cursor.execute("SELECT COUNT(*) AS cnt FROM Project")
    projects = cursor.fetchone()["cnt"]

    cursor.close(); conn.close()

    total_qty    = int(qty["t"])
    available    = int(qty["a"])
    in_use       = total_qty - available

    return jsonify({
        "total_items":        total_items,
        "total_quantity":     total_qty,
        "available_quantity": available,
        "in_use_quantity":    in_use,
        "active_issues":      active,
        "overdue_count":      overdue,
        "categories":         categories,
        "teams":              teams,
        "projects":           projects,
    })


@dashboard_bp.route("/dashboard/recent", methods=["GET"])
@login_required
def get_recent():
    conn   = get_db()
    cursor = conn.cursor(dictionary=True)
    cursor.execute(
        """SELECT ur.UsageID, ur.Quantity, ur.IssueDate, ur.ReturnDate,
                  i.ItemName, s.StatusName, p.ProjectName, t.TeamName
           FROM Usage_Record ur
           JOIN  Item i ON ur.ItemID   = i.ItemID
           JOIN  Status s ON ur.StatusID = s.StatusID
           LEFT JOIN Project p ON ur.ProjectID = p.ProjectID
           LEFT JOIN ExternalTeam t ON ur.TeamID = t.TeamID
           ORDER BY ur.UsageID DESC LIMIT 10"""
    )
    records = cursor.fetchall()
    for r in records:
        if r["IssueDate"] and hasattr(r["IssueDate"], "isoformat"):
            r["IssueDate"] = r["IssueDate"].isoformat()
        if r["ReturnDate"] and hasattr(r["ReturnDate"], "isoformat"):
            r["ReturnDate"] = r["ReturnDate"].isoformat()
    cursor.close(); conn.close()
    return jsonify(records)


@dashboard_bp.route("/dashboard/category-stats", methods=["GET"])
@login_required
def get_category_stats():
    conn   = get_db()
    cursor = conn.cursor(dictionary=True)
    cursor.execute(
        """SELECT c.CategoryName,
                  COUNT(i.ItemID)                         AS item_count,
                  COALESCE(SUM(i.TotalQuantity),0)        AS total_qty,
                  COALESCE(SUM(i.AvailableQuantity),0)    AS available_qty
           FROM Category c
           LEFT JOIN Item i ON c.CategoryID = i.CategoryID
           GROUP BY c.CategoryID, c.CategoryName
           ORDER BY item_count DESC"""
    )
    data = cursor.fetchall()
    cursor.close(); conn.close()
    return jsonify(data)