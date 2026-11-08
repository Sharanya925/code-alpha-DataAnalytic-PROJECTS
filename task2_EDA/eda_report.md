# EDA Report: Books to Scrape dataset

## 1. Questions we want to answer
1. How are book prices distributed, and are there outliers?
2. Do higher-rated books cost more?
3. Does price differ across categories, and which categories are priciest?
4. Is the data clean (missing values, duplicates, odd values)?
5. Does stock level relate to price or rating?

## 2. Data structure
- Rows: 1000, columns: 10

| column | dtype | missing | unique |
|---|---|---|---|
| title | str | 0 | 999 |
| price_gbp | float64 | 0 | 903 |
| rating | int64 | 0 | 5 |
| in_stock_listing | bool | 0 | 1 |
| url | str | 0 | 1000 |
| category | str | 0 | 50 |
| upc | str | 0 | 1000 |
| num_reviews | int64 | 0 | 1 |
| stock_count | int64 | 0 | 21 |
| description_len | int64 | 0 | 737 |

- Duplicate titles: 1; duplicate URLs: 0

### Summary statistics (numeric)
|       |   price_gbp |   rating |   num_reviews |   stock_count |   description_len |
|:------|------------:|---------:|--------------:|--------------:|------------------:|
| count |     1000    |  1000    |          1000 |       1000    |           1000    |
| mean  |       35.07 |     2.92 |             0 |          8.59 |           1431.63 |
| std   |       14.45 |     1.43 |             0 |          5.65 |            669.32 |
| min   |       10    |     1    |             0 |          1    |              0    |
| 25%   |       22.11 |     2    |             0 |          3    |           1069.75 |
| 50%   |       35.98 |     3    |             0 |          7    |           1348.5  |
| 75%   |       47.46 |     4    |             0 |         14    |           1681.5  |
| max   |       59.99 |     5    |             0 |         22    |           8646    |

## 3. Price distribution and anomalies
- Mean £35.07, median £35.98, std £14.45, range £10.00 to £59.99
- Skewness: -0.04
- IQR outlier fences: £-15.92 to £85.48; outliers found: 0
- Shapiro-Wilk normality test on price: p = 2.62e-17 (not normal)

## 4. Do higher-rated books cost more?
|   rating |   count |   mean |   median |
|---------:|--------:|-------:|---------:|
|        1 |     226 |  34.56 |    34.77 |
|        2 |     196 |  34.81 |    36.22 |
|        3 |     203 |  34.69 |    33.78 |
|        4 |     179 |  36.09 |    37.8  |
|        5 |     196 |  35.37 |    36.9  |

- H0: price is unrelated to rating.
- Spearman rho = 0.029 (p = 0.356); Kruskal-Wallis across rating groups p = 0.815
- Conclusion: fail to reject H0 at alpha = 0.05; no evidence price depends on rating (|rho| = 0.03 is weak).

## 5. Category analysis
- Categories: 50

Top 5 by mean price:

| category   |   count |   mean |   median |
|:-----------|--------:|-------:|---------:|
| Suspense   |       1 |  58.33 |    58.33 |
| Novels     |       1 |  54.81 |    54.81 |
| Politics   |       3 |  53.61 |    52.65 |
| Health     |       4 |  51.45 |    51.34 |
| New Adult  |       6 |  46.38 |    44.18 |

Bottom 5 by mean price:

| category      |   count |   mean |   median |
|:--------------|--------:|-------:|---------:|
| Erotica       |       1 |  19.19 |    19.19 |
| Paranormal    |       1 |  15.4  |    15.4  |
| Adult Fiction |       1 |  15.36 |    15.36 |
| Academic      |       1 |  13.12 |    13.12 |
| Crime         |       1 |  10.97 |    10.97 |

- H0: median price is equal across categories (categories with >= 5 books).
- Kruskal-Wallis p = 0.952 -> fail to reject H0

## 6. Stock, reviews and correlations
|                 |   price_gbp |   rating |   stock_count |   description_len |
|:----------------|------------:|---------:|--------------:|------------------:|
| price_gbp       |        1    |     0.03 |         -0.01 |              0.06 |
| rating          |        0.03 |     1    |          0.02 |              0    |
| stock_count     |       -0.01 |     0.02 |          1    |              0.07 |
| description_len |        0.06 |     0    |          0.07 |              1    |

- Stock vs price: rho = -0.013 (p = 0.674)
- Stock count range: 1 to 22; books with unusually low stock (<= 1): 98
- Note: num_reviews is constant (0) on this site, so it carries no signal.

## 7. Key takeaways
- - Price: books cost £10.00 to £59.99 (mean £35.07, median £35.98). Skewness is -0.04, so the distribution is symmetric. The Shapiro-Wilk test (p = 2.62e-17) shows it is not bell-shaped: prices are spread almost evenly across the range. No outliers were found (0 by the IQR method).
- Rating has almost no effect on price. Average price is £34.56 to £36.09 across 1 to 5 star books (Spearman rho = 0.029, p = 0.356; Kruskal-Wallis p = 0.815), so we fail to reject H0.
- Category does not affect price either (50 categories, Kruskal-Wallis p = 0.952). Many categories have only 1 book, so their averages are unreliable.
- Stock count and description length have almost no correlation with price (Spearman about -0.01 and 0.06).
- Data quality: 1000 rows, 0 missing values, and 1 duplicate title (all URLs and UPCs are unique, so it is probably two different books with the same name). num_reviews is always 0 and in_stock_listing is always True, so they carry no information. Next step: group small categories together, or study how stock levels relate to rating.