import polars as pl
from transformation.pivot import load_wide_from_db

def split_train_test(wide, last_train_year=2017, last_test_year=2019):
    train = wide.filter(pl.col("year") <= last_train_year)
    test = wide.filter((pl.col("year") > last_train_year) & (pl.col("year") <= last_test_year))
    
    return train, test

if __name__ == '__main__':
    wide = load_wide_from_db()
    train, test = split_train_test(wide)
    print("Train shape:", train.shape)
    print("Test shape:", test.shape)

    baseline = train["unemployment"].mean()
    print("Baseline unemployment mean:", baseline)

    mae = (test["unemployment"] - baseline).abs().mean()
    print("Mean Absolute Error (MAE):", mae)

