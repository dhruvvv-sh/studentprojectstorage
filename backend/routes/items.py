from flask import Blueprint, request, jsonify, session
from werkzeug.security import generate_password_hash
from db import get_db
from routes.auth import login_required, role_required

items_bp = Blueprint("items", __name__)


# ══════════════════════════════════════════════════════════════
#  CATEGORIES
# ══════════════════════════════════════════════════════════════

@items_bp.route("/categories", methods=["GET"])
@login_required
def get_categories():
    conn   = get_db()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM Category ORDER BY CategoryName")
    data = cursor.fetchall()
    cursor.close(); conn.close()
    return jsonify(data)


@items_bp.route("/categories", methods=["POST"])
@role_required("admin", "lab_incharge")
def add_category():
    body = request.get_json() or {}
    if not body.get("name"):
        return jsonify({"error": "Category name is required"}), 400
    conn   = get_db()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO Category (CategoryName, Description) VALUES (%s, %s)",
        (body["name"], body.get("description", "")),
    )
    conn.commit()
    new_id = cursor.lastrowid
    cursor.close(); conn.close()
    return jsonify({"success": True, "id": new_id}), 201


@items_bp.route("/categories/<int:cat_id>", methods=["PUT"])
@role_required("admin", "lab_incharge")
def update_category(cat_id):
    body = request.get_json() or {}
    conn   = get_db()
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE Category SET CategoryName=%s, Description=%s WHERE CategoryID=%s",
        (body.get("name"), body.get("description", ""), cat_id),
    )
    conn.commit()
    cursor.close(); conn.close()
    return jsonify({"success": True})


@items_bp.route("/categories/<int:cat_id>", methods=["DELETE"])
@role_required("admin")
def delete_category(cat_id):
    conn   = get_db()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM Category WHERE CategoryID=%s", (cat_id,))
    conn.commit()
    cursor.close(); conn.close()
    return jsonify({"success": True})


# ══════════════════════════════════════════════════════════════
#  ITEMS
# ══════════════════════════════════════════════════════════════

@items_bp.route("/items", methods=["GET"])
@login_required
def get_items():
    search   = request.args.get("search", "")
    category = request.args.get("category", "")

    query  = """
        SELECT i.ItemID, i.ItemName, i.TotalQuantity, i.AvailableQuantity,
               i.StorageLocation, i.CategoryID, c.CategoryName,
               (i.TotalQuantity - i.AvailableQuantity) AS InUseQuantity
        FROM Item i
        JOIN Category c ON i.CategoryID = c.CategoryID
        WHERE 1=1
    """
    params = []

    if search:
        query += " AND (i.ItemName LIKE %s OR i.StorageLocation LIKE %s)"
        params += [f"%{search}%", f"%{search}%"]
    if category:
        query += " AND i.CategoryID = %s"
        params.append(category)

    query += " ORDER BY i.ItemName"

    conn   = get_db()
    cursor = conn.cursor(dictionary=True)
    cursor.execute(query, params)
    data = cursor.fetchall()
    cursor.close(); conn.close()
    return jsonify(data)


@items_bp.route("/items/<int:item_id>", methods=["GET"])
@login_required
def get_item(item_id):
    conn   = get_db()
    cursor = conn.cursor(dictionary=True)
    cursor.execute(
        """SELECT i.*, c.CategoryName FROM Item i
           JOIN Category c ON i.CategoryID = c.CategoryID
           WHERE i.ItemID = %s""",
        (item_id,),
    )
    item = cursor.fetchone()
    cursor.close(); conn.close()
    if not item:
        return jsonify({"error": "Item not found"}), 404
    return jsonify(item)


@items_bp.route("/items", methods=["POST"])
@role_required("admin", "lab_incharge")
def add_item():
    body = request.get_json() or {}
    if not body.get("name") or not body.get("category_id"):
        return jsonify({"error": "Item name and category are required"}), 400
    qty = int(body.get("quantity", 0))
    conn   = get_db()
    cursor = conn.cursor()
    cursor.execute(
        """INSERT INTO Item (ItemName, CategoryID, TotalQuantity, AvailableQuantity, StorageLocation)
           VALUES (%s, %s, %s, %s, %s)""",
        (body["name"], body["category_id"], qty, qty, body.get("storage_location", "")),
    )
    conn.commit()
    new_id = cursor.lastrowid
    cursor.close(); conn.close()
    return jsonify({"success": True, "id": new_id}), 201


@items_bp.route("/items/<int:item_id>", methods=["PUT"])
@role_required("admin", "lab_incharge")
def update_item(item_id):
    body = request.get_json() or {}
    conn   = get_db()
    cursor = conn.cursor()
    cursor.execute(
        """UPDATE Item
           SET ItemName=%s, CategoryID=%s, TotalQuantity=%s,
               AvailableQuantity=%s, StorageLocation=%s
           WHERE ItemID=%s""",
        (
            body.get("name"), body.get("category_id"),
            body.get("total_quantity"), body.get("available_quantity"),
            body.get("storage_location", ""), item_id,
        ),
    )
    conn.commit()
    cursor.close(); conn.close()
    return jsonify({"success": True})


