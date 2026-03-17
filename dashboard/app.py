"""Streamlit dashboard pour visualiser les données et les prédictions."""

import streamlit as st
import pandas as pd


@st.cache_data
def load_features(path: str = "data/02_intermediate/features.parquet") -> pd.DataFrame:
    return pd.read_parquet(path)


def main() -> None:
    st.set_page_config(page_title="EnergyStock AI", layout="wide")
    st.title("EnergyStock AI — Dashboard")

    df = load_features()
    tickers = sorted(df["ticker"].unique())

    ticker = st.selectbox("Ticker", tickers, index=tickers.index("NEE") if "NEE" in tickers else 0)
    date_min = df["date"].min()
    date_max = df["date"].max()
    as_of_date = st.date_input("Date", value=date_max, min_value=date_min, max_value=date_max)

    subset = df[(df["ticker"] == ticker) & (df["date"] == pd.to_datetime(as_of_date))]

    if subset.empty:
        st.warning("Aucune donnée disponible pour la date sélectionnée.")
        return

    st.markdown(f"### Données pour {ticker} - {as_of_date}")
    st.dataframe(subset.head(5))

    st.markdown("---")
    st.subheader("Visualisation des rendements")
    rendements = df[df["ticker"] == ticker][["date", "return"]].dropna()
    st.line_chart(rendements.set_index("date"))


if __name__ == "__main__":
    main()
