# Analisador Léxico COBOL

Primeira fase do compilador descrito na *Especificação Textual do Compilador
COBOL*, **Seção 2 – Análise Léxica**. Lê um programa COBOL em formato fixo de
colunas e gera a lista de **tokens**.

```
programa .cob  ──►  ANALISADOR LÉXICO  ──►  lista de tokens (+ mensagens de erro)
```

Só precisa de **Python 3.8+**, sem nenhuma instalação extra.

---

## Como rodar

Abra o terminal dentro desta pasta (`lexico-cobol`):

```
python lexico.py exemplos-professor\prog001_divisoes.cob     (um arquivo)
python lexico.py exemplos-professor                          (a pasta toda)
```

Para cada programa, a saída mostra:

1. **a lista de tokens**: uma linha por token;
2. **um resumo** com quantos tokens há de cada categoria;
3. **as mensagens do léxico** (níveis I, W, E, S).

Além de imprimir na tela, grava um arquivo `<programa>.tokens.txt` ao lado
do programa com a lista de tokens.

Exemplo de saída:

```
LINHA:COL  ÁREA  CATEGORIA      TEXTO
   15:8    A     PALAVRA_CHAVE  IDENTIFICATION
   15:23   B     PALAVRA_CHAVE  DIVISION
   15:31   B     PONTO          .
   16:8    A     PALAVRA_CHAVE  PROGRAM-ID
   16:18   B     PONTO          .
   16:20   B     IDENT          PROG0001
```

| Coluna | O que é |
|---|---|
| LINHA:COL | onde o token começa no arquivo |
| ÁREA | `A` se começa nas colunas 8–11, `B` se começa na coluna 12 em diante |
| CATEGORIA | tipo do token (tabela abaixo) |
| TEXTO | o texto original do token |

Opções: `-D` liga as linhas de depuração (`D` na coluna 7); `-I pasta`
adiciona uma pasta onde procurar copybooks; `-n` não grava o `.tokens.txt`.

---

## Arquivos da pasta

```
lexico-cobol/
├── lexico.py                 programa que você executa
├── analisador/
│   ├── lexer.py              o analisador léxico
│   └── diagnostics.py        mensagens de erro (níveis I/W/E/S)
├── exemplos-professor/       os 7 programas de teste do professor
├── exemplos/
│   ├── formato.cbl           exercita o layout de colunas
│   ├── copia.cbl             exercita a diretiva COPY
│   ├── copybooks/CLIENTE.cpy copybook usado por copia.cbl
│   └── erros_lexicos.cbl     um erro léxico proposital por linha
└── testes/test_lexico.py     testes automáticos
```

Rodar os testes: `python -m unittest discover -s testes -v`

---

## O que o léxico faz

### 1. Lê cada linha respeitando as colunas (item 2.1)

| Colunas | Tratamento |
|---|---|
| 1–6 | área de sequência: **ignorada** |
| 7 | indicador: `*` ou `/` comentário (linha ignorada); `-` continuação; `D` linha de depuração (só lida com `WITH DEBUGGING MODE` ou opção `-D`); outro caractere → erro `LEX-003` |
| 8–11 | Área A |
| 12–72 | Área B |
| 73–80 | identificação do programa: **desprezada** |

### 2. Quebra o texto em tokens (item 2.2)

| Categoria | Exemplos | Regras |
|---|---|---|
| `PALAVRA_CHAVE` | `IDENTIFICATION`, `DIVISION`, `MOVE`, `PERFORM` | palavras reservadas da linguagem |
| `IDENT` | `WS-TOTAL`, `100-INICIO` | nomes criados pelo programador: letras, dígitos e hífen; até 30 caracteres; não começa nem termina com hífen; precisa ter ao menos uma letra |
| `NUM` | `150`, `-123.45`, `01` | dígitos, sinal opcional, ponto decimal interno; até 18 dígitos |
| `ALFA` | `'OLA'`, `"D'AGUA"` | texto entre aspas simples ou duplas; aspas duplicadas viram uma aspa dentro do texto |
| `PIC` | `S9(5)V99`, `X(20)` | a palavra logo depois de `PIC`/`PICTURE` |
| `PONTO` | `.` | fim de sentença |
| `VIRGULA`, `PONTO_VIRGULA` | `,` `;` | separadores |
| `ABRE`, `FECHA` | `(` `)` | parênteses |
| `OP` | `+ - * / ** = > < >= <=` | operadores |
| `EOF` | — | marca o fim do arquivo |

