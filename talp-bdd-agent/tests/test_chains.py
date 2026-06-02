"""Test LangChain workflows with mocked LLM."""

from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest

from app.chains.qa_chain import QAAnalysisChain
from app.core.config import Settings
from app.schemas.qa import QARequest, QAAnalysisResponse


class TestQAAnalysisChain:
    """Test the BDD QA analysis workflow."""

    @pytest.fixture
    def mock_settings(self) -> Settings:
        """Provide test settings."""
        return Settings(
            llm_model="gpt-4o-mini",
            llm_api_key="test-key",
            llm_base_url="https://api.example.com",
            llm_temperature=0.0,
        )

    def test_chain_initialization(self, mock_settings: Settings) -> None:
        """Chain initializes with correct settings."""
        chain = QAAnalysisChain(settings=mock_settings)
        assert chain.settings.llm_model == "gpt-4o-mini"
        assert chain.settings.llm_temperature == 0.0

    @patch("app.chains.qa_chain.ChatOpenAI")
    def test_chain_invoke_with_mock_llm(
        self,
        mock_llm_class: MagicMock,
        mock_settings: Settings,
        mock_qa_response: QAAnalysisResponse,
    ) -> None:
        """Chain invokes LLM and returns structured response."""
        # Setup mock LLM
        mock_llm = MagicMock()
        mock_llm.with_structured_output.return_value = MagicMock()
        mock_llm_class.return_value = mock_llm

        # Setup chain to return mock response
        mock_chain = MagicMock()
        mock_chain.invoke.return_value = mock_qa_response

        with patch("app.chains.qa_chain.ChatPromptTemplate") as mock_prompt:
            mock_prompt.from_messages.return_value = MagicMock()

            # Manually set chain for this test
            chain = QAAnalysisChain(settings=mock_settings)
            chain._chain = mock_chain

            # Invoke chain
            request = QARequest(story="As a user, I want to reset my password")
            response = chain.invoke(request)

            # Verify response structure
            assert isinstance(response, QAAnalysisResponse)
            assert response.summary
            assert len(response.bdd_scenarios) > 0

    def test_format_acceptance_criteria_empty(self) -> None:
        """Empty criteria list returns default message."""
        from app.chains.qa_chain import _format_acceptance_criteria

        result = _format_acceptance_criteria([])
        assert result == "No acceptance criteria provided."

    def test_format_acceptance_criteria_with_items(self) -> None:
        """Criteria are formatted as bullet points."""
        from app.chains.qa_chain import _format_acceptance_criteria

        criteria = ["Email is sent", "Link expires in 30 minutes"]
        result = _format_acceptance_criteria(criteria)
        assert "- Email is sent" in result
        assert "- Link expires in 30 minutes" in result

    def test_load_prompt_file_exists(self) -> None:
        """Prompt files can be loaded from disk."""
        from app.chains.qa_chain import _load_prompt

        # Versioned system prompt should exist
        content = _load_prompt("system/qa.md")
        assert len(content) > 0
        assert "QA" in content or "analysis" in content.lower()

    def test_load_prompt_file_not_found(self) -> None:
        """Loading non-existent prompt raises FileNotFoundError."""
        from app.chains.qa_chain import _load_prompt

        with pytest.raises(FileNotFoundError):
            _load_prompt("nonexistent.md")
