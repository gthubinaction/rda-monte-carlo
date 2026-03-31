# RDA Monte Carlo Simulation

**Reestruturação Dinâmica de Ativos (RDA): Uma Abordagem Multicritérios de Recuperação Fiscal**

Repositório de dados e código aberto referente à simulação Monte Carlo descrita na Seção 6 do artigo.  
Publicado em conformidade com os princípios de **ciência aberta** (*open science*) e **pesquisa reprodutível**.

---

## Estrutura do repositório

```
rda-monte-carlo/
├── simulation/
│   └── rda_montecarlo.py     # Código principal — 10.000 iterações
├── data/
│   └── parameters.json       # Todas as premissas e distribuições documentadas
├── notebooks/
│   └── analysis.ipynb        # Visualizações e reprodução da Tabela 3 do artigo
├── outputs/                  # Gerado ao executar a simulação
│   ├── raw_iterations.csv    # Resultados brutos (10.000 linhas)
│   ├── results_summary.csv   # Percentis P10/P25/P50/P75/P90
│   ├── tabela3_cenarios.csv  # Tabela 3 do artigo
│   ├── fig1_distribuicao_impacto.png
│   ├── fig2_contribuicao_pilares.png
│   └── fig3_sensibilidade.png
├── requirements.txt
└── LICENSE
```

---

## Como executar

### Pré-requisitos

```bash
pip install -r requirements.txt
```

### Simulação via linha de comando

```bash
python simulation/rda_montecarlo.py
```

Saída esperada:

```
Running RDA Monte Carlo simulation (10,000 iterations)...

── Scenario Summary (R$ million/year, annual average) ──────────────
 scenario_label  pilar1  pilar2  pilar3  net_total  pct_rcl
     Pessimista     ...     ...     ...        595      1.8%
        Moderado     ...     ...     ...        995      3.0%
        Otimista     ...     ...     ...      1.436      4.3%
```

### Notebook interativo

```bash
jupyter notebook notebooks/analysis.ipynb
```

---

## Premissas e transparência metodológica

Todas as distribuições de probabilidade utilizadas estão documentadas em [`data/parameters.json`](data/parameters.json), incluindo:

- **Fonte bibliográfica** por variável
- **Tipo de distribuição**: triangular `{min, mode, max}` — adequada para variáveis com expert elicitation (Vose, 2008)
- **Justificativa dos intervalos** baseada em literatura e relatórios oficiais

### Variáveis críticas (Seção 6.3 do artigo)

| Variável | Distribuição | Fonte principal |
|---|---|---|
| Taxa de monetização de ativos | Triangular (0,40 – 0,70 – 0,85) | World Bank (2021); Kaganova & McKellar (2006) |
| Autossustentabilidade das ETEs | Triangular (0,50 – 0,65 – 0,80) | SENAI (2023); UNESCO-UNEVOC (2021) |
| Múltiplo P/VPA Banrisul | Triangular (1,0 – 1,3 – 1,6) implícito | Damodaran (2022); BCB (2024) |

### Reprodutibilidade

A semente aleatória (`SEED = 42`) está fixada em `rda_montecarlo.py`.  
Para análise de robustez da semente, altere o valor e re-execute — os percentis P10/P50/P90 devem variar < 2%.

---

## Como citar

```bibtex
@software{rda_montecarlo_2025,
  author    = {[Nome do Autor]},
  title     = {RDA Monte Carlo Simulation},
  year      = {2025},
  url       = {https://github.com/[usuario]/rda-monte-carlo},
  note      = {Supplementary material for: Reestruturação Dinâmica de Ativos (RDA):
               Uma Abordagem Multicritérios de Recuperação Fiscal}
}
```

---

## Referências principais

- Kaganova, O., & McKellar, J. (Eds.). (2006). *Managing Government Property Assets*. Urban Institute Press.
- Vose, D. (2008). *Risk Analysis: A Quantitative Guide* (3rd ed.). Wiley.
- World Bank (2021). *Government Asset Monetization: Lessons from International Experience*. Washington, DC.
- SENAI (2023). *Relatório de Gestão 2022*. Brasília: CNI.
- Banrisul (2024). *Relatório Anual 2023*. Porto Alegre.
- BCB (2024). *Relatório de Estabilidade Financeira*. Brasília: Banco Central do Brasil.

---

## Licença

MIT License — livre para uso, adaptação e redistribuição com atribuição.
