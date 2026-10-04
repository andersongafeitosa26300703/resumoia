# ResumoIA

Carrossel diario de noticias de inteligencia artificial no Instagram (@resumoia), com aprovacao antes de publicar.

## Fluxo diario (horario de Brasilia)
| Hora | Quem | O que faz |
|---|---|---|
| 04:30 | GitHub Actions (`collect.yml`) | Le os feeds RSS e grava `data/candidates.json` |
| 05:00 | Rotina em nuvem do Claude | Escolhe 4 noticias, escreve os resumos e grava `data/today.json` (prompt em `docs/prompt-rotina.md`) |
| logo apos | GitHub Actions (`draft.yml`) | Gera as 5 imagens e a legenda e abre uma Issue "Rascunho AAAA-MM-DD" |
| quando voce quiser | **Voce** | Confere a Issue e adiciona o rotulo `aprovado` (pode ser pelo celular) |
| em seguida | GitHub Actions (`publish.yml`) | Publica o carrossel no Instagram e fecha a Issue |

Para descartar um rascunho: feche a Issue sem rotulo. Nada e publicado sem o rotulo.

## Segredos do repositorio
- `IG_ACCESS_TOKEN`: token de Pagina permanente (gerado com o `get_token.py` do projeto 365 Dias Estoicos).
- `IG_USER_ID`: opcional (o robo descobre a conta pelo token).

## Comandos locais
```
python scripts/fetch_news.py                 # coleta as candidatas
python scripts/make_draft.py                 # gera drafts/DATA a partir de data/today.json
python scripts/render_carousel.py            # prototipo com data/sample.json
```
