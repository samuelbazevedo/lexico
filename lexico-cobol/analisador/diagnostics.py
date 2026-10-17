"""Tratamento de erros do compilador (Seção 6 da especificação).

Níveis de severidade:
  I (Informational) - sugestões de estilo ou otimização
  W (Warning)       - potenciais ambiguidades; não impedem a compilação
  E (Error)         - erros sintáticos/semânticos graves; impedem a linkedição
  S (Severe)        - falha catastrófica no processo de compilação
"""

from dataclasses import dataclass, field
from typing import List, Optional

SEVERIDADES = {"I": 0, "W": 4, "E": 8, "S": 12}
NOMES = {"I": "INFORMATIONAL", "W": "WARNING", "E": "ERROR", "S": "SEVERE"}


@dataclass
class Posicao:
    arquivo: str
    linha: int
    coluna: int

    def __str__(self):
        return f"{self.arquivo}:{self.linha}:{self.coluna}"


@dataclass
class Diagnostico:
    severidade: str          # 'I', 'W', 'E' ou 'S'
    codigo: str              # ex.: LEX-002, SIN-010, SEM-001
    mensagem: str
    pos: Optional[Posicao] = None

    def __str__(self):
        onde = f"{self.pos}: " if self.pos else ""
        return f"{onde}{self.severidade} [{self.codigo}] {self.mensagem}"


class FalhaSevera(Exception):
    """Levantada para abortar a compilação imediatamente (nível S)."""


@dataclass
class Relatorio:
    itens: List[Diagnostico] = field(default_factory=list)

    def add(self, sev, codigo, msg, pos=None):
        d = Diagnostico(sev, codigo, msg, pos)
        self.itens.append(d)
        if sev == "S":
            raise FalhaSevera(str(d))
        return d

    def info(self, codigo, msg, pos=None):
        return self.add("I", codigo, msg, pos)

    def aviso(self, codigo, msg, pos=None):
        return self.add("W", codigo, msg, pos)

    def erro(self, codigo, msg, pos=None):
        return self.add("E", codigo, msg, pos)

    def severo(self, codigo, msg, pos=None):
        return self.add("S", codigo, msg, pos)

    def conta(self, sev):
        return sum(1 for d in self.itens if d.severidade == sev)

    @property
    def tem_erro(self):
        return any(d.severidade in ("E", "S") for d in self.itens)

    @property
    def codigo_retorno(self):
        """Return code no estilo IBM: 0, 4 (W), 8 (E), 12 (S)."""
        return max((SEVERIDADES[d.severidade] for d in self.itens), default=0)

    def ordenados(self):
        def chave(d):
            if d.pos is None:
                return ("", 0, 0)
            return (d.pos.arquivo, d.pos.linha, d.pos.coluna)
        return sorted(self.itens, key=chave)

    def resumo(self):
        return ("I={} W={} E={} S={}  (RC={})".format(
            self.conta("I"), self.conta("W"), self.conta("E"),
            self.conta("S"), self.codigo_retorno))
