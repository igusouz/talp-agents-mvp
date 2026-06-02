"""
Inicialização do banco de dados
"""

from app.db.base import Base, engine


def init_db():
    """Criar todas as tabelas."""
    Base.metadata.create_all(bind=engine)


if __name__ == "__main__":
    init_db()
    print("✅ Banco de dados inicializado")
