"""
Task 2: Exploratory Data Analysis (EDA)  (CodeAlpha Data Analytics internship)

Runs on the dataset produced by scraper.py (books.csv).

Usage:
    python eda.py                    # reads books.csv, writes eda_output/
    python eda.py --csv other.csv

Outputs (in eda_output/): PNG charts + eda_report.md (numbers filled in automatically)
Requires: pandas, numpy, matplotlib, seaborn, scipy
"""
import argparse
import os

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
from scipy import stats

sns.set_theme(style="whitegrid", context="notebook")
OUT = "eda_output"
lines = []  # report lines


def say(text=""):
    print(text)
    lines.append(text)


def save(fig_name):
    plt.tight_layout()
    plt.savefig(os.path.join(OUT, fig_name), dpi=150)
    plt.close()


def main(csv):
    os.makedirs(OUT, exist_ok=True)
    df = pd.read_csv(csv)
    has_cat = "category" in df.columns and df["category"].notna().any()
    has_stock = "stock_count" in df.columns

    say("# EDA Report: Books to Scrape dataset\n")
    say("## 1. Questions we want to answer")
    say("1. How are book prices distributed, and are there outliers?")
    say("2. Do higher-rated books cost more?")
    if has_cat:
        say("3. Does price differ across categories, and which categories are priciest?")
    say("4. Is the data clean (missing values, duplicates, odd values)?")
    if has_stock:
        say("5. Does stock level relate to price or rating?")

    # ---- 2. structure
    say("\n## 2. Data structure")
    say(f"- Rows: {len(df)}, columns: {df.shape[1]}")
    say("\n| column | dtype | missing | unique |\n|---|---|---|---|")
    for c in df.columns:
        say(f"| {c} | {df[c].dtype} | {df[c].isna().sum()} | {df[c].nunique()} |")
    dup_titles = df["title"].duplicated().sum()
    dup_urls = df["url"].duplicated().sum() if "url" in df else 0
    say(f"\n- Duplicate titles: {dup_titles}; duplicate URLs: {dup_urls}")
    say("\n### Summary statistics (numeric)")
    say(df.describe().round(2).to_markdown())

    # ---- 3. price distribution + outliers
    say("\n## 3. Price distribution and anomalies")
    p = df["price_gbp"]
    q1, q3 = p.quantile([0.25, 0.75])
    iqr = q3 - q1
    lo, hi = q1 - 1.5 * iqr, q3 + 1.5 * iqr
    outliers = df[(p < lo) | (p > hi)]
    say(f"- Mean £{p.mean():.2f}, median £{p.median():.2f}, std £{p.std():.2f}, "
        f"range £{p.min():.2f} to £{p.max():.2f}")
    say(f"- Skewness: {stats.skew(p):.2f}")
    say(f"- IQR outlier fences: £{lo:.2f} to £{hi:.2f}; outliers found: {len(outliers)}")
    sw_n = min(len(p), 5000)
    sw = stats.shapiro(p.sample(sw_n, random_state=0))
    say(f"- Shapiro-Wilk normality test on price: p = {sw.pvalue:.3g} "
        f"({'not normal' if sw.pvalue < 0.05 else 'consistent with normal'})")

    fig, ax = plt.subplots(1, 2, figsize=(11, 4))
    sns.histplot(p, bins=30, kde=True, ax=ax[0], color="#3b6ea5")
    ax[0].set(title="Price distribution", xlabel="Price (£)")
    sns.boxplot(x=p, ax=ax[1], color="#9db8d6")
    ax[1].set(title="Price box plot", xlabel="Price (£)")
    save("01_price_distribution.png")

    # ---- 4. rating vs price (hypothesis test)
    say("\n## 4. Do higher-rated books cost more?")
    rating_stats = df.groupby("rating")["price_gbp"].agg(["count", "mean", "median"]).round(2)
    say(rating_stats.to_markdown())
    rho, p_rho = stats.spearmanr(df["rating"], df["price_gbp"])
    groups = [g["price_gbp"].values for _, g in df.groupby("rating")]
    kw = stats.kruskal(*groups)
    say(f"\n- H0: price is unrelated to rating.")
    say(f"- Spearman rho = {rho:.3f} (p = {p_rho:.3g}); Kruskal-Wallis across rating groups p = {kw.pvalue:.3g}")
    say(f"- Conclusion: {'reject H0' if p_rho < 0.05 else 'fail to reject H0'} at alpha = 0.05; "
        f"{'a relationship exists' if p_rho < 0.05 else 'no evidence price depends on rating'} "
        f"(|rho| = {abs(rho):.2f} is {'weak' if abs(rho) < 0.3 else 'moderate/strong'}).")

    fig, ax = plt.subplots(1, 2, figsize=(11, 4))
    sns.countplot(x="rating", data=df, ax=ax[0], color="#3b6ea5")
    ax[0].set(title="Books per star rating", xlabel="Rating (stars)", ylabel="Books")
    sns.boxplot(x="rating", y="price_gbp", data=df, ax=ax[1], color="#9db8d6")
    ax[1].set(title="Price by rating", xlabel="Rating (stars)", ylabel="Price (£)")
    save("02_rating_vs_price.png")

    # ---- 5. category analysis
    if has_cat:
        say("\n## 5. Category analysis")
        cat = (df.groupby("category")["price_gbp"].agg(["count", "mean", "median"])
               .round(2).sort_values("mean", ascending=False))
        say(f"- Categories: {len(cat)}")
        say("\nTop 5 by mean price:\n")
        say(cat.head(5).to_markdown())
        say("\nBottom 5 by mean price:\n")
        say(cat.tail(5).to_markdown())
        big = [g["price_gbp"].values for _, g in df.groupby("category") if len(g) >= 5]
        kwc = stats.kruskal(*big)
        say(f"\n- H0: median price is equal across categories (categories with >= 5 books).")
        say(f"- Kruskal-Wallis p = {kwc.pvalue:.3g} -> "
            f"{'reject H0: price differs by category' if kwc.pvalue < 0.05 else 'fail to reject H0'}")

        top = cat[cat["count"] >= 10].head(10).reset_index()
        plt.figure(figsize=(8, 5))
        sns.barplot(y="category", x="mean", data=top, color="#3b6ea5")
        plt.title("Mean price, top 10 categories (>= 10 books)")
        plt.xlabel("Mean price (£)"); plt.ylabel("")
        save("03_category_mean_price.png")

    # ---- 6. stock and correlations
    if has_stock:
        say("\n## 6. Stock, reviews and correlations")
        num = df.select_dtypes("number")
        num = num.loc[:, num.nunique() > 1]  # constant columns have no correlation
        corr = num.corr(method="spearman").round(2)
        say(corr.to_markdown())
        plt.figure(figsize=(6, 5))
        sns.heatmap(corr, annot=True, cmap="vlag", center=0, vmin=-1, vmax=1)
        plt.title("Spearman correlation")
        save("04_correlation_heatmap.png")

        r2, p2 = stats.spearmanr(df["stock_count"], df["price_gbp"])
        say(f"\n- Stock vs price: rho = {r2:.3f} (p = {p2:.3g})")
        say(f"- Stock count range: {df['stock_count'].min()} to {df['stock_count'].max()}; "
            f"books with unusually low stock (<= 1): {(df['stock_count'] <= 1).sum()}")
        if "num_reviews" in df and df["num_reviews"].nunique() == 1:
            say(f"- Note: num_reviews is constant ({df['num_reviews'].iloc[0]}) on this site, so it carries no signal.")

    say("\n## 7. Key takeaways")
    say("- (Fill in after reading the numbers above: shape of price distribution, whether rating/"
        "category drive price, any anomalies found, and what you would investigate next.)")

    with open(os.path.join(OUT, "eda_report.md"), "w", encoding="utf-8") as f:
        f.write("\n".join(lines))
    print(f"\nWrote charts and eda_report.md to {OUT}/")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--csv", default="books.csv")
    main(ap.parse_args().csv)