Palavras são convertidas para maiúsculas (`move` = `MOVE`); o texto dos
literais é mantido como está.

### 3. Casos especiais

- **Continuação de literal:** um texto entre aspas que não fecha até a
  coluna 72 continua na linha seguinte, que deve ter `-` na coluna 7. O texto
  recomeça depois da primeira aspa dessa linha.
- **Continuação de palavra:** se uma palavra termina exatamente na coluna 72
  e a linha seguinte tem `-` na coluna 7, as duas partes viram um único token
  (`TO T` + `-AB-TRABALHADOR` → `TAB-TRABALHADOR`).
- **`AUTHOR.`, `DATE-WRITTEN.` etc.:** o texto depois desses parágrafos é
  livre, então é tratado como comentário (mensagem informativa `LEX-006`).
- **Sublinhado `_` em nomes** (`PROG005_STRING`): não é do padrão, mas é
  aceito pelo GnuCOBOL; o léxico aceita e mostra um aviso `LEX-017`.
- **COPY:** `COPY CLIENTE.` faz o léxico parar o arquivo atual, ler
  `CLIENTE.cpy` (na mesma pasta, em `copybooks/` ou na pasta `-I`) e colocar
  os tokens do copybook no lugar. Copybook não encontrado → erro `LEX-023`;
  copybook que inclui a si mesmo → erro severo `LEX-024`.

---

## Mensagens de erro do léxico

| Nível | Significado |
|---|---|
| **I** | informação (sugestão) |
| **W** | aviso: não é erro, mas merece atenção |
| **E** | erro léxico |
| **S** | falha grave: a análise para na hora |

| Código | Nível | Situação |
|---|---|---|
| LEX-000 | S | arquivo não pode ser lido |
| LEX-001 | W | tabulação encontrada (convertida em espaços) |
| LEX-002 | W | linha com menos de 7 colunas |
| LEX-003 | E | caractere inválido na coluna 7 |
| LEX-004 | W | `-` na coluna 7 sem nada para continuar |
| LEX-005 | W | linha de continuação com texto na Área A |
| LEX-006 | I | `AUTHOR.` e similares tratados como comentário |
| LEX-007 | E | literal sem aspas de fechamento |
| LEX-008 | E | linha de continuação de literal sem aspas |
| LEX-009 | W | literal com mais de 160 caracteres |
| LEX-010 | W | literal vazio |
| LEX-011 | W | ponto final sem espaço depois |
| LEX-012 | E | caractere inválido |
| LEX-013 | E | número com mais de 18 dígitos |
| LEX-014 | E | nome com mais de 30 caracteres |
| LEX-015 | E | nome começando ou terminando com hífen |
| LEX-016 | E | nome sem nenhuma letra |
| LEX-017 | W | nome com sublinhado `_` |
| LEX-020 a 026 | E/S | problemas na diretiva COPY |

Formato da mensagem: `arquivo:linha:coluna: NÍVEL [CÓDIGO] descrição`.

---

## Resultado com os programas do professor

Programas do repositório
[ebasso/cobol-exemplos](https://github.com/ebasso/cobol-exemplos) (licença MIT):

| Programa | Tokens | Resultado |
|---|---|---|
| prog001_divisoes.cob | 47 | OK (6 informações) |
| prog002_operacoes.cob | 320 | OK (1 aviso) |
| prog003_calculadora.cob | 229 | OK |
| prog004_folha_pgto.cob | 221 | OK (1 aviso) |
| prog005_strings.cob | 236 | OK (2 avisos) |
| prog006_files.cob | 225 | OK (3 avisos) |
| prog007_loja.cob | 566 | OK (2 avisos) |
