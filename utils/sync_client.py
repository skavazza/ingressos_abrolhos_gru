"""
Cliente de sincronização para comunicação com o app servidor.
"""
from __future__ import annotations

from pathlib import Path
from typing import Any, Optional

import requests


class SyncClient:
    """Cliente HTTP para sincronização de preços, registros e documentos."""

    def __init__(self, base_url: str, timeout: int = 20) -> None:
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout

    def obter_tabela_preco(self) -> dict[str, Any]:
        """Obtém a tabela de preços ativa do servidor."""
        response = requests.get(
            f"{self.base_url}/precos/ativo",
            timeout=self.timeout,
        )
        response.raise_for_status()
        return response.json()

    def enviar_registro(self, payload: dict[str, Any]) -> dict[str, Any]:
        """Envia um registro de visita para o servidor."""
        response = requests.post(
            f"{self.base_url}/registros",
            json=payload,
            timeout=self.timeout,
        )
        response.raise_for_status()
        return response.json()

    def enviar_documento(
        self,
        empresa_id: int,
        tipo: str,
        arquivo_path: str | Path,
        registro_visita_id: Optional[int] = None,
    ) -> dict[str, Any]:
        """Envia um documento para auditoria."""
        arquivo_path = Path(arquivo_path)
        data = {
            "empresa_id": str(empresa_id),
            "tipo": tipo,
        }
        if registro_visita_id is not None:
            data["registro_visita_id"] = str(registro_visita_id)

        with arquivo_path.open("rb") as arquivo:
            files = {"arquivo": (arquivo_path.name, arquivo)}
            response = requests.post(
                f"{self.base_url}/documentos",
                data=data,
                files=files,
                timeout=self.timeout,
            )
        response.raise_for_status()
        return response.json()
