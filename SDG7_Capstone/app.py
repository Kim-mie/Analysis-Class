"""SDG 7 dashboard: urban-rural electrification gap in Sub-Saharan Africa.
Organised by CRISP-DM phases. Run:  streamlit run app.py
Needs ssa_model_data.csv (created by the notebook, Section 3) next to this file.
"""
import os
import pickle
import numpy as np
import pandas as pd
import plotly.express as px
import streamlit as st
from sklearn.linear_model import Ridge, LinearRegression
from sklearn.metrics import mean_squared_error, r2_score
from sklearn.model_selection import GroupShuffleSplit
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler

st.set_page_config(page_title="SDG 7: Urban-Rural Electrification Gap", layout="wide")

FEATURES = ["log_gdp_pc", "urban_pop_pct", "pop_growth", "renewable_pct"]
LABELS = {
    "log_gdp_pc": "log GDP per capita",
    "urban_pop_pct": "Urban population (%)",
    "pop_growth": "Population growth (%)",
    "renewable_pct": "Renewable share of energy (%)",
    "urban_rural_gap": "Urban-rural gap (pp)",
    "access_urban_pct": "Urban access (%)",
    "access_rural_pct": "Rural access (%)",
}
TARGET = "urban_rural_gap"


@st.cache_data
def load():
    path = os.path.join(os.path.dirname(__file__), "ssa_model_data.csv")
    return pd.read_csv(path)


if not os.path.exists(os.path.join(os.path.dirname(__file__), "ssa_model_data.csv")):
    st.error("ssa_model_data.csv not found. Run the notebook first (Section 3 writes it).")
    st.stop()

df = load()

st.title("SDG 7: the urban-rural electrification gap in Sub-Saharan Africa")
st.caption("Sub-target 7.1, universal access to electricity. Source: World Bank (WDI / ESMAP), 2007 onward.")

tabs = st.tabs(["1. Business", "2. Data understanding", "3. Data preparation",
                "4. Modelling", "5. Evaluation", "6. Predict (what-if)"])

# ---------------------------------------------------------------- 1
with tabs[0]:
    st.header("Business understanding")
    st.markdown(
        """
**Problem.** National "% with electricity" figures hide a sharp urban-rural split. Rural population growth is outpacing new
connections, so the number of people without power stays above 500 million.

**Question.** Which country-level factors are associated with the size of the urban-rural gap, and how well can we predict it?

**Use.** Help funders and governments prioritise where rural electrification (grid, mini-grid, off-grid solar) is most needed.
        """
    )
    latest = df["year"].max()
    c = df[df["year"] == latest]
    a, b, g, n = st.columns(4)
    a.metric(f"Avg urban access ({latest})", f"{c['access_urban_pct'].mean():.0f}%")
    b.metric(f"Avg rural access ({latest})", f"{c['access_rural_pct'].mean():.0f}%")
    g.metric("Avg gap", f"{c[TARGET].mean():.0f} pp")
    n.metric("Countries", df["Country Name"].nunique())

# ---------------------------------------------------------------- 2
with tabs[1]:
    st.header("Data understanding")
    y0, y1 = int(df["year"].min()), int(df["year"].max())
    yr = st.slider("Year range", y0, y1, (y0, y1))
    countries = sorted(df["Country Name"].unique())
    pick = st.multiselect("Countries (empty = all)", countries)
    d = df[(df["year"] >= yr[0]) & (df["year"] <= yr[1])]
    if pick:
        d = d[d["Country Name"].isin(pick)]
    if d.empty:
        st.warning("No data for this selection.")
    else:
        st.subheader("Descriptive statistics")
        cols = ["access_urban_pct", "access_rural_pct", TARGET] + [c for c in FEATURES]
        st.dataframe(d[cols].describe().T.round(2))

        c1, c2 = st.columns(2)
        with c1:
            tr = d.groupby("year")[["access_urban_pct", "access_rural_pct"]].mean().reset_index()
            st.plotly_chart(px.line(tr.melt("year"), x="year", y="value", color="variable", markers=True,
                                    title="Average access over time (%)",
                                    labels={"value": "%", "variable": ""}))
        with c2:
            st.plotly_chart(px.histogram(d, x=TARGET, nbins=25, title="Distribution of the urban-rural gap",
                                         labels={TARGET: LABELS[TARGET]}))

        last = d[d["year"] == d["year"].max()].sort_values(TARGET, ascending=False)
        st.plotly_chart(px.bar(last, x="Country Name", y=TARGET,
                               title=f"Gap by country ({int(last['year'].max())})",
                               labels={TARGET: LABELS[TARGET]}))

        st.subheader("Relationships")
        xv = st.selectbox("Predictor", FEATURES, format_func=lambda k: LABELS[k])
        st.plotly_chart(px.scatter(d, x=xv, y=TARGET, color="IncomeGroup", hover_name="Country Name",
                                   labels={xv: LABELS[xv], TARGET: LABELS[TARGET]},
                                   title=f"{LABELS[TARGET]} vs {LABELS[xv]}"))
        corr = d[[TARGET] + FEATURES].corr().round(2)
        st.plotly_chart(px.imshow(corr, text_auto=True, zmin=-1, zmax=1, color_continuous_scale="RdBu_r",
                                  title="Correlation matrix"))

