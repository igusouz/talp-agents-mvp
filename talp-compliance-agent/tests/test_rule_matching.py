"""
Testes para matching heurístico de regras
"""

import pytest

from app.services.rule_matcher import RuleMatcher


class TestRuleMatcher:
    """Testes para o serviço de matching entre User Stories e Regras."""

    @pytest.fixture
    def matcher(self):
        """Fixture para criar instância do RuleMatcher."""
        return RuleMatcher("data/catalog_rules_v1.csv")

    # =========================================================================
    # TESTES OBRIGATÓRIOS
    # =========================================================================

    def test_user_story_with_triagem_and_sinais_vitais_detects_rule_001(self, matcher):
        """Deve detectar RULE_001 quando US contém 'triagem' e 'sinais vitais'."""
        user_story = (
            "Como triador, devo registrar os sinais vitais do paciente "
            "e identificar suas comorbidades"
        )

        detected = matcher.match_rules(user_story)
        rule_ids = [r.rule_id for r in detected]

        assert "RULE_001" in rule_ids, "RULE_001 deveria ter sido detectada"

    def test_user_story_with_antibiotico_detects_rule_008(self, matcher):
        """Deve detectar RULE_008 quando US contém 'antibiótico'."""
        user_story = (
            "Todo paciente que recebe um antibiótico deve ter sua prescrição "
            "validada pela CCIH"
        )

        detected = matcher.match_rules(user_story)
        rule_ids = [r.rule_id for r in detected]

        assert "RULE_008" in rule_ids, "RULE_008 deveria ter sido detectada"

    def test_user_story_with_medicamento_detects_rule_007(self, matcher):
        """Deve detectar RULE_007 quando US contém 'medicamento'."""
        user_story = "O paciente deve receber medicamento apenas com prescrição válida"

        detected = matcher.match_rules(user_story)
        rule_ids = [r.rule_id for r in detected]

        assert "RULE_007" in rule_ids, "RULE_007 deveria ter sido detectada"

    def test_user_story_without_evidence_returns_no_rules(self, matcher):
        """Deve retornar lista vazia quando US não contém evidências do catálogo."""
        user_story = (
            "O paciente deve receber uma xícara de café e um biscoito no café da manhã"
        )

        detected = matcher.match_rules(user_story)

        assert len(detected) == 0, "Não deveria ter detectado nenhuma regra"

    def test_matcher_cannot_return_nonexistent_rule_id(self, matcher):
        """O matcher não pode retornar um rule_id que não existe no catálogo."""
        # Criar uma User Story que poderia gerar matches (para garantir que funciona)
        user_story = "Triagem com sinais vitais do paciente"

        detected = matcher.match_rules(user_story)

        # Validar que todos os rule_ids detectados existem no catálogo
        is_valid = matcher.validate_matched_rule_ids(detected)
        assert is_valid, "Detector retornou rule_id que não existe no catálogo"

    # =========================================================================
    # TESTES ADICIONAIS DE NORMALIZACAO
    # =========================================================================

    def test_matcher_is_case_insensitive(self, matcher):
        """Deve ignorar diferença de maiúsculas/minúsculas."""
        user_story_lower = "triagem com sinais vitais"
        user_story_upper = "TRIAGEM COM SINAIS VITAIS"
        user_story_mixed = "TrIaGeM CoM SiNaIs ViTaIs"

        detected_lower = matcher.match_rules(user_story_lower)
        detected_upper = matcher.match_rules(user_story_upper)
        detected_mixed = matcher.match_rules(user_story_mixed)

        assert len(detected_lower) > 0
        assert len(detected_upper) > 0
        assert len(detected_mixed) > 0
        assert (
            detected_lower[0].rule_id
            == detected_upper[0].rule_id
            == detected_mixed[0].rule_id
        )

    def test_matcher_normalizes_accents(self, matcher):
        """Deve tratar palavras com e sem acento como equivalentes."""
        # RULE_001 tem "parâmetros"
        user_story_with_accent = "Os parâmetros clínicos devem ser registrados"
        user_story_without_accent = "Os parametros clinicos devem ser registrados"

        detected_with = matcher.match_rules(user_story_with_accent)
        detected_without = matcher.match_rules(user_story_without_accent)

        assert len(detected_with) > 0, "Deveria detectar com acentos"
        assert len(detected_without) > 0, "Deveria detectar sem acentos"

    def test_normalize_text_removes_accents(self, matcher):
        """Função normalize_text deve remover acentos."""
        text_with_accents = "São José - Análise"
        normalized = matcher.normalize_text(text_with_accents)

        assert "ã" not in normalized
        assert "é" not in normalized
        assert normalized == "sao jose - analise"

    def test_normalize_text_to_lowercase(self, matcher):
        """Função normalize_text deve converter para minúsculas."""
        text = "HELLO World ÉTudO"
        normalized = matcher.normalize_text(text)

        assert normalized == normalized.lower()
        assert normalized == "hello world etudo"

    # =========================================================================
    # TESTES DE MATCHING SPECIFICOS
    # =========================================================================

    def test_find_matching_keywords_for_rule_001(self, matcher):
        """Deve encontrar keywords de RULE_001 em uma User Story."""
        user_story = "Triagem deve conter sinais vitais e parâmetros clínicos"
        rule = matcher.catalog_repository.get_rule("RULE_001")

        matched = matcher.find_matching_keywords(user_story, rule.keywords)

        assert len(matched) > 0, "Deveria ter encontrado keywords"
        assert any("triagem" in k.lower() for k in matched)

    def test_confidence_calculation(self, matcher):
        """Confidence deve ser baseado na quantidade de keywords encontradas."""
        # User Story com apenas 1 keyword
        user_story_partial = "Triagem do paciente"
        detected_partial = matcher.match_rules(user_story_partial)

        # User Story com múltiplas keywords
        user_story_full = "Triagem com sinais vitais e parâmetros clínicos e comorbidades"
        detected_full = matcher.match_rules(user_story_full)

        if len(detected_partial) > 0 and len(detected_full) > 0:
            # A US com mais keywords deve ter confidence igual ou maior
            partial_conf = detected_partial[0].confidence
            full_conf = detected_full[0].confidence

            assert (
                full_conf >= partial_conf
            ), "Confidence deveria ser maior com mais keywords"

    def test_get_detected_rules_dict_format(self, matcher):
        """Deve retornar dicionários com todos os campos obrigatórios."""
        user_story = "Triagem com sinais vitais"

        rules_dict = matcher.get_detected_rules_dict(user_story)

        assert len(rules_dict) > 0

        for rule_dict in rules_dict:
            assert "rule_id" in rule_dict
            assert "name" in rule_dict
            assert "domain" in rule_dict
            assert "description" in rule_dict
            assert "mandatory" in rule_dict
            assert "blocking" in rule_dict
            assert "matched_keywords" in rule_dict
            assert "literal_evidence" in rule_dict
            assert rule_dict["source"] == "Catalogo_Regras_V1"

    def test_matched_keywords_are_from_rule(self, matcher):
        """Keywords retornadas devem pertencer à regra original."""
        user_story = "Triagem e sinais vitais com comorbidades"

        detected = matcher.match_rules(user_story)

        for detected_rule in detected:
            # Buscar a regra original
            original_rule = matcher.catalog_repository.get_rule(detected_rule.rule_id)
            assert original_rule is not None

            # Verificar que keywords detectadas existem na regra
            for keyword in detected_rule.evidence_found:
                assert keyword in original_rule.keywords

    def test_empty_user_story_returns_no_rules(self, matcher):
        """User Story vazia não deve retornar regras."""
        detected = matcher.match_rules("")
        assert len(detected) == 0

    def test_user_story_with_similar_but_different_words(self, matcher):
        """Palavras similares mas diferentes não devem gerar falsos positivos."""
        # "triadagem" é similar a "triagem" mas é diferente
        user_story = "Triadagem do paciente"

        detected = matcher.match_rules(user_story)

        # Não deveria detectar RULE_001
        rule_ids = [r.rule_id for r in detected]
        assert "RULE_001" not in rule_ids

    def test_manchester_keyword_matching(self, matcher):
        """Deve detectar palavras-chave do Protocolo Manchester."""
        user_story = "Classificação de risco segundo Manchester"

        detected = matcher.match_rules(user_story)
        rule_ids = [r.rule_id for r in detected]

        assert "RULE_002" in rule_ids, "Deveria detectar RULE_002 (Manchester)"

    def test_hda_keyword_matching(self, matcher):
        """Deve detectar HDA (História da Doença Atual)."""
        user_story = "O médico deve registrar a HDA do paciente"

        detected = matcher.match_rules(user_story)
        rule_ids = [r.rule_id for r in detected]

        assert "RULE_003" in rule_ids, "Deveria detectar RULE_003 (HDA)"

    def test_cid_keyword_matching(self, matcher):
        """Deve detectar CID (Classificação de Doenças)."""
        user_story = "Todo atendimento deve ter um diagnóstico com CID"

        detected = matcher.match_rules(user_story)
        rule_ids = [r.rule_id for r in detected]

        assert "RULE_004" in rule_ids, "Deveria detectar RULE_004 (CID)"

    def test_prescricao_keyword_matching(self, matcher):
        """Deve detectar palavras relacionadas a prescrição."""
        user_story = "O médico faz a prescrição do fármaco"

        detected = matcher.match_rules(user_story)
        rule_ids = [r.rule_id for r in detected]

        assert "RULE_007" in rule_ids, "Deveria detectar RULE_007 (Prescrição)"

    def test_antimicrobiano_keyword_matching(self, matcher):
        """Deve detectar antimicrobiano (alternativa a antibiótico)."""
        user_story = "O uso de antimicrobiano requer validação CCIH"

        detected = matcher.match_rules(user_story)
        rule_ids = [r.rule_id for r in detected]

        assert "RULE_008" in rule_ids, "Deveria detectar RULE_008 (Antimicrobiano)"

    def test_multiple_rules_can_be_detected_in_same_user_story(self, matcher):
        """Múltiplas regras podem ser detectadas na mesma User Story."""
        user_story = (
            "Na triagem, registrar sinais vitais. "
            "No diagnóstico, usar CID. "
            "Para medicamentos, exigir prescrição."
        )

        detected = matcher.match_rules(user_story)
        rule_ids = [r.rule_id for r in detected]

        # Deveria detectar pelo menos RULE_001, RULE_004, RULE_007
        assert len(detected) >= 3, f"Deveria detectar múltiplas regras, detectou {len(detected)}"

    def test_no_false_positives_with_word_boundaries(self, matcher):
        """Não deve encontrar keywords dentro de palavras maiores."""
        # "prescricao" contém "criacao", mas não deveria ser um match
        user_story = "Criação de novo paciente no sistema"

        detected = matcher.match_rules(user_story)
        rule_ids = [r.rule_id for r in detected]

        # Não deveria detectar nenhuma regra baseada em "criacao"
        assert "RULE_007" not in rule_ids, "Falso positivo com word boundaries"
