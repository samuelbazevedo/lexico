#!/usr/bin/env python3
"""Executa SOMENTE o analisador léxico (Seção 2) e mostra a saída em tokens.

Uso:
    python lexico.py programa.cob              # um arquivo
    python lexico.py pasta-com-programas       # todos os .cob/.cbl da pasta
    python lexico.py programa.cob -D           # ativa linhas de depuração 'D'
    python lexico.py programa.cob -I copybooks # pasta extra de copybooks

Para cada fonte é impresso:
  1. a tabela de tokens  (linha:coluna, área A/B, categoria, texto)
  2. um resumo com a quantidade de tokens por categoria
  3. os diagnósticos do léxico (níveis I / W / E / S)
e é gravado um arquivo  <fonte>.tokens.txt  ao lado do fonte com a mesma tabela.
"""

import argparse
import collections
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from analisador.diagnostics import Relatorio, FalhaSevera   # noqa: E402
from analisador.lexer import Lexer                          # noqa: E402

EXTENSOES = (".cob", ".cbl", ".cobol", ".cpy")


def lista_fontes(caminhos):
    for c in caminhos:
        if os.path.isdir(c):
            for nome in sorted(os.listdir(c)):
                if nome.lower().endswith(EXTENSOES[:3]):
                    yield os.path.join(c, nome)
        else:
            yield c


def tabela(tokens):
    linhas = [f"{'LINHA:COL':<10} {'ÁREA':<4}  {'CATEGORIA':<14} TEXTO",
              "-" * 60]
    for t in tokens:
        arq = "" if t.pos.arquivo == tokens[-1].pos.arquivo else \
            f"   [{os.path.basename(t.pos.arquivo)}]"      # token vindo de copybook
        linhas.append(f"{t.pos.linha:>5}:{t.pos.coluna:<4} {t.area:<4}  {t.tipo:<14} "
                      f"{t.texto}{arq}")
    return "\n".join(linhas)


def analisa(fonte, args):
    rel = Relatorio()
    tokens = []
    try:
        tokens = Lexer(rel, dirs_copy=args.dirs, debug=args.debug).tokenizar_arquivo(fonte)
    except FalhaSevera:
        pass

    print("=" * 70)
    print(f"ARQUIVO: {fonte}")
    print("=" * 70)
    if tokens:
        tab = tabela(tokens)
        print(tab)
        if not args.nao_gravar:
            destino = fonte + ".tokens.txt"
            with open(destino, "w", encoding="utf-8") as f:
                f.write(tab + "\n")
        cont = collections.Counter(t.tipo for t in tokens if t.tipo != "EOF")
        print("\nRESUMO POR CATEGORIA:")
        for tipo, n in cont.most_common():
            print(f"  {tipo:<14} {n:>5}")
        print(f"  {'TOTAL':<14} {sum(cont.values()):>5}")

    print("\nDIAGNÓSTICOS DO LÉXICO:")
    if not rel.itens:
        print("  nenhum")
    for d in rel.ordenados():
        print("  " + str(d))
    print(f"\nRESULTADO: {'ERRO LÉXICO' if rel.tem_erro else 'OK'} - {rel.resumo()}")
    if tokens and not args.nao_gravar:
        print(f"Tokens gravados em: {fonte}.tokens.txt")
    print()
    return rel


def main():
    ap = argparse.ArgumentParser(description="Executa somente o analisador léxico COBOL")
    ap.add_argument("fontes", nargs="+", help="arquivo(s) .cob/.cbl ou pasta(s)")
    ap.add_argument("-I", dest="dirs", action="append", default=[],
                    help="pasta adicional de copybooks")
    ap.add_argument("-D", "--debug", action="store_true",
                    help="ativa as linhas de depuração (indicador 'D')")
    ap.add_argument("-n", "--nao-gravar", action="store_true",
                    help="não grava o arquivo .tokens.txt")
    args = ap.parse_args()

    resultados = []
    for f in lista_fontes(args.fontes):
        if not os.path.isfile(f):
            print(f"{f}: arquivo não encontrado", file=sys.stderr)
            resultados.append((f, None))
            continue
        resultados.append((f, analisa(f, args)))

    if len(resultados) > 1:
        print("=" * 70)
        print("RESUMO GERAL")
        print("=" * 70)
        for f, rel in resultados:
            st = "não encontrado" if rel is None else (
                "ERRO" if rel.tem_erro else "OK") + "  " + rel.resumo()
            print(f"  {os.path.basename(f):<28} {st}")
    rcs = [12 if r is None else r.codigo_retorno for _, r in resultados]
    return max(rcs, default=0)


if __name__ == "__main__":
    sys.exit(main())
