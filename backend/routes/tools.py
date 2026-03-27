"""Tool CRUD API routes."""

from flask import Blueprint, request, jsonify
from models.database import db, ToolModel
import uuid
from datetime import datetime

tools_bp = Blueprint("tools", __name__)


@tools_bp.route("/api/tools", methods=["GET"])
def list_tools():
    """List all tools with optional filtering."""
    category = request.args.get("category")
    available = request.args.get("available")
    search = request.args.get("search")

    query = ToolModel.query

    if category:
        query = query.filter_by(category=category)
    if available is not None:
        query = query.filter_by(is_available=available.lower() == "true")
    if search:
        query = query.filter(ToolModel.name.contains(search))

    tools = query.all()
    return jsonify({"tools": [t.to_dict() for t in tools], "count": len(tools)})


@tools_bp.route("/api/tools/<tool_id>", methods=["GET"])
def get_tool(tool_id):
    """Get a specific tool by ID."""
    tool = ToolModel.query.get(tool_id)
    if not tool:
        return jsonify({"error": "Tool not found"}), 404
    return jsonify(tool.to_dict())


@tools_bp.route("/api/tools", methods=["POST"])
def create_tool():
    """Create a new tool."""
    data = request.get_json()
    if not data or not data.get("name"):
        return jsonify({"error": "Tool name is required"}), 400

    tool = ToolModel(
        tool_id=str(uuid.uuid4()),
        name=data["name"],
        description=data.get("description", ""),
        category=data.get("category", "other"),
        condition=data.get("condition", "good"),
        owner_id=data.get("owner_id"),
        image_url=data.get("image_url"),
        max_lending_days=data.get("max_lending_days", 14),
        is_available=True,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
    )
    db.session.add(tool)
    db.session.commit()
    return jsonify(tool.to_dict()), 201


@tools_bp.route("/api/tools/<tool_id>", methods=["PUT"])
def update_tool(tool_id):
    """Update an existing tool."""
    tool = ToolModel.query.get(tool_id)
    if not tool:
        return jsonify({"error": "Tool not found"}), 404

    data = request.get_json()
    if not data:
        return jsonify({"error": "No data provided"}), 400

    for field in ("name", "description", "category", "condition",
                  "owner_id", "image_url", "max_lending_days", "is_available"):
        if field in data:
            setattr(tool, field, data[field])
    tool.updated_at = datetime.utcnow()

    db.session.commit()
    return jsonify(tool.to_dict())


@tools_bp.route("/api/tools/<tool_id>", methods=["DELETE"])
def delete_tool(tool_id):
    """Delete a tool."""
    tool = ToolModel.query.get(tool_id)
    if not tool:
        return jsonify({"error": "Tool not found"}), 404

    db.session.delete(tool)
    db.session.commit()
    return jsonify({"message": "Tool deleted", "tool_id": tool_id})
