#########################################
# MoviesLen数据预处理
# 将原始数据转换为适合推荐系统模型训练的格式
#########################################

import os
import pandas as pd

# 读取用户数据
user_path = "../data/raw/movielens/ml-100k/u.user"
users = pd.read_csv(user_path, sep="|", header=None,
                    names=["user_id", "age", "gender", "occupation", "zip_code"])
# 读取职业全集
occupation_path = "../data/raw/movielens/ml-100k/u.occupation"
occupations = pd.read_csv(occupation_path, header=None, names=["occupation"])

# u.user
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

# 将职业映射为连续的数字
# 建立 {职业名: 连续id} 映射
occupation_map = {occ: idx for idx, occ in enumerate(occupations["occupation"].tolist())}

# 删除zip_code列
users = users.drop(columns=["zip_code", "age"])  # 删除 zip_code 和 age 列

# 映射到 users 表
users["occupation"] = users["occupation"].map(occupation_map)

print(users.head())      # 打印前几行数据
print(users.info()) 

# 保存到../data/processed/movielens/users.csv
os.makedirs("../data/processed/movielens", exist_ok=True)

users.to_csv("../data/processed/movielens/users.csv", index=False)
print("user.csv 保存成功!")
