"""
Serviço: Catalog Repository - Carregamento e gerenciamento de regras
"""

import csv
import os
from pathlib import Path
from typing import Optional

from app.schemas.models import CatalogRule


class CatalogRepository:
    """Repositório para carregar e gerenciar catálogo de regras."""

    def __init__(self, catalog_path: str | None = None):
        """
        Inicializar repositório com caminho para catálogo.

        Args:
            catalog_path: Caminho relativo ou absoluto para o arquivo CSV
        """
        resolved_path = catalog_path or os.getenv("CATALOG_RULES_PATH", "data/catalog_rules_v1.csv")
        self.catalog_path = Path(resolved_path)
        self._rules_cache: Optional[list[CatalogRule]] = None

    def load_rules(self) -> list[CatalogRule]:
        """
        Carregar regras do arquivo CSV.

        Returns:
            Lista de CatalogRule carregadas do CSV

        Raises:
            FileNotFoundError: Se o arquivo CSV não existir
            ValueError: Se houver erro ao processar o CSV
        """
        if self._rules_cache is not None:
            return self._rules_cache

        if not self.catalog_path.exists():
            raise FileNotFoundError(f"Catálogo não encontrado: {self.catalog_path}")

        rules = []

        try:
            with open(self.catalog_path, "r", encoding="utf-8") as f:
                reader = csv.DictReader(f)

                if reader.fieldnames is None:
                    raise ValueError("Arquivo CSV vazio ou inválido")

                for row_num, row in enumerate(reader, start=2):  # start=2 (header é linha 1)
                    try:
                        rule = self._parse_rule_row(row, row_num)
                        rules.append(rule)
                    except ValueError as e:
                        raise ValueError(f"Erro na linha {row_num}: {e}")

        except csv.Error as e:
            raise ValueError(f"Erro ao processar CSV: {e}")

        # Cache das regras carregadas
        self._rules_cache = rules
        return rules

    @staticmethod
    def _parse_rule_row(row: dict, row_num: int) -> CatalogRule:
        """
        Parse uma linha do CSV para CatalogRule.

        Args:
            row: Dicionário com dados da linha
            row_num: Número da linha (para mensagens de erro)

        Returns:
            CatalogRule instanciada

        Raises:
            ValueError: Se algum campo obrigatório estiver vazio ou inválido
        """
        # Validar campos obrigatórios
        rule_id = row.get("rule_id", "").strip()
        if not rule_id:
            raise ValueError("rule_id é obrigatório e não pode estar vazio")

        name = row.get("name", "").strip()
        if not name:
            raise ValueError("name é obrigatório e não pode estar vazio")

        domain = row.get("domain", "").strip()
        if not domain:
            raise ValueError("domain é obrigatório e não pode estar vazio")

        description = row.get("description", "").strip()
        if not description:
            raise ValueError("description é obrigatório e não pode estar vazio")

        # Parse booleanos
        mandatory_str = row.get("mandatory", "").strip().lower()
        if mandatory_str not in ("true", "false"):
            raise ValueError(f"mandatory deve ser 'true' ou 'false', recebido: '{mandatory_str}'")
        mandatory = mandatory_str == "true"

        blocking_str = row.get("blocking", "").strip().lower()
        if blocking_str not in ("true", "false"):
            raise ValueError(f"blocking deve ser 'true' ou 'false', recebido: '{blocking_str}'")
        blocking = blocking_str == "true"

        # Parse keywords (separados por ;)
        keywords_str = row.get("keywords", "").strip().strip('"')
        keywords = [k.strip() for k in keywords_str.split(";") if k.strip()]

        evidence = row.get("evidence", "").strip()
        if not evidence:
            raise ValueError("evidence é obrigatório e não pode estar vazio")

        return CatalogRule(
            rule_id=rule_id,
            name=name,
            domain=domain,
            description=description,
            mandatory=mandatory,
            blocking=blocking,
            keywords=keywords,
            evidence=evidence,
        )

    def get_rule(self, rule_id: str) -> Optional[CatalogRule]:
        """
        Obter uma regra específica pelo ID.

        Args:
            rule_id: ID da regra

        Returns:
            CatalogRule se encontrada, None caso contrário
        """
        rules = self.load_rules()
        for rule in rules:
            if rule.rule_id == rule_id:
                return rule
        return None

    def get_rules_by_domain(self, domain: str) -> list[CatalogRule]:
        """
        Obter todas as regras de um domínio.

        Args:
            domain: Domínio das regras

        Returns:
            Lista de CatalogRule do domínio especificado
        """
        rules = self.load_rules()
        return [r for r in rules if r.domain == domain]

    def get_mandatory_rules(self) -> list[CatalogRule]:
        """
        Obter todas as regras obrigatórias.

        Returns:
            Lista de CatalogRule obrigatórias
        """
        rules = self.load_rules()
        return [r for r in rules if r.mandatory]

    def get_blocking_rules(self) -> list[CatalogRule]:
        """
        Obter todas as regras bloqueantes.

        Returns:
            Lista de CatalogRule bloqueantes
        """
        rules = self.load_rules()
        return [r for r in rules if r.blocking]

    def clear_cache(self):
        """Limpar cache de regras carregadas."""
        self._rules_cache = None

    def sync_csv_to_db(self) -> int:
        """
        Sincronizar regras do CSV para o banco de dados.

        Returns:
            Número de regras sincronizadas
        """
        try:
            from app.services.persistence_service import PersistenceService

            # Carregar regras do CSV
            rules = self.load_rules()

            # Converter para dicionários
            rules_dict = [
                {
                    "rule_id": rule.rule_id,
                    "name": rule.name,
                    "domain": rule.domain,
                    "description": rule.description,
                    "mandatory": rule.mandatory,
                    "blocking": rule.blocking,
                    "keywords": rule.keywords,
                    "evidence": rule.evidence,
                }
                for rule in rules
            ]

            # Salvar no banco
            count = PersistenceService.save_rule_catalog(rules_dict)
            return count

        except Exception as e:
            print(f"Erro ao sincronizar catálogo: {e}")
            return 0