@items_bp.route("/items/<int:item_id>", methods=["DELETE"])
@role_required("admin")
def delete_item(item_id):
    conn   = get_db()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM Item WHERE ItemID=%s", (item_id,))
    conn.commit()
    cursor.close(); conn.close()
    return jsonify({"success": True})


# ══════════════════════════════════════════════════════════════
#  EXTERNAL TEAMS
# ══════════════════════════════════════════════════════════════

@items_bp.route("/teams", methods=["GET"])
@login_required
def get_teams():
    conn   = get_db()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM ExternalTeam ORDER BY TeamName")
    data = cursor.fetchall()
    cursor.close(); conn.close()
    return jsonify(data)


@items_bp.route("/teams", methods=["POST"])
@role_required("admin", "lab_incharge")
def add_team():
    body = request.get_json() or {}
    if not body.get("name"):
        return jsonify({"error": "Team name is required"}), 400
    conn   = get_db()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO ExternalTeam (TeamName, ContactPerson) VALUES (%s, %s)",
        (body["name"], body.get("contact", "")),
    )
    conn.commit()
    new_id = cursor.lastrowid
    cursor.close(); conn.close()
    return jsonify({"success": True, "id": new_id}), 201


@items_bp.route("/teams/<int:team_id>", methods=["PUT"])
@role_required("admin", "lab_incharge")
def update_team(team_id):
    body = request.get_json() or {}
    conn   = get_db()
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE ExternalTeam SET TeamName=%s, ContactPerson=%s WHERE TeamID=%s",
        (body.get("name"), body.get("contact", ""), team_id),
    )
    conn.commit()
    cursor.close(); conn.close()
    return jsonify({"success": True})


# ══════════════════════════════════════════════════════════════
#  PROJECTS
# ══════════════════════════════════════════════════════════════

@items_bp.route("/projects", methods=["GET"])
@login_required
def get_projects():
    conn   = get_db()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM Project ORDER BY ProjectName")
    data = cursor.fetchall()
    cursor.close(); conn.close()
    return jsonify(data)


@items_bp.route("/projects", methods=["POST"])
@role_required("admin", "lab_incharge", "student")
def add_project():
    body = request.get_json() or {}
    if not body.get("name"):
        return jsonify({"error": "Project name is required"}), 400
    conn   = get_db()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO Project (ProjectName, LeadStudent) VALUES (%s, %s)",
        (body["name"], body.get("lead_student", "")),
    )
    conn.commit()
    new_id = cursor.lastrowid
    cursor.close(); conn.close()
    return jsonify({"success": True, "id": new_id}), 201


@items_bp.route("/projects/<int:project_id>", methods=["PUT"])
@role_required("admin", "lab_incharge", "student")
def update_project(project_id):
    body = request.get_json() or {}
    conn   = get_db()
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE Project SET ProjectName=%s, LeadStudent=%s WHERE ProjectID=%s",
        (body.get("name"), body.get("lead_student", ""), project_id),
    )
    conn.commit()
    cursor.close(); conn.close()
    return jsonify({"success": True})


# ══════════════════════════════════════════════════════════════
#  STATUS
# ══════════════════════════════════════════════════════════════

@items_bp.route("/status", methods=["GET"])
@login_required
def get_status():
    conn   = get_db()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM Status")
    data = cursor.fetchall()
    cursor.close(); conn.close()
    return jsonify(data)


# ══════════════════════════════════════════════════════════════
#  USERS  (admin only)
# ══════════════════════════════════════════════════════════════

@items_bp.route("/users", methods=["GET"])
@role_required("admin")
def get_users():
    conn   = get_db()
    cursor = conn.cursor(dictionary=True)
    cursor.execute(
        """SELECT u.UserID, u.Username, u.FullName, u.Role, u.TeamID, t.TeamName
           FROM Users u
           LEFT JOIN ExternalTeam t ON u.TeamID = t.TeamID
           ORDER BY u.FullName"""
    )
    data = cursor.fetchall()
    cursor.close(); conn.close()
    return jsonify(data)


@items_bp.route("/users", methods=["POST"])
@role_required("admin")
def add_user():
    body = request.get_json() or {}
    if not body.get("username") or not body.get("password"):
        return jsonify({"error": "Username and password are required"}), 400
    conn   = get_db()
    cursor = conn.cursor()
    hashed = generate_password_hash(body["password"])
    cursor.execute(
        """INSERT INTO Users (Username, Password, FullName, Role, TeamID)
           VALUES (%s, %s, %s, %s, %s)""",
        (body["username"], hashed, body.get("full_name", ""), body.get("role", "student"), body.get("team_id")),
    )
    conn.commit()
    new_id = cursor.lastrowid
    cursor.close(); conn.close()
    return jsonify({"success": True, "id": new_id}), 201


@items_bp.route("/users/<int:user_id>", methods=["DELETE"])
@role_required("admin")
def delete_user(user_id):
    if user_id == session.get("user_id"):
        return jsonify({"error": "Cannot delete your own account"}), 400
    conn   = get_db()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM Users WHERE UserID=%s", (user_id,))
    conn.commit()
    cursor.close(); conn.close()
    return jsonify({"success": True})