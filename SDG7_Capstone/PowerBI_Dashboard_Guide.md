# Power BI Dashboard Guide: SDG 7 Urban–Rural Electrification Gap

You will build the report in **Power BI Desktop** (Windows). It takes about 45–60 minutes.
Everything is built from two files the notebook writes: **`ssa_powerbi_data.csv`** and **`model_comparison.csv`**.
Run the notebook first so both files exist.

---

## 1. Load the data
1. Power BI Desktop → **Home → Get data → Text/CSV** → pick `ssa_powerbi_data.csv` → **Transform Data**.
2. In Power Query, set the data types:
   - `year` → **Whole number**
   - `access_urban_pct`, `access_rural_pct`, `urban_rural_gap`, `gdp_pc`, `urban_pop_pct`, `pop_growth`, `renewable_pct`, `predicted_gap`, `residual` → **Decimal number**
   - `Country Name`, `Country Code`, `IncomeGroup`, `split` → **Text**
3. Rename the query to **`ssa`** (right panel → Properties → Name). The DAX below uses this name.
4. **Close & Apply**.
5. Repeat **Get data → Text/CSV** for `model_comparison.csv`. In Power Query, rename the first column (blank or `Unnamed`) to **Model**, and name the query **`models`**.
6. Select the `Country Name` column in the Fields pane → **Column tools → Data category → Country/Region** (this makes the map work).

No relationship between the tables is needed.

---

## 2. DAX measures
Select the `ssa` table → **Home → New measure**, and paste each one.

```DAX
Avg Urban Access = AVERAGE(ssa[access_urban_pct])
Avg Rural Access = AVERAGE(ssa[access_rural_pct])
Avg Gap = AVERAGE(ssa[urban_rural_gap])

Latest Year = CALCULATE(MAX(ssa[year]), ALL(ssa[year]))

Avg Gap (Latest Year) =
CALCULATE([Avg Gap], ssa[year] = [Latest Year])

Gap Change since Start =
VAR y0 = CALCULATE(MIN(ssa[year]), ALLSELECTED(ssa[year]))
VAR y1 = CALCULATE(MAX(ssa[year]), ALLSELECTED(ssa[year]))
RETURN CALCULATE([Avg Gap], ssa[year] = y1) - CALCULATE([Avg Gap], ssa[year] = y0)

Countries = DISTINCTCOUNT(ssa[Country Name])

Avg Predicted Gap = AVERAGE(ssa[predicted_gap])

Test RMSE (pp) =
SQRT(AVERAGEX(FILTER(ssa, ssa[split] = "test"), ssa[residual] ^ 2))
```

---

## 3. Report pages (one per CRISP-DM phase)
Use **View → Page view → Fit to page**. Pick one consistent colour theme (View → Themes). Suggested: blue for urban, orange for rural.

### Page 1: Business understanding
- Text box: the problem, the business question and the use (copy from notebook Section 1).
- **Card** visuals: `Avg Urban Access`, `Avg Rural Access`, `Avg Gap`, `Countries`.
- **Slicer**: `year` (slider style).

### Page 2: Data understanding
- **Line chart**: X = `year`, Y = `Avg Urban Access` and `Avg Rural Access` (average access over time).
- **Clustered bar chart**: Y = `Country Name`, X = `Avg Gap (Latest Year)`, sorted descending (largest gaps by country).
- **Filled map** (or map): Location = `Country Name`, Colour saturation = `Avg Gap`.
- **Histogram-style column chart**: right-click `urban_rural_gap` → **New group → Bin size 10**, use the bin as X and **Count** as Y.
- **Slicers**: `Country Name` (dropdown) and `IncomeGroup`. Try **Kenya** to show your comparator.
- **Scatter chart**: X = `gdp_pc`, Y = `urban_rural_gap`, Details = `Country Name`, Legend = `IncomeGroup`.
- **Table**: Min, Max, Average, Standard deviation of `urban_rural_gap` (drag the field into a table and pick each aggregation) for the descriptive statistics.

### Page 3: Data preparation and missing data
- Text box with the steps (merge 8 indicators, SSA only, 2007 onward, interpolation limited to 2 years, target never imputed, log GDP, split by country).
- Small table: rows kept, countries kept, years covered.
- Text box with the **missing-data findings** (MCAR/MAR/MNAR) copied from notebook Section 2.3.

### Page 4: Modelling and evaluation
- **Table** from `models`: Model, `CV MSE (train countries)`, `Train R2`, `Test R2`, `Test MSE`, `Test RMSE`.
- **Clustered column chart**: Axis = `Model`, Values = `Test MSE`.
- **Scatter chart** with filter `split = test`: X = `urban_rural_gap` (actual), Y = `predicted_gap`, Details = `Country Name`. Add a diagonal reference by adding a constant line in the Analytics pane if you want.
- **Card**: `Test RMSE (pp)`.
- Text box: one-paragraph explanation of **R² vs MSE** (copy from notebook Section 5.1) and which model was selected and why.

### Page 5: Deployment and conclusions
- Text box: the selected model, what `best_model.pkl` does, and how to load it:
  `pickle.load(open("best_model.pkl","rb"))["model"].predict(df[features])`.
- Text box: conclusions, limitations (few countries, survey-based data, missing policy variables) and recommendations.
- Optional: **Table** of `Country Name`, `year`, `urban_rural_gap`, `predicted_gap`, `residual` with the `split` slicer.

---

## 4. Finishing touches
- Titles on every visual; axis titles with units (**percentage points** for the gap, **%** for access).
- Use **sync slicers** (View → Sync slicers) so `year` and `Country Name` carry across pages.
- Name each page after its CRISP-DM phase.
- Save as `SDG7_Dashboard.pbix` in the project folder.
- Optional: **File → Export → PDF** for a backup copy to submit.

## 5. What you present (two tools)
1. **The Power BI dashboard**: walk through Pages 1–5.
2. **The model**: show `best_model.pkl` being loaded and used in the notebook (Section 6 does this) and explain how it was selected.

## 6. Checklist for the incubation form
- [ ] CRISP-DM followed (all six phases in the notebook and dashboard pages)
- [ ] At least 3 models (4 compared)
- [ ] Assumptions tested (Section 4.2) and remedies applied
- [ ] Missing values investigated (Section 2.3)
- [ ] Power BI dashboard built
- [ ] Best model saved as a pickle file
- [ ] Fee cleared
- [ ] Uploaded to the LMS before the deadline