# ---------------------------------------------------------------- 3
with tabs[2]:
    st.header("Data preparation")
    st.markdown(
        """
- Merged eight World Bank indicators on country and year; kept **Sub-Saharan Africa** only.
- Restricted to **2007 onward** (earlier years are sparse).
- Predictor gaps filled by **interpolation within each country** (max 2 years); rows still missing were dropped; the target was never imputed.
- **log transform** of GDP per capita (right-skewed).
- **Standardised** inputs inside the model pipeline (fit on training data only).
- Train/test split **by country**, so test countries are unseen.
        """
    )
    st.write(f"Modelling dataset: **{len(df):,} rows**, **{df['Country Name'].nunique()} countries**, "
             f"{int(df['year'].min())}-{int(df['year'].max())}.")
    st.dataframe(df.head(50))


# ---------------------------------------------------------------- model
@st.cache_resource
def fit(alpha, test_size, seed):
    X, y, g = df[FEATURES], df[TARGET], df["Country Name"]
    tr, te = next(GroupShuffleSplit(n_splits=1, test_size=test_size, random_state=seed).split(X, y, g))
    ols = make_pipeline(StandardScaler(), LinearRegression()).fit(X.iloc[tr], y.iloc[tr])
    rdg = make_pipeline(StandardScaler(), Ridge(alpha=alpha)).fit(X.iloc[tr], y.iloc[tr])
    return ols, rdg, X.iloc[tr], X.iloc[te], y.iloc[tr], y.iloc[te]


with tabs[3]:
    st.header("Modelling")
    st.markdown(
        "Linear Regression is the baseline. **Ridge (L2)** shrinks coefficients to cope with correlated predictors. "
        "Change the settings and watch Section 5 update."
    )
    alpha = st.slider("Ridge alpha (penalty strength)", 0.01, 100.0, 1.0, 0.01)
    test_size = st.slider("Share of countries held out for testing", 0.15, 0.4, 0.25, 0.05)
    ols, rdg, Xtr, Xte, ytr, yte = fit(alpha, test_size, 42)
    coefs = pd.DataFrame({"Linear": ols[-1].coef_, "Ridge": rdg[-1].coef_},
                         index=[LABELS[f] for f in FEATURES]).round(3)
    st.subheader("Standardised coefficients")
    st.dataframe(coefs)
    st.plotly_chart(px.bar(coefs.reset_index().melt("index"), x="value", y="index", color="variable",
                           barmode="group", orientation="h",
                           labels={"value": "Effect on gap (pp) per 1 std dev", "index": ""}))
    st.caption("Assumption tests (linearity, independence, homoscedasticity, normality, VIF) are in the notebook, Section 4.2.")

# ---------------------------------------------------------------- 5
with tabs[4]:
    st.header("Evaluation")
    rows = {}
    for name, m in [("Linear Regression", ols), ("Ridge", rdg)]:
        for part, Xa, ya in [("train", Xtr, ytr), ("test", Xte, yte)]:
            p = m.predict(Xa)
            mse = mean_squared_error(ya, p)
            rows[f"{name} ({part})"] = {"R²": r2_score(ya, p), "MSE": mse, "RMSE": np.sqrt(mse)}
    st.dataframe(pd.DataFrame(rows).T.round(3))
    st.markdown(
        """
**MSE** is the average squared error, in percentage-points squared (take the square root, RMSE, for percentage points); it punishes large misses.
**R²** is unit-free: the share of the variation in the gap the model explains, compared with just predicting the average (it can be negative on unseen data).
        """
    )
    comp_path = os.path.join(os.path.dirname(__file__), "model_comparison.csv")
    if os.path.exists(comp_path):
        st.subheader("All four models (from the notebook)")
        st.caption("Selected by lowest country-grouped cross-validated MSE on the training countries; test metrics on unseen countries.")
        st.dataframe(pd.read_csv(comp_path, index_col=0))
    p = rdg.predict(Xte)
    ev = pd.DataFrame({"Actual": yte.values, "Predicted": p})
    fig = px.scatter(ev, x="Actual", y="Predicted", title="Ridge: actual vs predicted (unseen countries)")
    lo, hi = float(min(ev.min())), float(max(ev.max()))
    fig.add_shape(type="line", x0=lo, y0=lo, x1=hi, y1=hi, line=dict(dash="dash", color="red"))
    st.plotly_chart(fig)

# ---------------------------------------------------------------- 6
with tabs[5]:
    st.header("Predict the gap (what-if)")
    pkl_path = os.path.join(os.path.dirname(__file__), "best_model.pkl")
    artifact = None
    if os.path.exists(pkl_path):
        with open(pkl_path, "rb") as f:
            artifact = pickle.load(f)
    pred_model = artifact["model"] if artifact else rdg
    st.caption(
        (f"Uses the best model saved from the notebook (best_model.pkl: {artifact['model_name']}). "
         if artifact else "Uses the Ridge model from the Modelling tab (best_model.pkl not found). ")
        + "An illustration of association, not a causal forecast."
    )
    c1, c2 = st.columns(2)
    with c1:
        gdp = st.slider("GDP per capita (US$)", 300, 20000, 1500, 50)
        urb = st.slider("Urban population (%)", 10.0, 90.0, float(df["urban_pop_pct"].median()), 0.5)
    with c2:
        grw = st.slider("Population growth (%)", 0.0, 5.0, float(df["pop_growth"].median()), 0.1)
        ren = st.slider("Renewable share of energy (%)", 0.0, 100.0, float(df["renewable_pct"].median()), 1.0)
    x = pd.DataFrame([{"log_gdp_pc": np.log(gdp), "urban_pop_pct": urb, "pop_growth": grw, "renewable_pct": ren}])
    st.metric("Predicted urban-rural gap", f"{pred_model.predict(x)[0]:.1f} percentage points")
