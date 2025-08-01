# create_configs.py

import os

names = [
    "anthropology",
    "bankers",
    "biology_expert",
    "doctors_md",
    "junior_corporate_lawyer",
    "mathematics_phd",
    "quantitative_finance",
    "radiology",
    "tax_lawyer",
    "mechanical_engineers",
]

# 1) Make sure the directory exists
os.makedirs("configs", exist_ok=True)

# 2) Create each stub file
for name in names:
    path = os.path.join("configs", f"{name}.yml")
    with open(path, "w") as f:
        f.write("hard: {}\nsoft: {}\n")
 
print("✅ Created stub configs in ./configs/")
 