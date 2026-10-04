# ResumoIA

Carrossel diario de noticias de inteligencia artificial no Instagram (@resumoia), com aprovacao antes de publicar.
Tudo roda no GitHub Actions; o Claude (escolha e resumo das noticias) usa a assinatura do Claude do dono, sem chave de API.

## Fluxo diario (horario de Brasilia)
| Hora | Workflow | O que faz |
|---|---|---|
| 05:00 | `daily.yml` | Le os feeds RSS, o **Claude** escolhe 4 noticias e escreve os resumos, o GitHub gera as 5 imagens e a legenda e abre uma Issue "Rascunho AAAA-MM-DD" |
| quando voce quiser | **Voce** | Confere a Issue e adiciona o rotulo `aprovado` (pode ser pelo celular) |
| em seguida | `publish.yml` | Publica o carrossel no Instagram e fecha a Issue |

Para descartar um rascunho: feche a Issue sem rotulo. Nada e publicado sem o rotulo.
`draft.yml` regenera o rascunho se alguem editar `data/today.json` na mao e der push.

## Segredos do repositorio
- `CLAUDE_CODE_OAUTH_TOKEN`: token da assinatura do Claude (gerado com `claude setup-token`, planos Pro/Max).
- `IG_ACCESS_TOKEN`: token de Pagina permanente do Instagram.
- `IG_USER_ID`: opcional (o robo descobre a conta pelo token).
- O app **Claude** do GitHub precisa estar instalado neste repositorio (github.com/apps/claude).

## Comandos locais
```
python scripts/fetch_news.py                 # coleta as candidatas
python scripts/make_draft.py                 # gera drafts/DATA a partir de data/today.json
python scripts/render_carousel.py            # prototipo com data/sample.json
```
