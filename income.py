import pandas as pd


def get_parent_category(item):
    global parent_child_categories
    category = item["Category"]
    return parent_child_categories[category]


def check_categories(df):
    current_categories = set(df["Category"])
    default_categories_df = pd.read_csv("default_categories.csv")
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


def load_default_categories():
    default_categories_df = pd.read_csv("default_categories.csv")
    output = default_categories_df.set_index('Category').T.to_dict('list')
    parent_categories = set(default_categories_df["ParentCategory"])
    parent_child_categories = {}
    for item in output:
        parent_child_categories[item] = output[item][0]
    return parent_child_categories, parent_categories


parent_child_categories, parent_categories = load_default_categories()
print("Hello Vu Anh ^-^")
print("\nGenerate Personal Financial Report")
df = pd.read_csv("data/MoneyLover-2020-02-18.csv", sep=";")
check_categories(df)
df["day"] = df.apply(lambda item: item['Date'][:2], axis=1)
df["month"] = df.apply(lambda item: item['Date'][3:5], axis=1)
df["year"] = df.apply(lambda item: item['Date'][6:], axis=1)
df["ParentCategory"] = df.apply(get_parent_category, axis=1)
result = df.groupby(['year', 'month', 'ParentCategory'], as_index=False).agg({"Amount": "sum"})

groups = result.groupby(["year", "month"])
categories_order_list = open("categories_order.txt").read().splitlines()
categories_order = {}
for i, item in enumerate(categories_order_list):
    categories_order[item] = i


def get_order(item):
    category = item["ParentCategory"]
    if category in categories_order:
        return categories_order[category]
    else:
        return 100


for key, value in groups:
    year, month = key[0], key[1]
    filename = f"data/report-{year}-{month}.xlsx"
    current_categories = set(value["ParentCategory"])
    null_categories = set(categories_order_list) - current_categories
    for category in null_categories:
        value = value.append({
            "year": year,
            "month": month,
            "ParentCategory": category,
            "Amount": 0
        }, ignore_index=True)
    value["Order"] = value.apply(get_order, axis=1)
    value["Amount"] = value.apply(lambda item: item["Amount"] if item["Amount"] > 0 else -item["Amount"], axis=1)
    value = value.sort_values(by=['Order'])
    value.to_excel(filename, index=False)
