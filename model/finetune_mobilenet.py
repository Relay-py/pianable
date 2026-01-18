import random

import torch
import torch.nn as nn
from torch.utils.data import DataLoader

import torchvision
from torchvision import transforms, datasets
from torchvision import models

from train import train, compute_class_weights, to_device


random.seed(0)

train_transform = transforms.Compose([
    transforms.RandomHorizontalFlip(p=0.5),
    transforms.Resize((128, 128)),
    transforms.ToTensor(),
    transforms.Normalize(mean=[0.485, 0.456, 0.406],
                         std=[0.229, 0.224, 0.225]),
])

test_transform = transforms.Compose([
    transforms.Resize((128, 128)),
    transforms.ToTensor(),
    transforms.Normalize(mean=[0.485, 0.456, 0.406],
                         std=[0.229, 0.224, 0.225]),
])

dataset_path = "model/dataset/"

train_dataset = datasets.ImageFolder(dataset_path + "train", transform=train_transform)
val_dataset = datasets.ImageFolder(dataset_path + "val", transform=test_transform)
test_dataset = datasets.ImageFolder(dataset_path + "test", transform=test_transform)

batch_size = 32

train_loader = DataLoader(train_dataset, batch_size=batch_size, shuffle=True, num_workers=0)
val_loader = DataLoader(val_dataset, batch_size=batch_size, shuffle=False, num_workers=0)
test_loader = DataLoader(test_dataset, batch_size=batch_size, shuffle=False, num_workers=0)


model = models.mobilenet_v2()

model.classifier[1] = nn.Linear(model.last_channel, 2)
model = to_device(model)

adamW_params = {
    "lr": 1e-3,
    "weight_decay": 1e-2,
    "betas": (0.9, 0.999),
    "eps": 1e-8
}

class_weights = to_device(compute_class_weights(dataset_path + "train"))

train(model, 15, train_loader, val_loader, test_loader, loss_func=nn.CrossEntropyLoss(weight=class_weights), optimizer_params=adamW_params)