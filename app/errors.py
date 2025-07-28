# app/errors.py
from flask import Blueprint, render_template, jsonify, request
from werkzeug.exceptions import HTTPException
import logging

errors = Blueprint("errors", __name__)
logger = logging.getLogger(__name__)


@errors.app_errorhandler(404)
def not_found_error(error):
    """Handle 404 errors."""
    if request.path.startswith("/api/"):
        return jsonify({"error": "Resource not found"}), 404
    return render_template("errors/404.html"), 404


@errors.app_errorhandler(500)
def internal_error(error):
    """Handle 500 errors."""
    logger.error(f"Internal error: {error}", exc_info=True)
    if request.path.startswith("/api/"):
        return jsonify({"error": "Internal server error"}), 500
    return render_template("errors/500.html"), 500


@errors.app_errorhandler(HTTPException)
def handle_exception(e):
    """Handle all HTTP exceptions."""
    logger.warning(f"HTTP Exception: {e}")
    if request.path.startswith("/api/"):
        return jsonify({"error": e.description}), e.code
    return render_template("errors/error.html", error=e), e.code
