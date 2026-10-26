# cripto-core

Biblioteca Python pura extraída na Sprint 06A. Distribuição `cripto-core==0.1.0`, pacote `cripto_core`, Python 3.13.15 e uv 0.12.19. Sem dependências de produção além da biblioteca padrão; sem CLI, flags, rede, banco, carteira ou relógio de parede.

## API e contratos

| Módulo | API | Contrato |
|---|---|---|
| `errors` | `PaperError`, `MarketError` | Tipos únicos de erro e códigos existentes; fachadas do bot reexportam as mesmas classes |
| `numeric` | `parse_decimal`, `number`, `text`, `bounded`, `money`, `Q`, `ZERO` | Conversão textual finita, limites e arredondamentos originais; quantum monetário de oito casas |
| `validation` | `mapping`, `sequence`, `identifier`, `instant`, `require_object` | Validação estrita e conversão de timestamp UTC recebido explicitamente |
| `serialization` | `canonical`, `digest`, `record`, `fingerprint` | JSON canônico, SHA256 e representação Decimal exata |
| `contracts` | `Plan` | DTO imutável, reserva e fill_id do contrato `paper-integral-v1`; não cria reserva/lançamento |
| `execution` | `observation`, `filters`, `range_check`, `quantity_step`, `execution_price`, `make_plan` | Modelo sintético BTCUSDT/Spot existente: tick/step/notional/custos e observação posterior; não admite ou executa ordens |
| `sizing` | `sized_quantity(usdt_free, equity, module, quote, at, parameters, rules)` | Mesmo cálculo anterior com saldos explícitos; não recebe Wallet ou altera limites |
| `strategy.sma` | `Snapshot`, `Decision`, `Strategy`, `TrendSMA` | SMA pura, warm-up/cross/igualdade/inventário e precisão local 80 preservados |

Use `Decimal` recebido de strings, sem float. Helpers monetários e sizing conservam a política de contexto do chamador; os casos financeiros do bot usam `localcontext().prec=80`. `make_plan` e SMA estabelecem seu próprio contexto local 80. Importar a biblioteca não altera contexto global. Regras/filtros suportados permanecem os do modelo sintético atual; não generalizar para outros pares ou liquidez real.

Wallet/Intent/Posting, ledger, journal, risco/admissão, registro/flags, coordenação, casos de uso e backtest continuam no bot. Instalar core não habilita estratégia nem modo de execução. Os imports antigos do bot permanecem como reexports explícitos ou wrappers sem cópia de algoritmo. O literal do modelo no DTO Plan preserva a identidade serializada anterior; não é um novo store.

## Desenvolvimento e build

```bash
uv sync --locked --group dev --offline
uv run --locked --offline ruff check .
uv run --locked --offline ruff format --check .
uv run --locked --offline mypy src
uv run --locked --offline pytest -q --cov=cripto_core --cov-branch
uv build --offline --out-dir dist/06a-final
```

O lock e os artefatos são independentes do bot. Downloads de ferramentas ausentes são separados dos testes offline; a entrega registra a reutilização de dependências verificadas da baseline quando o cache é incompleto. Core precisa ser importável/testável sem o bot instalado. Os testes reutilizam vetores sintéticos e oráculos anteriores de execução/SMA, além de verificar precisão, pureza transitiva e sizing explícito.

## Consumo

Construir primeiro `dist/06a-final/cripto_core-0.1.0-py3-none-any.whl`. O bot declara dependência exata e fonte local explícita desse wheel; instalar os dois wheels identificados para o smoke, sem importar o checkout irmão. Essa fonte local exige disponibilizar o artefato no caminho registrado; não representa publicação em índice. Mudança no core exige nova identidade e atualização deliberada da composição/lock.

A identidade experimental do bot inclui código efetivamente instalado do core, versão, tipo de instalação e controles do consumidor. Instalação por wheel deve conferir com RECORD; core editable é rejeitado pela identidade do consumidor nesta entrega. Congelamento/retomada não dependem apenas do número da versão. Reorganização não reabre janela final histórica.

Documentação central: [Sprint 06A](../docs/sprints/sprint-06a.md), [validação](../docs/testes/sprint-06a-validacao.md) e [arquitetura](../docs/arquitetura.md). Nenhuma ordem externa ou recurso AWS integra esta biblioteca.
