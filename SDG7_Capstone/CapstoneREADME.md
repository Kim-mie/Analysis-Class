# SDG-Linked Portfolio Project — One-Pager

## Chosen SDG and Sub-Target

**SDG 7 — Affordable and Clean Energy**
**Sub-target 7.1** — "By 2030, ensure universal access to affordable, reliable and modern energy services," measured by indicator **7.1.1: proportion of population with access to electricity**.

**Specific angle:** the persistent **urban–rural electrification gap in Sub-Saharan Africa**. Regional electrification has grown steadily since 2010, but almost all of the remaining "energy access deficit" is concentrated in rural areas, and rural population growth is currently outpacing new rural connections — meaning the absolute number of unconnected rural people is not shrinking even as national percentages improve.

## Why This Excites Me

The headline "% electrified" number that shows up in most SDG dashboards hides a much sharper story once you split it by urban vs. rural. Roughly 82% of urban Sub-Saharan Africans had power in 2023, versus about a third of rural residents — and rural population growth is outrunning new connections, so the raw number of people without power has stayed above 500 million for two decades even as the percentage figure improves. Kenya is a useful microcosm here: it's frequently cited as one of the region's off-grid/mini-grid solar success stories, which makes it a natural comparator against countries where rural electrification has stalled. I'm interested in eventually building a model (in a later phase of this project) that looks at what predicts the *size and persistence* of the urban-rural gap across countries and years, rather than just tracking the national average — that's the sub-area I want to dig into.

**What my own EDA (2007-2023, clean sub-panel) already shows:** the average urban-rural gap across Sub-Saharan Africa is about **44 percentage points** (std ~21), and the two distributions barely overlap — urban access is heavily clustered in the 75-100% range, while rural access is clustered in the 0-25% range. The extremes make the point vividly: **Equatorial Guinea** shows an 89-point gap (90% urban vs. ~1-2% rural, 2018-2022) despite substantial national oil wealth, while a handful of smaller/wealthier nations like **Mauritius** show almost no gap at all (both near 99-100%). **Kenya** is the case that most excites me: its gap shrank from ~43 points in 2007 to ~29.6 points in 2022, with the sharpest improvement in rural access happening from 2015 onward (29% to 68.4%) — timing that lines up closely with the mini-grid/off-grid solar expansion documented in reference #4 below. Seeing the literature and the data tell the same story from two different angles is exactly why I want to keep digging into this sub-area.

## References

1. IEA, IRENA, UNSD, World Bank, & WHO (2024). *Tracking SDG 7: The Energy Progress Report 2024.* World Bank, Washington DC. https://www.iea.org/reports/tracking-sdg7-the-energy-progress-report-2024
   *In plain words: the official global "scorecard" tracking who has electricity access and who doesn't, country by country.*

2. ESMAP / World Bank (2025). *Chapter 1: Access to Electricity* (Tracking SDG7 report chapter — urban/rural divide, Mission 300 initiative). https://trackingsdg7.esmap.org/sites/default/files/download-documents/chapter1_accesstoelectricity.pdf
   *In plain words: a shorter chapter from that same report focused specifically on the urban vs. rural gap and a $90B initiative ("Mission 300") to close it.*

3. Falama, Y. (2025). "Performance Improvement of Rural Electrification–Based PV Energy System: A Case Study in Sub-Saharan Africa." *Journal of Electrical and Computer Engineering*, 2025, 8843767. https://doi.org/10.1155/jece/8843767
   *In plain words: shows that if you design solar-panel systems for villages more cleverly, they get cheaper and work better — which makes villages more willing to actually use them.*

4. "The political economy of mini-grid electricity development and innovation in Kenya." *DOAJ.* https://doaj.org/article/fca134d4cdb44ee48ae29759155b74ba
   *In plain words: small local power systems ("mini-grids") for villages only succeed in Kenya if companies, government, and villagers all cooperate — it's not just a technology problem.*

5. "A focus on Ghana's sustainable development: Examining the interplay of income inequality and energy poverty." *DOAJ.* https://doaj.org/article/0dc6bb6ec0574a859d7393ef803246d0
   *In plain words: being poor and lacking electricity feed off each other in a loop — and giving cities power while leaving rural areas behind can widen the rich-poor gap even further.*

## Dataset

**Name:** SDG 7.1.1 Electrification Dataset — Access to Electricity (World Development Indicators), World Bank / ESMAP
**Link:** https://data.worldbank.org/indicator/EG.ELC.ACCS.ZS (also available split by urban: `EG.ELC.ACCS.UR.ZS` and rural: `EG.ELC.ACCS.RU.ZS`; raw source at https://trackingsdg7.esmap.org/downloads)
**License:** CC BY-4.0
**Description:** Country-year panel (1990–2023) giving the percentage of the population with access to electricity, for every country, split into total/urban/rural. Compiled by the World Bank's Global Electrification Database from nationally representative household surveys and census data. Filtered to Sub-Saharan African countries this is well under 50,000 rows (~48 countries × ~34 years × 3 series ≈ 4,900 rows), fits the "small dataset" guidance, and is not from Kaggle — it's sourced directly from the World Bank site with full indicator-level provenance.

**Cleaning decision made during EDA:** missingness by year showed >90% of countries had no data in 1990, dropping steadily until ~2007, after which coverage is 100% complete through 2023 (likely reflecting the ramp-up in international statistical reporting around the UN Millennium Development Goals). The analysis below therefore uses a **2007-2023 sub-panel (48 countries x 17 years = 816 country-years, 0% missing)** rather than the full 1990-2023 range, to avoid biasing distributions/trends with unreliable early data.