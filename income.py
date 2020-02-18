import pandas as pd


def get_parent_category(item):
    global parent_categories
    category = item["Category"]
    return parent_categories[category]


def check_categories(df):
    current_categories = set(df["Category"])
    default_categories_df = pd.read_csv("categories.csv")
    default_categories = set(df["Category"])
    default_N = default_categories_df.shape[0]
    current_N = len(current_categories)
    print(f"Load {default_N} default categories")
    print(f"Load {current_N} current categories")
    child_categories = list(current_categories)
    child_categories.sort()
    diff = current_categories - default_categories
    if len(diff) > 0:
        print("\n[Error] Please update new categories")
        print(diff)
        exit(0)


def load_parent_categories():
    default_categories_df = pd.read_csv("categories.csv")
    output = default_categories_df.set_index('Category').T.to_dict('list')
    result = {}
    for item in output:
        result[item] = output[item][0]
    return result


parent_categories = load_parent_categories()
print("Hello Vu Anh ^-^")
print("\nGenerate Personal Financial Report")
df = pd.read_csv("files/MoneyLover-2020-02-18.csv", sep=";")
check_categories(df)
df["day"] = df.apply(lambda item: item['Date'][:2], axis=1)
df["month"] = df.apply(lambda item: item['Date'][3:5], axis=1)
df["year"] = df.apply(lambda item: item['Date'][6:], axis=1)
df["ParentCategory"] = df.apply(get_parent_category, axis=1)
result = df.groupby(['year', 'month', 'ParentCategory'], as_index=False).agg({"Amount": "sum"})

groups = result.groupby(["year", "month"])
for key, value in groups:
    year, month = key[0], key[1]
    filename = f"files/report-{year}-{month}.xlsx"
    value.to_excel(filename, index=False)
