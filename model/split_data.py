import os
import random
import math

"""
After downloading the dataset, run once
"""

dataset_path = "model/dataset"
split_ratios = [0.8, 0.1, 0.1] # train, val, test

os.mkdir(dataset_path + "/train")
os.mkdir(dataset_path + "/val")
os.mkdir(dataset_path + "/test")

# move everything into "train" directory
for item in os.listdir(dataset_path):
    if not os.path.isdir(f'{dataset_path}/{item}') or item == "train" or item == "val" or item == "test":
        continue

    os.rename(f'{dataset_path}/{item}', f'{dataset_path}/train/{item}')

# select proportion of random images to move into val and test directories per class
for item in os.listdir(f'{dataset_path}/train'):
    if not os.path.isdir(f'{dataset_path}/train/{item}'):
        continue

    os.mkdir(dataset_path + "/test/" + item)
    os.mkdir(dataset_path + "/val/" + item)

    total_samples = len(os.listdir(f'{dataset_path}/train/{item}'))
    val_samples = math.floor(split_ratios[1] * total_samples)
    test_samples = math.floor(split_ratios[2] * total_samples)

    images = [name for name in os.listdir(f'{dataset_path}/train/{item}')]
    random.shuffle(images)
    
    for i in range(val_samples):
        os.rename(f'{dataset_path}/train/{item}/{images[i]}', f'{dataset_path}/val/{item}/{images[i]}')

    for i in range(val_samples, val_samples + test_samples):
        os.rename(f'{dataset_path}/train/{item}/{images[i]}', f'{dataset_path}/test/{item}/{images[i]}')