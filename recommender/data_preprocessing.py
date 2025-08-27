#########################################
# MovieLens 数据预处理
# 将原始数据转换为适合推荐系统模型训练的格式
#########################################

import os
import pandas as pd

# 输出目录
output_dir = "../data/processed/movielens"
os.makedirs(output_dir, exist_ok=True)

# ----------------------------------------
# 1. 处理 u.user 表
# ----------------------------------------

user_path = "../data/raw/movielens/ml-100k/u.user"
users = pd.read_csv(user_path, sep="|", header=None,
                    names=["user_id", "age", "gender", "occupation", "zip_code"])

# 年龄 -> 映射为年龄段
def age_to_group(age):
    if age < 18:
        return 0
    elif age < 25:
        return 1
    elif age < 35:
        return 2
    elif age < 45:
        return 3
    elif age < 55:
        return 4
    else:
        return 5
    
users['age_group'] = users['age'].apply(age_to_group)

# 性别 -> 0/1
users["gender"] = users["gender"].map({"M": 0, "F": 1})

# occupation -> one-hot (0/1)
occupation_onehot = pd.get_dummies(users["occupation"], prefix="occ").astype(int)

# 删除无用列
users = users.drop(columns=["zip_code", "age", "occupation"])

# 合并 one-hot
users_final = pd.concat([users, occupation_onehot], axis=1)

# 保存
users_final.to_csv(f"{output_dir}/users.csv", index=False)
print("users.csv 保存成功!")
print(users_final.head())


# ----------------------------------------
# 2. 处理 u.item 表
# ----------------------------------------

# 读取 genre 列表
genre_path = "../data/raw/movielens/ml-100k/u.genre"
genres = pd.read_csv(genre_path, sep="|", header=None, names=["genre", "genre_id"])
genres = genres.dropna()
genre_list = genres["genre"].tolist()

# 读取 u.item
item_path = "../data/raw/movielens/ml-100k/u.item"
items = pd.read_csv(
    item_path,
    sep="|",
    header=None,
    encoding="latin-1",
    names=[
        "movie_id", "title", "release_date", "video_release_date", "IMDb_URL"
    ] + genre_list
)

# 提取 genres 列表
def extract_genres(row):
    return [genre for genre in genre_list if row[genre] == 1]

items["genres"] = items.apply(extract_genres, axis=1)

# 删除 title 中年份
items["title"] = items["title"].str.replace(r" \(\d{4}\)$", "", regex=True)

# 删除无用列
items = items.drop(columns=["video_release_date", "IMDb_URL", "release_date"])

# 生成 genres_str
items["genres_str"] = items["genres"].apply(lambda x: ",".join(x))

# 拼接最终表：movie_id, title, genres_str + multi-hot
genre_df = items[genre_list].copy()
items_final = pd.concat([items[["movie_id", "title", "genres_str"]], genre_df], axis=1)

# 保存
items_final.to_csv(f"{output_dir}/items.csv", index=False)
print("items.csv 保存成功!")
print(items_final.head())

# ----------------------------------------
# 处理u.data表
# ----------------------------------------
data_path = "../data/raw/movielens/ml-100k/u.data"
datas = pd.read_csv(
    data_path,
    sep="\t",           # 这里改成 tab
    header=None,
    names=["user_id", "movie_id", "rating", "timestamp"]
)

# 删除 timestamp 列
datas = datas.drop(columns=["timestamp"])

# 保存
datas.to_csv(f"{output_dir}/ratings.csv", index=False)
print("ratings.csv 保存成功!")
print(datas.head())

