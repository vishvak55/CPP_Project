"""Lending CRUD API routes."""

from flask import Blueprint, request, jsonify
from models.database import db, LendingModel, ToolModel
import uuid
from datetime import datetime, timedelta

lendings_bp = Blueprint("lendings", __name__)


@lendings_bp.route("/api/lendings", methods=["GET"])
def list_lendings():
    """List all lending records with optional filtering."""
    status = request.args.get("status")
    borrower_id = request.args.get("borrower_id")
    tool_id = request.args.get("tool_id")

    query = LendingModel.query

    if status:
        query = query.filter_by(status=status)
    if borrower_id:
        query = query.filter_by(borrower_id=borrower_id)
    if tool_id:
        query = query.filter_by(tool_id=tool_id)

    lendings = query.all()
    return jsonify({"lendings": [l.to_dict() for l in lendings], "count": len(lendings)})


@lendings_bp.route("/api/lendings/<record_id>", methods=["GET"])
def get_lending(record_id):
    """Get a specific lending record by ID."""
    lending = LendingModel.query.get(record_id)
    if not lending:
        return jsonify({"error": "Lending record not found"}), 404
    return jsonify(lending.to_dict())


@lendings_bp.route("/api/lendings", methods=["POST"])
def create_lending():
    """Create a new lending request."""
    data = request.get_json()
    if not data or not data.get("tool_id") or not data.get("borrower_id"):
        return jsonify({"error": "tool_id and borrower_id are required"}), 400

    lending = LendingModel(
        record_id=str(uuid.uuid4()),
        tool_id=data["tool_id"],
        borrower_id=data["borrower_id"],
        lender_id=data.get("lender_id"),
        status="requested",
        requested_at=datetime.utcnow(),
        lending_days=data.get("lending_days", 7),
        notes=data.get("notes"),
    )
    db.session.add(lending)
    db.session.commit()
    return jsonify(lending.to_dict()), 201


@lendings_bp.route("/api/lendings/<record_id>", methods=["PUT"])
def update_lending(record_id):
    """Update a lending record."""
    lending = LendingModel.query.get(record_id)
    if not lending:
        return jsonify({"error": "Lending record not found"}), 404

    data = request.get_json()
    if not data:
        return jsonify({"error": "No data provided"}), 400

    for field in ("status", "lending_days", "notes", "lender_id"):
        if field in data:
            setattr(lending, field, data[field])

    db.session.commit()
    return jsonify(lending.to_dict())


@lendings_bp.route("/api/lendings/<record_id>", methods=["DELETE"])
def delete_lending(record_id):
    """Delete a lending record."""
    lending = LendingModel.query.get(record_id)
    if not lending:
        return jsonify({"error": "Lending record not found"}), 404

    db.session.delete(lending)
    db.session.commit()
    return jsonify({"message": "Lending record deleted", "record_id": record_id})


@lendings_bp.route("/api/lendings/<record_id>/approve", methods=["POST"])
def approve_lending(record_id):
    """Approve a lending request."""
    lending = LendingModel.query.get(record_id)
    if not lending:
        return jsonify({"error": "Lending record not found"}), 404
    if lending.status != "requested":
        return jsonify({"error": f"Cannot approve lending in status '{lending.status}'"}), 400

    lending.status = "approved"
    lending.approved_at = datetime.utcnow()
    db.session.commit()
    return jsonify(lending.to_dict())


@lendings_bp.route("/api/lendings/<record_id>/activate", methods=["POST"])
def activate_lending(record_id):
    """Activate a lending (mark tool as handed over)."""
    lending = LendingModel.query.get(record_id)
    if not lending:
        return jsonify({"error": "Lending record not found"}), 404
    if lending.status != "approved":
        return jsonify({"error": f"Cannot activate lending in status '{lending.status}'"}), 400

    lending.status = "active"
    lending.lent_at = datetime.utcnow()
    lending.due_date = datetime.utcnow() + timedelta(days=lending.lending_days)

    # Mark tool as unavailable
    tool = ToolModel.query.get(lending.tool_id)
    if tool:
        tool.is_available = False

    db.session.commit()
    return jsonify(lending.to_dict())


@lendings_bp.route("/api/lendings/<record_id>/return", methods=["POST"])
def return_lending(record_id):
    """Mark a tool as returned."""
    lending = LendingModel.query.get(record_id)
    if not lending:
        return jsonify({"error": "Lending record not found"}), 404
    if lending.status not in ("active", "overdue"):
        return jsonify({"error": f"Cannot return lending in status '{lending.status}'"}), 400

    lending.status = "returned"
    lending.returned_at = datetime.utcnow()

    # Mark tool as available
    tool = ToolModel.query.get(lending.tool_id)
    if tool:
        tool.is_available = True

    db.session.commit()
    return jsonify(lending.to_dict())
