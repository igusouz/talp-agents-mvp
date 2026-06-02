"""
Testes para carregamento do catálogo de regras
"""

import pytest

from app.services.catalog_repository import CatalogRepository


class TestCatalogLoader:
    """Testes para o carregamento do catálogo de regras."""

    @pytest.fixture
    def catalog(self):
        """Fixture para criar repositório do catálogo."""
        return CatalogRepository("data/catalog_rules_v1.csv")

    def test_load_catalog_returns_8_rules(self, catalog):
        """Deve carregar exatamente 8 regras do catálogo."""
        rules = catalog.load_rules()
        assert len(rules) == 8, f"Esperado 8 regras, mas carregou {len(rules)}"

    def test_catalog_contains_rule_001(self, catalog):
        """Deve conter a regra RULE_001."""
        rule = catalog.get_rule("RULE_001")
        assert rule is not None, "RULE_001 não foi encontrada no catálogo"
        assert rule.rule_id == "RULE_001"
        assert rule.name == "Sinais Vitais Obrigatórios"
        assert rule.domain == "Triagem"

    def test_catalog_contains_rule_008(self, catalog):
        """Deve conter a regra RULE_008."""
        rule = catalog.get_rule("RULE_008")
        assert rule is not None, "RULE_008 não foi encontrada no catálogo"
        assert rule.rule_id == "RULE_008"
        assert rule.name == "Validação CCIH"
        assert rule.domain == "Controle de Infecção"

    def test_no_rule_with_empty_rule_id(self, catalog):
        """Nenhuma regra pode ter rule_id vazio."""
        rules = catalog.load_rules()
        for rule in rules:
            assert rule.rule_id, "Encontrada regra com rule_id vazio"
            assert rule.rule_id.strip() != "", "Encontrada regra com rule_id em branco"

    def test_all_rules_have_mandatory_and_blocking_fields(self, catalog):
        """Todas as regras devem ter campos mandatory e blocking."""
        rules = catalog.load_rules()
        for rule in rules:
            assert isinstance(rule.mandatory, bool), f"mandatory deve ser bool, recebido {type(rule.mandatory)}"
            assert isinstance(rule.blocking, bool), f"blocking deve ser bool, recebido {type(rule.blocking)}"

    def test_all_rules_have_keywords(self, catalog):
        """Todas as regras devem ter pelo menos uma keyword."""
        rules = catalog.load_rules()
        for rule in rules:
            assert len(rule.keywords) > 0, f"Regra {rule.rule_id} não possui keywords"

    def test_all_rules_have_evidence(self, catalog):
        """Todas as regras devem ter um evidence ID."""
        rules = catalog.load_rules()
        for rule in rules:
            assert rule.evidence, f"Regra {rule.rule_id} não possui evidence"

    def test_get_mandatory_rules(self, catalog):
        """Deve retornar lista de regras obrigatórias."""
        mandatory_rules = catalog.get_mandatory_rules()
        assert len(mandatory_rules) > 0, "Deve haver regras obrigatórias"
        for rule in mandatory_rules:
            assert rule.mandatory is True

    def test_get_blocking_rules(self, catalog):
        """Deve retornar lista de regras bloqueantes."""
        blocking_rules = catalog.get_blocking_rules()
        assert len(blocking_rules) > 0, "Deve haver regras bloqueantes"
        for rule in blocking_rules:
            assert rule.blocking is True

    def test_get_rules_by_domain(self, catalog):
        """Deve retornar regras de um domínio específico."""
        triagem_rules = catalog.get_rules_by_domain("Triagem")
        assert len(triagem_rules) > 0, "Deve haver regras no domínio Triagem"
        for rule in triagem_rules:
            assert rule.domain == "Triagem"

    def test_catalog_caching(self, catalog):
        """Regras devem ser cacheadas após primeiro carregamento."""
        rules1 = catalog.load_rules()
        rules2 = catalog.load_rules()
        # Mesma referência de memória indica que foi cacheado
        assert rules1 is rules2, "Regras não foram cacheadas corretamente"

    def test_cache_clear(self, catalog):
        """Cache deve ser limpável."""
        rules1 = catalog.load_rules()
        catalog.clear_cache()
        rules2 = catalog.load_rules()
        assert rules1 is not rules2, "Cache não foi limpo corretamente"
        assert len(rules1) == len(rules2), "Número de regras mudou após limpar cache"

    def test_all_rules_have_valid_fields(self, catalog):
        """Todas as regras devem ter campos válidos."""
        rules = catalog.load_rules()
        for rule in rules:
            assert rule.rule_id.strip() != "", "rule_id vazio"
            assert rule.name.strip() != "", "name vazio"
            assert rule.domain.strip() != "", "domain vazio"
            assert rule.description.strip() != "", "description vazio"
            assert len(rule.keywords) > 0, "keywords vazio"
            assert rule.evidence.strip() != "", "evidence vazio"

    def test_first_rule_is_rule_001(self, catalog):
        """A primeira regra do catálogo deve ser RULE_001."""
        rules = catalog.load_rules()
        assert rules[0].rule_id == "RULE_001", "Primeira regra não é RULE_001"

    def test_last_rule_is_rule_008(self, catalog):
        """A última regra do catálogo deve ser RULE_008."""
        rules = catalog.load_rules()
        assert rules[-1].rule_id == "RULE_008", "Última regra não é RULE_008"
