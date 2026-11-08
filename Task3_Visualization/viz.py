"""
Task 3: Data Visualization  (CodeAlpha Data Analytics internship)

Turns books.csv (from scraper.py) into individual charts, a one-page dashboard,
and a short data story.

Usage:
    python viz.py                  # reads books.csv, writes viz_output/
    python viz.py --csv other.csv

Requires: pandas, numpy, matplotlib, seaborn
"""
import argparse
import os

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns

OUT = "viz_output"
BLUE, LIGHT, ACCENT, GREY = "#2f5d8a", "#9db8d6", "#d1495b", "#555555"
sns.set_theme(style="whitegrid", context="notebook")
plt.rcParams.update({"axes.spines.top": False, "axes.spines.right": False,
                     "axes.titleweight": "bold", "axes.titlesize": 12})


def save(name):
    plt.tight_layout()
    plt.savefig(os.path.join(OUT, name), dpi=160, bbox_inches="tight")
    plt.close()


# ---- individual chart functions (each takes an axis so the dashboard can reuse them)
def price_hist(df, ax):
    sns.histplot(df["price_gbp"], bins=30, color=BLUE, ax=ax)
    med = df["price_gbp"].median()
    ax.axvline(med, color=ACCENT, ls="--")
    ax.text(med, ax.get_ylim()[1] * 0.92, f" median £{med:.2f}", color=ACCENT, va="top")
    q1, q3 = df["price_gbp"].quantile([0.25, 0.75])
    ax.set(title=f"Half of all books cost £{q1:.0f} to £{q3:.0f}", xlabel="Price (£)", ylabel="Number of books")


def rating_bar(df, ax):
    g = df.groupby("rating")["price_gbp"].mean()
    ax.bar(g.index, g.values, color=BLUE)
    for x, v in g.items():
        ax.text(x, v + 0.3, f"£{v:.0f}", ha="center", fontsize=9)
    ax.set(title="Average price by star rating", xlabel="Rating (stars)", ylabel="Mean price (£)")
    ax.set_ylim(0, g.max() * 1.15)


def rating_counts(df, ax):
    c = df["rating"].value_counts().sort_index()
    ax.bar(c.index, c.values, color=LIGHT)
    for x, v in c.items():
        ax.text(x, v + 1, str(v), ha="center", fontsize=9)
    ax.set(title="How many books per rating", xlabel="Rating (stars)", ylabel="Books")
    ax.set_ylim(0, c.max() * 1.15)


def category_price(df, ax, n=10):
    g = (df.groupby("category")["price_gbp"].agg(["mean", "count"])
         .query("count >= 10").sort_values("mean").tail(n))
    colors = [ACCENT if i == len(g) - 1 else BLUE for i in range(len(g))]
    ax.barh(g.index, g["mean"], color=colors)
    ax.set(title=f"Priciest categories (mean £, >= 10 books)", xlabel="Mean price (£)")


def category_count(df, ax, n=10):
    c = df["category"].value_counts().head(n).sort_values()
    ax.barh(c.index, c.values, color=LIGHT)
    ax.set(title=f"Largest categories by book count", xlabel="Books")


def stock_scatter(df, ax):
    ax.scatter(df["stock_count"], df["price_gbp"], s=14, alpha=0.4, color=BLUE)
    ax.set(title="Price vs stock level", xlabel="Copies in stock", ylabel="Price (£)")


def main(csv):
    os.makedirs(OUT, exist_ok=True)
    df = pd.read_csv(csv)
    has_cat = "category" in df.columns and df["category"].notna().any()
    has_stock = "stock_count" in df.columns

    # individual charts
    charts = [("01_price_distribution.png", price_hist),
              ("02_price_by_rating.png", rating_bar),
              ("03_rating_counts.png", rating_counts)]
    if has_cat:
        charts += [("04_category_price.png", category_price),
                   ("05_category_count.png", category_count)]
    if has_stock:
        charts.append(("06_price_vs_stock.png", stock_scatter))
    for name, fn in charts:
        fig, ax = plt.subplots(figsize=(7, 4.2))
        fn(df, ax)
        save(name)

    # one-page dashboard
    panels = [price_hist, rating_bar, rating_counts]
    if has_cat:
        panels += [category_price, category_count]
    if has_stock:
        panels.append(stock_scatter)
    ncols = 2
    nrows = -(-len(panels) // ncols)
    fig = plt.figure(figsize=(13, 3.6 * nrows + 1.6))
    gs = fig.add_gridspec(nrows + 1, ncols, height_ratios=[0.45] + [1] * nrows)

    # KPI strip
    kax = fig.add_subplot(gs[0, :])
    kax.axis("off")
    kpis = [("Books", f"{len(df):,}"),
            ("Mean price", f"£{df['price_gbp'].mean():.2f}"),
            ("Median price", f"£{df['price_gbp'].median():.2f}"),
            ("Avg rating", f"{df['rating'].mean():.2f} / 5")]
    if has_cat:
        kpis.append(("Categories", str(df["category"].nunique())))
    for i, (label, val) in enumerate(kpis):
        x = (i + 0.5) / len(kpis)
        kax.text(x, 0.62, val, ha="center", fontsize=20, fontweight="bold", color=BLUE)
        kax.text(x, 0.12, label, ha="center", fontsize=10, color=GREY)

    for i, fn in enumerate(panels):
        fn(df, fig.add_subplot(gs[1 + i // ncols, i % ncols]))
    fig.suptitle("Books to Scrape: Price & Rating Dashboard", fontsize=16, fontweight="bold", y=1.0)
    save("dashboard.png")

    # short data story with computed numbers
    p = df["price_gbp"]
    corr = df["rating"].corr(p, method="spearman")
    story = ["# Data story: what drives book prices?\n",
             f"- **Scope:** {len(df):,} books scraped from Books to Scrape.",
             f"- **Typical price:** median £{p.median():.2f}, middle 50% between "
             f"£{p.quantile(.25):.2f} and £{p.quantile(.75):.2f}.",
             f"- **Rating vs price:** Spearman correlation {corr:.2f} "
             f"({'little to no' if abs(corr) < 0.2 else 'a noticeable'} relationship), "
             "so a higher star rating does not by itself mean a higher price."]
    if has_cat:
        g = df.groupby("category")["price_gbp"].agg(["mean", "count"]).query("count >= 10")
        story.append(f"- **Categories:** highest average price is {g['mean'].idxmax()} "
                     f"(£{g['mean'].max():.2f}), lowest is {g['mean'].idxmin()} (£{g['mean'].min():.2f}).")
    story.append("\n**Decision takeaway:** (write your own 1-2 sentences, e.g. which categories a "
                 "store should stock or price differently, based on the charts.)")
    with open(os.path.join(OUT, "data_story.md"), "w", encoding="utf-8") as f:
        f.write("\n".join(story))
    print(f"Wrote {len(charts)} charts, dashboard.png and data_story.md to {OUT}/")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--csv", default="books.csv")
    main(ap.parse_args().csv)
