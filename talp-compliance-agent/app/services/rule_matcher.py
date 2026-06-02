"""
Serviço: Rule Matcher - Matching heurístico entre User Stories e Catálogo de Regras
"""

import re
import unicodedata
from typing import Optional

from app.schemas.models import DetectedRule, RuleDependency
from app.services.catalog_repository import CatalogRepository


class RuleMatcher:
    """Matchear regras de compliance entre User Stories e catálogo."""

    def __init__(self, catalog_path: str = "data/catalog_rules_v1.csv"):
        """
        Inicializar matcher com catálogo de regras.

        Args:
            catalog_path: Caminho para o arquivo CSV de regras
        """
        self.catalog_repository = CatalogRepository(catalog_path)
        self.rules = self.catalog_repository.load_rules()

    @staticmethod
    def normalize_text(text: str) -> str:
        """
        Normalizar texto para comparação insensível a acentos e maiúsculas.

        Args:
            text: Texto a normalizar

        Returns:
            Texto normalizado (minúsculas, sem acentos)
        """
        # Converter para minúsculas
        text = text.lower()

        # Remover acentos usando NFD (decomposição)
        text = unicodedata.normalize("NFD", text)
        text = "".join(c for c in text if unicodedata.category(c) != "Mn")

        return text

    def find_matching_keywords(
        self, user_story: str, rule_keywords: list[str]
    ) -> list[str]:
        """
        Encontrar palavras-chave da regra na User Story.

        Args:
            user_story: Texto da User Story
            rule_keywords: Lista de palavras-chave da regra

        Returns:
            Lista de palavras-chave encontradas
        """
        matched = []
        normalized_story = self.normalize_text(user_story)

        for keyword in rule_keywords:
            normalized_keyword = self.normalize_text(keyword)

            # Usar word boundaries para buscar palavras completas
            # Escapa caracteres especiais do regex
            pattern = r"\b" + re.escape(normalized_keyword) + r"\b"

            if re.search(pattern, normalized_story):
                matched.append(keyword)

        return matched

    def match_rules(self, user_story: str) -> list[DetectedRule]:
        """
        Matchear User Story contra todas as regras do catálogo.

        Args:
            user_story: Texto da User Story

        Returns:
            Lista de DetectedRule com regras encontradas
        """
        detected_rules = []

        for rule in self.rules:
            matched_keywords = self.find_matching_keywords(user_story, rule.keywords)

            if matched_keywords:
                # Calcular confidence baseado na quantidade de keywords encontradas
                confidence = min(len(matched_keywords) / len(rule.keywords), 1.0)

                detected_rule = DetectedRule(
                    rule_id=rule.rule_id,
                    name=rule.name,
                    domain=rule.domain,
                    matched=True,
                    confidence=confidence,
                    evidence_found=matched_keywords,
                    dependencies=[],
                )

                detected_rules.append(detected_rule)

        return detected_rules

    def get_detected_rules_dict(self, user_story: str) -> list[dict]:
        """
        Matchear User Story e retornar como dicionários com todos os campos.

        Args:
            user_story: Texto da User Story

        Returns:
            Lista de dicionários com dados da regra + matching
        """
        detected_rules = self.match_rules(user_story)
        result = []

        for detected in detected_rules:
            # Buscar a regra original no catálogo
            original_rule = self.catalog_repository.get_rule(detected.rule_id)

            if original_rule:
                rule_dict = {
                    "rule_id": original_rule.rule_id,
                    "name": original_rule.name,
                    "domain": original_rule.domain,
                    "description": original_rule.description,
                    "mandatory": original_rule.mandatory,
                    "blocking": original_rule.blocking,
                    "matched_keywords": detected.evidence_found,
                    "literal_evidence": detected.evidence_found,
                    "source": "Catalogo_Regras_V1",
                    "confidence": detected.confidence,
                }
                result.append(rule_dict)

        return result

    def validate_matched_rule_ids(self, detected_rules: list[DetectedRule]) -> bool:
        """
        Validar que todos os rule_ids das regras detectadas existem no catálogo.

        Args:
            detected_rules: Lista de regras detectadas

        Returns:
            True se todos os IDs são válidos, False caso contrário
        """
        valid_rule_ids = {rule.rule_id for rule in self.rules}

        for detected in detected_rules:
            if detected.rule_id not in valid_rule_ids:
                return False

        return True
