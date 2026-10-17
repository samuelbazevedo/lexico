"""Análise Léxica (Seção 2 da especificação).

Converte o fluxo de caracteres do fonte COBOL (formato fixo de colunas) em
um fluxo de tokens. Também trata a diretiva COPY (Seção 6), que interrompe a
leitura do arquivo atual para incluir textualmente um copybook.

Layout da linha (2.1):
  colunas 1-6   : área de sequência  -> ignorada
  coluna  7     : indicador  ('*' ou '/' comentário, '-' continuação,
                               'D' linha de depuração)
  colunas 8-11  : Área A  (divisões, seções, parágrafos, níveis 01/77, FD)
  colunas 12-72 : Área B  (comandos, cláusulas, níveis subordinados)
  colunas 73-80 : área de identificação do programa -> desprezada
"""

import os
import re
from dataclasses import dataclass

from .diagnostics import Posicao

# ---------------------------------------------------------------------------
# Categorias de token (2.2)
# ---------------------------------------------------------------------------
PALAVRA_CHAVE = "PALAVRA_CHAVE"
IDENT = "IDENT"            # palavra definida pelo usuário
NUM = "NUM"                # literal numérico
ALFA = "ALFA"              # literal alfanumérico
PIC = "PIC"                # cadeia de PICTURE (ex.: 9(5)V99)
PONTO = "PONTO"            # '.'  terminador de sentença/parágrafo
VIRGULA = "VIRGULA"        # ','  separador
PONTO_VIRGULA = "PONTO_VIRGULA"  # ';' separador
ABRE = "ABRE"              # '('
FECHA = "FECHA"            # ')'
OP = "OP"                  # + - * / ** = > < >= <=
EOF = "EOF"

# Palavras reservadas exigidas pela especificação ...
RESERVADAS_ESPEC = {
    "IDENTIFICATION", "ENVIRONMENT", "DATA", "PROCEDURE", "DIVISION",
    "SECTION", "DISPLAY", "ACCEPT", "PERFORM", "STOP", "RUN", "IF", "ELSE",
    "MOVE",
}
# ... e as demais palavras necessárias para a gramática das Seções 3 e 4.
RESERVADAS = RESERVADAS_ESPEC | {
    "PROGRAM-ID", "AUTHOR", "INSTALLATION", "DATE-WRITTEN", "DATE-COMPILED",
    "SECURITY", "REMARKS", "CONFIGURATION", "SOURCE-COMPUTER",
    "OBJECT-COMPUTER", "SPECIAL-NAMES", "INPUT-OUTPUT", "FILE-CONTROL",
    "SELECT", "ASSIGN", "TO", "ORGANIZATION", "ACCESS", "MODE", "SEQUENTIAL",
    "LINE", "FILE", "STATUS", "IS", "ARE", "FD", "WORKING-STORAGE", "PIC",
    "PICTURE", "VALUE", "VALUES", "THRU", "THROUGH", "ZERO", "ZEROS",
    "ZEROES", "SPACE", "SPACES", "FILLER", "THEN", "END-IF", "ADD",
    "SUBTRACT", "MULTIPLY", "DIVIDE", "COMPUTE", "GIVING", "BY", "FROM",
    "INTO", "REMAINDER", "ROUNDED", "UNTIL", "TIMES", "VARYING",
    "END-PERFORM", "WITH", "TEST", "BEFORE", "AFTER", "NO", "ADVANCING",
    "UPON", "NOT", "AND", "OR", "EQUAL", "GREATER", "LESS", "THAN", "OPEN",
    "CLOSE", "READ", "WRITE", "INPUT", "OUTPUT", "EXTEND", "AT", "END",
    "END-READ", "GO", "OF", "IN", "COPY", "REPLACING", "RECORD", "EXIT",
    "CONTINUE", "SET", "TRUE", "NUMERIC", "ALPHABETIC", "POSITIVE",
    "NEGATIVE", "DEBUGGING", "PROGRAM", "GOBACK", "NEXT", "SENTENCE",
    "END-ADD", "END-SUBTRACT", "END-MULTIPLY", "END-DIVIDE", "END-COMPUTE",
    "OPTIONAL", "USING",
}

