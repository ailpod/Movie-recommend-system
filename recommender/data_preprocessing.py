#########################################
# MovieLens 数据预处理脚本（重构版）
# 输出：users.csv（含偏好特征）、items.csv、ratings.csv
#########################################

import os
import pandas as pd
import re

# 输出目录
output_dir = "../data/processed/movielens"
database_output_dir = "../data/database_data"
os.makedirs(output_dir, exist_ok=True)

# ===================== 数据集读取 =====================
# 路径定义
genre_path = "../data/raw/movielens/ml-100k/u.genre"
item_path = "../data/raw/movielens/ml-100k/u.item"
data_path = "../data/raw/movielens/ml-100k/u.data"
user_path = "../data/raw/movielens/ml-100k/u.user"

# 读取数据
# 1. 电影类型表
genres = pd.read_csv(genre_path, sep="|", header=None, names=["genre", "genre_id"])
genres = genres.dropna()
genre_list = genres["genre"].tolist()

# 2. 电影信息表
items = pd.read_csv(
    item_path,
    sep="|",
    header=None,
    encoding="latin-1",
    names=["movie_id", "title", "release_date", "video_release_date", "IMDb_URL"] + genre_list
)

# 3. 用户评分表
ratings = pd.read_csv(
    data_path,
    sep="\t",
    header=None,
    names=["user_id", "movie_id", "rating", "timestamp"]
)
ratings = ratings.drop(columns=["timestamp"])

# 4. 用户信息表
users = pd.read_csv(
    user_path,
    sep="|",
    header=None,
    names=["user_id", "age", "gender", "occupation", "zip_code"]
)

# ======= 用户id和电影id重新编号（从0开始） =======
user_id_mapping = {id: idx for idx, id in enumerate(sorted(users['user_id'].unique()))}
movie_id_mapping = {id: idx for idx, id in enumerate(sorted(items['movie_id'].unique()))}

users['user_id'] = users['user_id'].map(user_id_mapping)
ratings['user_id'] = ratings['user_id'].map(user_id_mapping)
ratings['movie_id'] = ratings['movie_id'].map(movie_id_mapping)
items['movie_id'] = items['movie_id'].map(movie_id_mapping)
# 后续所有表格处理都用新的users、ratings、items

# -------------------------------
# 1. 处理 u.genre -> 生成 genre_list
# -------------------------------

# -------------------------------
# 2. 处理 u.item -> items.csv
# -------------------------------
# 提取 genres 列（multi-hot -> list）
items["genres"] = items.apply(lambda row: [g for g in genre_list if row[g] == 1], axis=1)

# 删除 title 中的年份
items["title"] = items["title"].str.replace(r" \(\d{4}\)$", "", regex=True)

# 删除无用列
items = items.drop(columns=["video_release_date", "IMDb_URL", "release_date"])

# 生成 genres_str
items["genres_str"] = items["genres"].apply(lambda x: ",".join(x))

# 拼接最终表：movie_id, title, genres_str + multi-hot
items_final = pd.concat([items[["movie_id", "title", "genres_str"]], items[genre_list]], axis=1)

# 保存
items_final.to_csv(f"{output_dir}/items.csv", index=False)
print("items.csv 保存成功!")
print(items_final.head())

# -------------------------------
# 3. 处理 u.data -> ratings.csv
# -------------------------------

# 保存
ratings.to_csv(f"{output_dir}/ratings.csv", index=False)
print("ratings.csv 保存成功!")
print(ratings.head())

# -------------------------------
# 4. 处理 u.user -> users.csv（含偏好特征）
# -------------------------------

# 年龄 -> 年龄段
def age_to_group(age):
    if age < 18: return 0
    elif age < 25: return 1
    elif age < 35: return 2
    elif age < 45: return 3
    elif age < 55: return 4
    else: return 5

users["age_group"] = users["age"].apply(age_to_group)

# 性别 -> 0/1
users["gender"] = users["gender"].map({"M": 0, "F": 1})

# 职业 -> one-hot
occupation_onehot = pd.get_dummies(users["occupation"], prefix="occ").astype(int)

# 删除无用列
users = users.drop(columns=["age", "occupation", "zip_code"])

# 合并 one-hot
users_final = pd.concat([users, occupation_onehot], axis=1)

