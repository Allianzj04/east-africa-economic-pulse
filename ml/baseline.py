import polars as pl
from transformation.pivot import load_wide_from_db
from ml.split import split_train_test

def mean_baseline_mae(train, test):
    baseline = train["unemployment"].mean()
    mae = (test["unemployment"] - baseline).abs().mean()
    return baseline, mae

def country_mean_baseline_mae(train, test):
    country_means = train.group_by("country").agg(pl.col("unemployment").mean().alias("baseline"))
    test_with_baseline = test.join(country_means, on="country", how="left")
    mae = (test_with_baseline["unemployment"] - test_with_baseline["baseline"]).abs().mean()
    
    return country_means, mae

if __name__ == '__main__':
    wide = load_wide_from_db()
    train, test = split_train_test(wide)
    baseline, mae_global = mean_baseline_mae(train, test)
    print("Baseline unemployment mean:", baseline)
    print("MAE (global-mean baseline):", mae_global)

    country_means, mae_country = country_mean_baseline_mae(train, test)
    print("Country means:\n", country_means)
    print("MAE (country-mean baseline):", mae_country)