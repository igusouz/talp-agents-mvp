"""
Serviço: File Loader - Carregar arquivos de dados
"""

import csv
import json
from pathlib import Path
from typing import Any, Optional


class FileLoader:
    """Carregar arquivos de dados (CSV, JSON, etc)."""

    @staticmethod
    def load_json(file_path: str) -> Optional[dict]:
        """
        Carregar arquivo JSON.

        Args:
            file_path: Caminho para o arquivo JSON

        Returns:
            Dicionário carregado ou None se erro

        Raises:
            FileNotFoundError: Se arquivo não existe
            json.JSONDecodeError: Se JSON é inválido
        """
        path = Path(file_path)

        if not path.exists():
            raise FileNotFoundError(f"Arquivo não encontrado: {file_path}")

        try:
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
            return data
        except json.JSONDecodeError as e:
            raise json.JSONDecodeError(
                f"Erro ao decodificar JSON em {file_path}: {e.msg}", e.doc, e.pos
            )

    @staticmethod
    def load_csv(file_path: str) -> list[dict]:
        """
        Carregar arquivo CSV.

        Args:
            file_path: Caminho para o arquivo CSV

        Returns:
            Lista de dicionários representando as linhas

        Raises:
            FileNotFoundError: Se arquivo não existe
            csv.Error: Se erro ao processar CSV
        """
        path = Path(file_path)

        if not path.exists():
            raise FileNotFoundError(f"Arquivo não encontrado: {file_path}")

        data = []
        try:
            with open(path, "r", encoding="utf-8") as f:
                reader = csv.DictReader(f)
                data = list(reader)
        except csv.Error as e:
            raise csv.Error(f"Erro ao processar CSV em {file_path}: {e}")

        return data

    @staticmethod
    def save_json(file_path: str, data: dict, pretty: bool = True) -> None:
        """
        Salvar dicionário como JSON.

        Args:
            file_path: Caminho para salvar o arquivo
            data: Dicionário a salvar
            pretty: Se True, formata com indentação

        Raises:
            IOError: Se erro ao salvar
        """
        path = Path(file_path)
        path.parent.mkdir(parents=True, exist_ok=True)

        try:
            with open(path, "w", encoding="utf-8") as f:
                if pretty:
                    json.dump(data, f, indent=2, ensure_ascii=False)
                else:
                    json.dump(data, f, ensure_ascii=False)
        except IOError as e:
            raise IOError(f"Erro ao salvar JSON em {file_path}: {e}")

    @staticmethod
    def load_file(file_path: str) -> Optional[Any]:
        """
        Carregar arquivo detectando tipo pela extensão.

        Args:
            file_path: Caminho do arquivo

        Returns:
            Conteúdo carregado ou None

        Raises:
            ValueError: Se tipo de arquivo não suportado
        """
        path = Path(file_path)

        if not path.exists():
            raise FileNotFoundError(f"Arquivo não encontrado: {file_path}")

        suffix = path.suffix.lower()

        if suffix == ".json":
            return FileLoader.load_json(file_path)
        elif suffix == ".csv":
            return FileLoader.load_csv(file_path)
        else:
            raise ValueError(f"Tipo de arquivo não suportado: {suffix}")