# -------------------------------
# 5. 生成用户偏好特征（加权平均）
# -------------------------------
# 电影类型特征
movie_genres = items_final[["movie_id"] + genre_list]

# 合并评分和电影类型
ratings_with_genres = ratings.merge(movie_genres, on="movie_id", how="left")

# 按用户分组，计算加权平均
def weighted_avg(x):
    return (x[genre_list].multiply(x["rating"], axis=0).sum()) / x["rating"].sum()

user_pref = ratings_with_genres.groupby("user_id").apply(weighted_avg).reset_index()
user_pref.columns = ["user_id"] + [f"pref_{g}" for g in genre_list]

# 合并到用户表
users_final = users_final.merge(user_pref, on="user_id", how="left").fillna(0)

# 将用户偏好特征的小数点保留两位
users_final[[f"pref_{g}" for g in genre_list]] = users_final[[f"pref_{g}" for g in genre_list]].round(2)

# 保存
users_final.to_csv(f"{output_dir}/users.csv", index=False)
print("users.csv 保存成功! (含用户偏好特征)")
print(users_final.head())


# 计算偏好的最大值，最小值，平均值
pref_stats = users_final[[f"pref_{g}" for g in genre_list]].agg(['min', 'max', 'mean']).T
pref_stats.columns = ['min', 'max', 'mean']
# 打印
print("用户偏好特征统计:")
print(pref_stats)

# -------------------------------
# 6. 生成数据库用用户表（user_id, age_group, gender, favorite_genres）
# -------------------------------

def top3_genres(row):
    # 取 pref_ 列
    pref_cols = [f"pref_{g}" for g in genre_list]
    # 排序取前三
    top_genres = row[pref_cols].sort_values(ascending=False).head(3).index
    # 去掉 "pref_" 前缀
    top_genres = [g.replace("pref_", "") for g in top_genres]
    return ",".join(top_genres)

users_db = users_final.copy()
users_db["favorite_genres"] = users_db.apply(top3_genres, axis=1)

# 只保留需要的列
users_db = users_db[["user_id", "age_group", "gender", "favorite_genres"]]

# 保存到 database 文件夹
os.makedirs(database_output_dir, exist_ok=True)
users_db.to_csv(f"{database_output_dir}/users.csv", index=False)
print("数据库用 users.csv 保存成功!")
print(users_db.head())


# -------------------------------
# 6. 生成数据库用电影表（movie_id, year, genres, reviewer_num）
# -------------------------------
# 提取年份
def extract_year(title):
    m = re.search(r"\((\d{4})\)$", title)
    if m:
        return int(m.group(1))
    else:
        return None

# items_original 中 title 还带年份
items_original = pd.read_csv(item_path, sep="|", header=None, encoding="latin-1",
                             names=["movie_id", "title", "release_date", "video_release_date", "IMDb_URL"] + genre_list)

# 使用映射后的movie_id
items_original['movie_id'] = items_original['movie_id'].map(movie_id_mapping)

items_db = items_original.copy()
items_db["year"] = items_db["release_date"].str.extract(r"(\d{4})")  # 字符串
items_db["year"] = items_db["year"].astype(pd.Int64Dtype())          # 转整数类型，支持 NaN
items_db["genres"] = items_db.apply(lambda row: ",".join([g for g in genre_list if row[g]==1]), axis=1)

# 计算 reviewer_num（评分人数）
reviewer_count = ratings.groupby("movie_id").size().reset_index(name="reviewer_num")

# 合并
items_db = items_db.merge(reviewer_count, on="movie_id", how="left").fillna(0)
items_db["reviewer_num"] = items_db["reviewer_num"].astype(int)

# 只保留需要的列
items_db = items_db[["movie_id", "year", "genres", "reviewer_num"]]

# 保存到 database 文件夹
items_db.to_csv(f"{database_output_dir}/items.csv", index=False)
print("数据库用 movies.csv 保存成功!")
print(items_db.head())

# -------------------------------
# 6. 生成数据库用评分表（user_id, movie_id, rating）
# -------------------------------
ratings_db = ratings.copy()
# 保存到 database 文件夹
ratings_db.to_csv(f"{database_output_dir}/ratings.csv", index=False)
print("数据库用 ratings.csv 保存成功!")
print(ratings_db.head())


