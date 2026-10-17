"""Testes automatizados do analisador léxico.

Executar a partir da pasta do projeto:
    python -m unittest discover -s testes -v
"""

import os
import sys
import unittest

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, RAIZ)

from analisador.diagnostics import Relatorio                                 # noqa: E402
from analisador.lexer import Lexer, PALAVRA_CHAVE, IDENT, NUM, ALFA, PIC, PONTO  # noqa: E402

EXEMPLOS = os.path.join(RAIZ, "exemplos")
PROFESSOR = os.path.join(RAIZ, "exemplos-professor")


def fixo(texto):
    """Converte linhas 'livres' em formato fixo: 6 colunas de sequência +
    indicador.  Linhas iniciadas por '*', '/', '-' ou 'D|' usam esse indicador."""
    out = []
    for n, l in enumerate(texto.strip("\n").split("\n"), start=1):
        seq = f"{n:06d}"
        if l.startswith("*") or l.startswith("/"):
            out.append(seq + l[0] + l[1:])
        elif l.startswith("-"):
            out.append(seq + "-" + l[1:])
        elif l.startswith("D|"):
            out.append(seq + "D" + l[2:])
        else:
            out.append(seq + " " + l)
    return "\n".join(out) + "\n"


def tokens(texto, debug=False):
    rel = Relatorio()
    toks = Lexer(rel, debug=debug).tokenizar_texto(fixo(texto), "teste.cbl")
    return toks, rel


class TestLexico(unittest.TestCase):
    def test_colunas_sequencia_e_identificacao_ignoradas(self):
        linha = "123456 DISPLAY 'A'.".ljust(72) + "XXXXXXXX"
        rel = Relatorio()
        toks = Lexer(rel).tokenizar_texto(linha + "\n", "t.cbl")
        self.assertEqual([t.valor for t in toks], ["DISPLAY", "A", "."])
        self.assertEqual(toks[0].pos.coluna, 8)

    def test_comentarios(self):
        toks, _ = tokens("* comentario\n/ outro\n DISPLAY 'X'.")
        self.assertEqual([t.valor for t in toks], ["DISPLAY", "X", "."])

    def test_linha_de_depuracao(self):
        toks, _ = tokens("D|    DISPLAY 'DBG'.")
        self.assertEqual(toks, [])
        toks, _ = tokens("D|    DISPLAY 'DBG'.", debug=True)
        self.assertEqual(len(toks), 3)

    def test_area_a_e_b(self):
        toks, _ = tokens("PROCEDURE DIVISION.\n    DISPLAY 'X'.")
        self.assertEqual(toks[0].area, "A")
        self.assertEqual(toks[3].area, "B")

    def test_categorias(self):
        toks, _ = tokens("    MOVE -123.45 TO WS-X OF GRP. 05 A PIC S9(3)V99.")
        tipos = [(t.tipo, t.valor) for t in toks]
        self.assertIn((PALAVRA_CHAVE, "MOVE"), tipos)
        self.assertIn((NUM, "-123.45"), tipos)
        self.assertIn((IDENT, "WS-X"), tipos)
        self.assertIn((PIC, "S9(3)V99"), tipos)
        self.assertEqual(tipos[-1], (PONTO, "."))

    def test_literais_aspas_simples_e_duplas(self):
        toks, _ = tokens('    DISPLAY \'D\'\'AGUA\' "DIZ ""OI""".')
        self.assertEqual([t.valor for t in toks if t.tipo == ALFA], ["D'AGUA", 'DIZ "OI"'])

    def test_continuacao_de_literal(self):
        l1 = '    DISPLAY "ABC'.ljust(65)
        texto = l1 + '\n-    "DEF".'
        toks, rel = tokens(texto)
        lit = [t for t in toks if t.tipo == ALFA][0].valor
        self.assertTrue(lit.startswith("ABC") and lit.endswith("DEF"))
        self.assertEqual(len(lit), 65 - len('    DISPLAY "') + 3)
        self.assertFalse(rel.tem_erro)

    def test_literal_nao_terminado(self):
        _, rel = tokens("    DISPLAY 'ABC")
        self.assertIn("LEX-007", [d.codigo for d in rel.itens])

    def test_identificador_invalido(self):
        _, rel = tokens("    MOVE 1 TO ABC-. MOVE 1 TO " + "A" * 31 + ".")
        cods = [d.codigo for d in rel.itens]
        self.assertIn("LEX-015", cods)
        self.assertIn("LEX-014", cods)

    def test_identificador_comecando_com_digito(self):
        toks, rel = tokens("    PERFORM 100-INICIO.")
        self.assertEqual(toks[1].tipo, IDENT)
        self.assertFalse(rel.tem_erro)

    def test_continuacao_de_palavra(self):
        l1 = "    MOVE 1 TO".ljust(64) + "T"    # T termina na coluna 72
        toks, rel = tokens(l1 + "\n-   AB-X.")
        self.assertEqual(toks[3].valor, "TAB-X")
        self.assertFalse(rel.tem_erro)

    def test_sublinhado_aceito_com_aviso(self):
        toks, rel = tokens("    DISPLAY PROG_01.")
        self.assertEqual(toks[1].valor, "PROG_01")
        self.assertIn("LEX-017", [d.codigo for d in rel.itens])
        self.assertFalse(rel.tem_erro)

    def test_caractere_invalido(self):
        _, rel = tokens("    DISPLAY @.")
        self.assertIn("LEX-012", [d.codigo for d in rel.itens])

    def test_formato_livre_rejeitado(self):
        rel = Relatorio()
        Lexer(rel).tokenizar_texto("IDENTIFICATION DIVISION.\n", "t.cbl")
        self.assertIn("LEX-003", [d.codigo for d in rel.itens])


class TestArquivosDeExemplo(unittest.TestCase):
    def lexa(self, caminho):
        rel = Relatorio()
        toks = Lexer(rel).tokenizar_arquivo(caminho)
        return toks, rel

    def test_programas_do_professor_sem_erro_lexico(self):
        for nome in sorted(os.listdir(PROFESSOR)):
            if nome.endswith(".cob"):
                with self.subTest(nome=nome):
                    toks, rel = self.lexa(os.path.join(PROFESSOR, nome))
                    self.assertFalse(rel.tem_erro, "\n".join(map(str, rel.itens)))
                    self.assertGreater(len(toks), 10)

    def test_copy_insere_tokens_do_copybook(self):
        toks, rel = self.lexa(os.path.join(EXEMPLOS, "copia.cbl"))
        self.assertFalse(rel.tem_erro)
        nomes = [t.valor for t in toks]
        self.assertIn("CLI-CODIGO", nomes)
        self.assertNotIn("COPY", nomes)
        self.assertTrue(any(t.pos.arquivo.endswith("CLIENTE.cpy") for t in toks))

    def test_erros_lexicos(self):
        _, rel = self.lexa(os.path.join(EXEMPLOS, "erros_lexicos.cbl"))
        cods = {d.codigo for d in rel.itens}
        for c in ("LEX-003", "LEX-007", "LEX-012", "LEX-013", "LEX-014", "LEX-015", "LEX-023"):
            self.assertIn(c, cods)


if __name__ == "__main__":
    unittest.main()
