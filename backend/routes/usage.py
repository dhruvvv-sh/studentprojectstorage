from flask import Blueprint, request, jsonify
from db import get_db
from routes.auth import login_required, role_required
from datetime import date, timedelta

usage_bp = Blueprint("usage", __name__)


def _serialize_record(r):
    """Convert date fields to ISO strings."""
    if r.get("IssueDate") and hasattr(r["IssueDate"], "isoformat"):
        r["IssueDate"] = r["IssueDate"].isoformat()
    if r.get("ReturnDate") and hasattr(r["ReturnDate"], "isoformat"):
        r["ReturnDate"] = r["ReturnDate"].isoformat()
    return r


BASE_SELECT = """
    SELECT ur.UsageID, ur.Quantity, ur.IssueDate, ur.ReturnDate,
           i.ItemID, i.ItemName,
           s.StatusID, s.StatusName,
           p.ProjectID, p.ProjectName,
           t.TeamID, t.TeamName
    FROM Usage_Record ur
    JOIN  Item         i ON ur.ItemID    = i.ItemID
    JOIN  Status       s ON ur.StatusID  = s.StatusID
    LEFT JOIN Project  p ON ur.ProjectID = p.ProjectID
    LEFT JOIN ExternalTeam t ON ur.TeamID = t.TeamID
"""


@usage_bp.route("/usage", methods=["GET"])
@login_required
def get_all_usage():
    conn   = get_db()
    cursor = conn.cursor(dictionary=True)
    cursor.execute(BASE_SELECT + " ORDER BY ur.UsageID DESC")
    records = [_serialize_record(r) for r in cursor.fetchall()]
    cursor.close(); conn.close()
    return jsonify(records)


@usage_bp.route("/usage/active", methods=["GET"])
@login_required
def get_active_usage():
    today  = date.today()
    conn   = get_db()
    cursor = conn.cursor(dictionary=True)
    cursor.execute(BASE_SELECT + " WHERE ur.ReturnDate IS NULL ORDER BY ur.IssueDate DESC")
    rows = cursor.fetchall()
    records = []
    for r in rows:
        r = _serialize_record(r)
        if r["IssueDate"]:
            r["days_out"] = (today - date.fromisoformat(r["IssueDate"])).days
        records.append(r)
    cursor.close(); conn.close()
    return jsonify(records)


@usage_bp.route("/usage/overdue", methods=["GET"])
@login_required
def get_overdue():
    threshold = (date.today() - timedelta(days=7)).isoformat()
    conn   = get_db()
    cursor = conn.cursor(dictionary=True)
    cursor.execute(
        BASE_SELECT + """
        WHERE ur.ReturnDate IS NULL AND ur.IssueDate <= %s
        ORDER BY ur.IssueDate ASC
        """,
        (threshold,),
    )
    records = [_serialize_record(r) for r in cursor.fetchall()]
    today = date.today()
    for r in records:
        if r["IssueDate"]:
            r["days_overdue"] = (today - date.fromisoformat(r["IssueDate"])).days
    cursor.close(); conn.close()
    return jsonify(records)


@usage_bp.route("/usage/issue", methods=["POST"])
@role_required("admin", "lab_incharge", "student")
def issue_item():
    body       = request.get_json() or {}
    item_id    = body.get("item_id")
    quantity   = int(body.get("quantity", 1))
    project_id = body.get("project_id") or None
    team_id    = body.get("team_id")    or None
    status_lbl = body.get("status", "In Use")

    if not item_id:
        return jsonify({"error": "item_id is required"}), 400
    if quantity < 1:
        return jsonify({"error": "Quantity must be at least 1"}), 400

    conn   = get_db()
    cursor = conn.cursor(dictionary=True)

    # Check stock
    cursor.execute("SELECT ItemName, AvailableQuantity FROM Item WHERE ItemID=%s", (item_id,))
    item = cursor.fetchone()
    if not item:
        cursor.close(); conn.close()
        return jsonify({"error": "Item not found"}), 404
    if item["AvailableQuantity"] < quantity:
        cursor.close(); conn.close()
        return jsonify({
            "error": f"Only {item['AvailableQuantity']} unit(s) available for '{item['ItemName']}'"
        }), 400

    # Resolve status
    cursor.execute("SELECT StatusID FROM Status WHERE StatusName=%s", (status_lbl,))
    status = cursor.fetchone()
    if not status:
        cursor.close(); conn.close()
        return jsonify({"error": f"Status '{status_lbl}' not found"}), 400

    # Insert usage record
    cursor.execute(
        """INSERT INTO Usage_Record (ItemID, StatusID, ProjectID, TeamID, Quantity, IssueDate)
           VALUES (%s, %s, %s, %s, %s, CURDATE())""",
        (item_id, status["StatusID"], project_id, team_id, quantity),
    )
    # Deduct stock
    cursor.execute(
        "UPDATE Item SET AvailableQuantity = AvailableQuantity - %s WHERE ItemID=%s",
        (quantity, item_id),
    )
    conn.commit()
    new_id = cursor.lastrowid
    cursor.close(); conn.close()
    return jsonify({"success": True, "usage_id": new_id}), 201


@usage_bp.route("/usage/return/<int:usage_id>", methods=["PUT"])
@role_required("admin", "lab_incharge", "student")
def return_item(usage_id):
    conn   = get_db()
    cursor = conn.cursor(dictionary=True)

    cursor.execute(
        "SELECT * FROM Usage_Record WHERE UsageID=%s AND ReturnDate IS NULL",
        (usage_id,),
    )
    record = cursor.fetchone()
    if not record:
        cursor.close(); conn.close()
        return jsonify({"error": "Record not found or already returned"}), 404

    # Get "Available" status id
    cursor.execute("SELECT StatusID FROM Status WHERE StatusName='Available'")
    available = cursor.fetchone()

    cursor.execute(
        "UPDATE Usage_Record SET ReturnDate=CURDATE(), StatusID=%s WHERE UsageID=%s",
        (available["StatusID"], usage_id),
    )
    cursor.execute(
        "UPDATE Item SET AvailableQuantity = AvailableQuantity + %s WHERE ItemID=%s",
        (record["Quantity"], record["ItemID"]),
    )
    conn.commit()
    cursor.close(); conn.close()
    return jsonify({"success": True})