"""
Session do banco de dados
"""

from app.db.base import SessionLocal


def get_session():
    """Obter nova session."""
    return SessionLocal()