# Parágrafos da IDENTIFICATION DIVISION cujo conteúdo é "comment-entry"
PARAGRAFOS_COMENTARIO = {"AUTHOR", "INSTALLATION", "DATE-WRITTEN",
                         "DATE-COMPILED", "SECURITY", "REMARKS"}

MAX_IDENT = 30
MAX_DIGITOS = 18
MAX_LITERAL = 160

_CHARS_PALAVRA = set("ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789-_")
_EXTENSOES_COPY = ["", ".cpy", ".CPY", ".cbl", ".CBL", ".cob", ".COB"]


@dataclass
class Token:
    tipo: str
    valor: str          # valor normalizado (palavras em maiúsculas)
    texto: str          # texto original
    pos: Posicao
    area: str = "B"     # 'A' se começa nas colunas 8-11, senão 'B'

    def __repr__(self):
        return f"{self.tipo}({self.valor!r})@{self.pos.linha}:{self.pos.coluna}"

    def eh(self, *valores):
        return self.tipo == PALAVRA_CHAVE and self.valor in valores


class Lexer:
    def __init__(self, relatorio, dirs_copy=None, debug=False):
        self.rel = relatorio
        self.dirs_copy = list(dirs_copy or [])
        self.debug_forcado = debug
        self.pilha_copy = []      # arquivos em processo de inclusão
        self._avisou_formato = False

    # ------------------------------------------------------------------
    # Ponto de entrada
    # ------------------------------------------------------------------
    def tokenizar_arquivo(self, caminho):
        try:
            with open(caminho, "r", encoding="utf-8", errors="replace") as f:
                texto = f.read()
        except OSError as e:
            self.rel.severo("LEX-000", f"não foi possível ler '{caminho}': {e}")
        toks = self.tokenizar_texto(texto, caminho)
        toks.append(Token(EOF, "", "", Posicao(caminho, texto.count("\n") + 1, 1)))
        return toks

    def tokenizar_texto(self, texto, arquivo):
        self.pilha_copy.append(os.path.abspath(arquivo))
        try:
            toks = self._linhas_para_tokens(texto, arquivo)
            return self._expandir_copy(toks, arquivo)
        finally:
            self.pilha_copy.pop()

    # ------------------------------------------------------------------
    # Leitura em colunas (formato fixo)
    # ------------------------------------------------------------------
    def _linhas_para_tokens(self, texto, arquivo):
        linhas = texto.split("\n")
        if linhas and linhas[-1] == "":
            linhas.pop()
        debug = self.debug_forcado or self._detecta_debugging_mode(linhas)

        toks = []
        literal_pendente = None   # [delim, partes, pos_inicial] quando um literal cruza a coluna 72
        em_comment_entry = False
        avisou_tab = False

        for nlinha, bruta in enumerate(linhas, start=1):
            bruta = bruta.rstrip("\r")
            if "\t" in bruta:
                if not avisou_tab:
                    self.rel.aviso("LEX-001", "tabulação encontrada; expandida para "
                                   "espaços (tab stop = 8)", Posicao(arquivo, nlinha, 1))
                    avisou_tab = True
                bruta = bruta.expandtabs(8)
            if len(bruta) < 7:
                if literal_pendente is None and bruta.strip() and not bruta[:6].strip().isdigit():
                    self.rel.aviso("LEX-002", "linha com menos de 7 colunas; conteúdo "
                                   "fora da Área A/B ignorado", Posicao(arquivo, nlinha, 1))
                continue

            indicador = bruta[6]
            conteudo = bruta[7:72].ljust(65)   # colunas 8-72
            area_a = conteudo[:4]

            if indicador in "*/":
                continue                        # linha de comentário
            if indicador in "Dd":
                if not debug:
                    continue                    # linha de depuração desativada
                indicador = " "
            if indicador not in " -":
                dica = ("" if self._avisou_formato else
                        " (o fonte deve estar em formato fixo: colunas 1-6 = sequência, "
                        "7 = indicador, código a partir da coluna 8)")
                self._avisou_formato = True
                self.rel.erro("LEX-003", f"indicador inválido '{indicador}' na coluna 7{dica}",
                              Posicao(arquivo, nlinha, 7))
                indicador = " "

            continuacao = indicador == "-"

            # literal aberto na linha anterior sem continuação -> erro
            if literal_pendente is not None and not continuacao:
                self._fecha_literal_nao_terminado(toks, literal_pendente)
                literal_pendente = None

            # comment-entry (AUTHOR. Fulano ...) vai até a próxima palavra na Área A
            if em_comment_entry:
                if area_a.strip() == "" and not continuacao:
                    continue
                em_comment_entry = False

            if not conteudo.strip():
                continue

            inicio = 0
            if continuacao:
                if literal_pendente is not None:
                    inicio = self._continua_literal(conteudo, arquivo, nlinha,
                                                    literal_pendente, toks)
                    if inicio is None:      # literal ainda continua na próxima linha
                        continue
                    literal_pendente = None
                else:
                    if area_a.strip():
                        self.rel.aviso("LEX-005", "Área A deve estar em branco em "
                                       "linha de continuação", Posicao(arquivo, nlinha, 8))
                    if self._continua_palavra(conteudo, arquivo, nlinha, toks):
                        continue
                    self.rel.aviso("LEX-004", "linha de continuação sem literal "
                                   "pendente; tratada como linha normal",
                                   Posicao(arquivo, nlinha, 7))

            # Detecta início de comment-entry
            primeira = conteudo.strip().split(" ")[0].upper().rstrip(".")
            if (not continuacao and area_a.strip() and primeira in PARAGRAFOS_COMENTARIO):
                col = conteudo.index(conteudo.strip()[0]) + 8
                p = Posicao(arquivo, nlinha, col)
                toks.append(Token(PALAVRA_CHAVE, primeira, primeira, p, "A"))
                toks.append(Token(PONTO, ".", ".", Posicao(arquivo, nlinha, col + len(primeira)), "B"))
                self.rel.info("LEX-006", f"parágrafo {primeira} é obsoleto; tratado "
                              "como comentário", p)
                em_comment_entry = True
                continue

            literal_pendente = self._lexar_linha(conteudo, inicio, arquivo, nlinha, toks)

        if literal_pendente is not None:
            self._fecha_literal_nao_terminado(toks, literal_pendente)
        return toks

    def _continua_palavra(self, conteudo, arquivo, nlinha, toks):
        """Continuação de palavra: se a linha anterior terminou uma palavra
        exatamente na coluna 72, o primeiro trecho desta linha é colado a ela
        (ex.: '... TO T' na col. 72  +  '-AB-TRABALHADOR.' -> TAB-TRABALHADOR)."""
        if not toks:
            return False
        ant = toks[-1]
        if ant.tipo not in (IDENT, PALAVRA_CHAVE, NUM):
            return False
        if ant.pos.coluna + len(ant.texto) - 1 != 72 or ant.pos.arquivo != arquivo:
            return False
        if ant.pos.linha >= nlinha:
            return False
        i = 0
        while i < len(conteudo) and conteudo[i] == " ":
            i += 1
        j = i
        while j < len(conteudo) and conteudo[j] in _CHARS_PALAVRA:
            j += 1
        if j == i:
            return False
        toks.pop()
        self._emite_palavra(ant.texto + conteudo[i:j], ant.pos, ant.area, toks)
        resto = self._lexar_linha(conteudo, j, arquivo, nlinha, toks)
        if resto is not None:
            self._fecha_literal_nao_terminado(toks, resto)
        return True

    @staticmethod
    def _detecta_debugging_mode(linhas):
        txt = []
        for l in linhas:
            if len(l) > 7 and l[6] not in "*/Dd":
                txt.append(l[7:72].upper())
        return re.search(r"WITH\s+DEBUGGING\s+MODE", " ".join(txt)) is not None

    def _fecha_literal_nao_terminado(self, toks, pendente):
        delim, partes, pos = pendente
        self.rel.erro("LEX-007", "literal alfanumérico não terminado "
                      "(faltou aspas de fechamento ou linha de continuação '-')", pos)
        valor = "".join(partes).rstrip()
        toks.append(Token(ALFA, valor, delim + valor + delim, pos))

    def _continua_literal(self, conteudo, arquivo, nlinha, pendente, toks):
        """Continuação de literal (indicador '-'): o literal anterior vai até a
        coluna 72 e prossegue após a primeira aspa da linha de continuação."""
        delim, partes, pos = pendente
        i = 0
        while i < len(conteudo) and conteudo[i] == " ":
            i += 1
        if i < 4:
            self.rel.aviso("LEX-005", "continuação deve começar na Área B",
                           Posicao(arquivo, nlinha, i + 8))
        if i >= len(conteudo) or conteudo[i] not in "'\"":
            self.rel.erro("LEX-008", "linha de continuação de literal deve começar "
                          "com aspas", Posicao(arquivo, nlinha, i + 8))
            self._fecha_literal_nao_terminado(toks, pendente)
            return i
        i += 1
        fim, texto = self._varre_literal(conteudo, i, delim)
        partes.append(texto)
        if fim is None:
            return None             # continua aberto
        valor = "".join(partes)
        self._emite_alfa(toks, valor, delim, pos)
        return fim

    @staticmethod
    def _varre_literal(conteudo, i, delim):
        """Lê até o delimitador (aspas duplicadas = aspas literais).
        Retorna (posição após o fechamento | None, texto)."""
        buf = []
        while i < len(conteudo):
            c = conteudo[i]
            if c == delim:
                if i + 1 < len(conteudo) and conteudo[i + 1] == delim:
                    buf.append(delim)
                    i += 2
                    continue
                return i + 1, "".join(buf)
            buf.append(c)
            i += 1
        return None, "".join(buf)

    def _emite_alfa(self, toks, valor, delim, pos):
        if len(valor) > MAX_LITERAL:
            self.rel.aviso("LEX-009", f"literal alfanumérico com {len(valor)} "
                           f"caracteres excede o limite de {MAX_LITERAL}", pos)
        if valor == "":
            self.rel.aviso("LEX-010", "literal alfanumérico vazio", pos)
        toks.append(Token(ALFA, valor, delim + valor + delim, pos))

    # ------------------------------------------------------------------
    # Varredura de uma linha (colunas 8-72)
    # ------------------------------------------------------------------
    def _lexar_linha(self, s, i, arquivo, nlinha, toks):
        n = len(s)
        while i < n:
            c = s[i]
            col = i + 8
            pos = Posicao(arquivo, nlinha, col)
            area = "A" if col <= 11 else "B"

            if c == " ":
                i += 1
                continue

            # Literal alfanumérico
            if c in "'\"":
                fim, texto = self._varre_literal(s, i + 1, c)
                if fim is None:
                    return [c, [texto], pos]   # pode continuar na próxima linha
                self._emite_alfa(toks, texto, c, pos)
                toks[-1].area = area
                i = fim
                continue

            # PICTURE: a próxima "palavra" após PIC [IS] é a cadeia de picture
            if self._espera_picture(toks):
                j = i
                while j < n and s[j] != " ":
                    j += 1
                pic = s[i:j]
                ponto_final = False
                if pic.endswith(".") or pic.endswith(","):
                    ponto_final = pic[-1]
                    pic = pic[:-1]
                toks.append(Token(PIC, pic.upper(), pic, pos, area))
                if ponto_final:
                    tipo = PONTO if ponto_final == "." else VIRGULA
                    toks.append(Token(tipo, ponto_final, ponto_final,
                                      Posicao(arquivo, nlinha, j - 1 + 8)))
                i = j
                continue

            # Literal numérico com sinal: +12 / -3.5
            if c in "+-" and i + 1 < n and (s[i + 1].isdigit() or
                                            (s[i + 1] == "." and i + 2 < n and s[i + 2].isdigit())):
                # Em COBOL operadores aritméticos exigem espaços em volta,
                # portanto '-1' colado é sempre literal com sinal.
                i = self._lexar_numero(s, i, pos, area, toks)
                continue

            # Literal numérico iniciado por ponto decimal: .5
            if c == "." and i + 1 < n and s[i + 1].isdigit():
                i = self._lexar_numero(s, i, pos, area, toks)
                continue

            # Palavras (palavras-chave, identificadores) e números sem sinal
            if c in _CHARS_PALAVRA and c not in "-_":
                j = i
                while j < n and s[j] in _CHARS_PALAVRA:
                    j += 1
                palavra = s[i:j]
                if palavra.isdigit():
                    i = self._lexar_numero(s, i, pos, area, toks)
                    continue
                i = j
                self._emite_palavra(palavra, pos, area, toks)
                continue

            # Ponto final
            if c == ".":
                toks.append(Token(PONTO, ".", ".", pos, area))
                if i + 1 < n and s[i + 1] != " ":
                    self.rel.aviso("LEX-011", "ponto final deve ser seguido de espaço", pos)
                i += 1
                continue
            if c == ",":
                toks.append(Token(VIRGULA, ",", ",", pos, area))
                i += 1
                continue
            if c == ";":
                toks.append(Token(PONTO_VIRGULA, ";", ";", pos, area))
                i += 1
                continue
            if c == "(":
                toks.append(Token(ABRE, "(", "(", pos, area))
                i += 1
                continue
            if c == ")":
                toks.append(Token(FECHA, ")", ")", pos, area))
                i += 1
                continue

            # Operadores
            dois = s[i:i + 2]
            if dois in ("**", ">=", "<="):
                toks.append(Token(OP, dois, dois, pos, area))
                i += 2
                continue
            if c in "+-*/=><":
                toks.append(Token(OP, c, c, pos, area))
                i += 1
                continue

            self.rel.erro("LEX-012", f"caractere inválido '{c}'", pos)
            i += 1
        return None

    @staticmethod
    def _espera_picture(toks):
        if not toks:
            return False
        t = toks[-1]
        if t.eh("PIC", "PICTURE"):
            return True
        return (t.eh("IS") and len(toks) >= 2 and toks[-2].eh("PIC", "PICTURE"))

    def _lexar_numero(self, s, i, pos, area, toks):
        j = i
        if s[j] in "+-":
            j += 1
        while j < len(s) and s[j].isdigit():
            j += 1
        if j + 1 < len(s) and s[j] == "." and s[j + 1].isdigit():
            j += 1
            while j < len(s) and s[j].isdigit():
                j += 1
        texto = s[i:j]
        # número imediatamente seguido de letra -> palavra iniciada por dígito
        if j < len(s) and s[j] in _CHARS_PALAVRA and texto.isdigit():
            k = j
            while k < len(s) and s[k] in _CHARS_PALAVRA:
                k += 1
            self._emite_palavra(s[i:k], pos, area, toks)
            return k
        digitos = sum(ch.isdigit() for ch in texto)
        if digitos > MAX_DIGITOS:
            self.rel.erro("LEX-013", f"literal numérico com {digitos} dígitos excede "
                          f"o máximo de {MAX_DIGITOS}", pos)
        toks.append(Token(NUM, texto.lstrip("+") if texto.startswith("+") else texto,
                          texto, pos, area))
        return j

    def _emite_palavra(self, palavra, pos, area, toks):
        up = palavra.upper()
        if up in RESERVADAS:
            toks.append(Token(PALAVRA_CHAVE, up, palavra, pos, area))
            return
        # Identificador (User-Defined Word): A-Z, 0-9, hífen; até 30 caracteres;
        # não pode iniciar nem terminar com hífen; deve conter ao menos uma letra.
        if len(up) > MAX_IDENT:
            self.rel.erro("LEX-014", f"identificador '{palavra}' tem {len(up)} "
                          f"caracteres (máximo {MAX_IDENT})", pos)
        if up.startswith("-") or up.endswith("-"):
            self.rel.erro("LEX-015", f"identificador '{palavra}' não pode iniciar "
                          "nem terminar com hífen", pos)
        if "_" in up:
            self.rel.aviso("LEX-017", f"identificador '{palavra}' usa sublinhado '_', que "
                           "não pertence ao padrão (A-Z, 0-9, hífen); aceito como extensão "
                           "do GnuCOBOL", pos)
        if not any(ch.isalpha() for ch in up):
            self.rel.erro("LEX-016", f"identificador '{palavra}' deve conter ao "
                          "menos uma letra", pos)
        toks.append(Token(IDENT, up, palavra, pos, area))

    # ------------------------------------------------------------------
    # Diretiva COPY (copybooks)
    # ------------------------------------------------------------------
    def _expandir_copy(self, toks, arquivo):
        saida = []
        i = 0
        while i < len(toks):
            t = toks[i]
            if not t.eh("COPY"):
                saida.append(t)
                i += 1
                continue
            # COPY nome [OF|IN biblioteca] .
            i += 1
            if i >= len(toks) or toks[i].tipo not in (IDENT, ALFA, PALAVRA_CHAVE):
                self.rel.erro("LEX-020", "nome do copybook esperado após COPY", t.pos)
                continue
            nome = toks[i].valor
            i += 1
            if i < len(toks) and toks[i].eh("OF", "IN"):
                i += 2
            if i < len(toks) and toks[i].eh("REPLACING"):
                self.rel.erro("LEX-021", "COPY ... REPLACING não é suportado", toks[i].pos)
                while i < len(toks) and toks[i].tipo != PONTO:
                    i += 1
            if i < len(toks) and toks[i].tipo == PONTO:
                i += 1
            else:
                self.rel.erro("LEX-022", "diretiva COPY deve terminar com ponto", t.pos)

            caminho = self._localiza_copybook(nome, arquivo)
            if caminho is None:
                self.rel.erro("LEX-023", f"copybook '{nome}' não encontrado "
                              f"(procurado em: {', '.join(self._dirs_busca(arquivo))})", t.pos)
                continue
            absol = os.path.abspath(caminho)
            if absol in self.pilha_copy:
                self.rel.severo("LEX-024", f"inclusão recursiva do copybook '{nome}' "
                                f"({' -> '.join(os.path.basename(p) for p in self.pilha_copy)})",
                                t.pos)
            if len(self.pilha_copy) > 16:
                self.rel.severo("LEX-025", "aninhamento de COPY excede 16 níveis", t.pos)
            try:
                with open(caminho, "r", encoding="utf-8", errors="replace") as f:
                    texto = f.read()
            except OSError as e:
                self.rel.severo("LEX-026", f"falha ao ler copybook '{caminho}': {e}", t.pos)
            saida.extend(self.tokenizar_texto(texto, caminho))
        return saida

    def _dirs_busca(self, arquivo):
        base = os.path.dirname(os.path.abspath(arquivo))
        dirs = [base, os.path.join(base, "copybooks")] + self.dirs_copy
        return dirs

    def _localiza_copybook(self, nome, arquivo):
        for d in self._dirs_busca(arquivo):
            for ext in _EXTENSOES_COPY:
                for variante in (nome, nome.lower(), nome.upper()):
                    p = os.path.join(d, variante + ext)
                    if os.path.isfile(p):
                        return p
        return None
