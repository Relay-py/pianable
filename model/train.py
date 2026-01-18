import random
import os
from PIL import Image
from tqdm import tqdm
from datetime import datetime

import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader
from sklearn.metrics import accuracy_score, precision_recall_fscore_support, confusion_matrix

import torchvision
from torchvision import transforms, datasets


def to_device(obj):
    if torch.cuda.is_available():
        obj = obj.to("cuda")
    elif torch.backends.mps.is_available():
        obj = obj.to("mps")

    return obj


def log_results(file, metrics):
    for metric in metrics:
        file.write(f'{metric}: {metrics[metric]}\t')

    file.write('\n')


def compute_class_weights(train_dir_path):
    counts = {}
    classes = []
    total = 0

    for pose in os.listdir(train_dir_path):
        if not os.path.isdir(f'{train_dir_path}/{pose}'):
            continue
        
        counts[pose] = len(os.listdir(f'{train_dir_path}/{pose}'))
        classes.append(pose)
        total += counts[pose]

    classes.sort()
    weights = [total / (len(classes) * counts[pose]) for pose in classes]
    
    return torch.tensor(weights, dtype=torch.float)
    

def validate(model, val_loader, loss_func):
    model.eval()
    all_preds = []
    all_labels = []
    running_loss = 0.0

    with torch.no_grad():
        for inputs, labels in tqdm(val_loader):
            inputs = to_device(inputs)
            labels = to_device(labels)

            outputs = model(inputs)
            loss = loss_func(outputs, labels)
            running_loss += loss.item()

            _, predictions = torch.max(outputs, 1)

            all_preds.extend(predictions.cpu().numpy())
            all_labels.extend(labels.cpu().numpy())

    average_val_loss = running_loss / len(val_loader)
    acc = accuracy_score(all_labels, all_preds)
    precision, recall, f1, _ = precision_recall_fscore_support(all_labels, all_preds, average='weighted')
    conf_matrix = confusion_matrix(all_labels, all_preds)

    metrics = {
        "accuracy": acc,
        "precision": precision,
        "recall": recall,
        "f1": f1,
        "average_val_loss": average_val_loss,
        "confusion_matrix": conf_matrix
    }

    return metrics


def train(model, num_epochs, train_loader, val_loader, test_loader, loss_func=nn.CrossEntropyLoss(), optimizer=optim.AdamW, optimizer_params=None, runs_dir="model/runs"):
    # create log file
    time = str(datetime.now())
    os.mkdir(runs_dir + "/" + time)
    logfile = open(runs_dir + "/" + time + "/metrics.txt", "a")
    best_accuracy = 0.0

    optimizer = optimizer(filter(lambda p: p.requires_grad, model.parameters()), **optimizer_params)

    # training loop
    for i in range(num_epochs):
        print(f'Epoch {i+1}/{num_epochs}')

        if i == 12:
            print("Switching learning rate")
            for param_group in optimizer.param_groups:
                param_group['lr'] = 1e-4

        model.train()
        running_loss = 0.0
        for inputs, labels in tqdm(train_loader):
            inputs = to_device(inputs)
            labels = to_device(labels)

            optimizer.zero_grad()

            outputs = model(inputs)
            loss = loss_func(outputs, labels)
            loss.backward()
            optimizer.step()

            running_loss += loss.item()

        # print and log metrics
        average_train_loss = running_loss / len(train_loader)
        metrics = validate(model, val_loader, loss_func)
        metrics["average_train_loss"] = average_train_loss
        del metrics["confusion_matrix"]

        print(f'Epoch {i+1} Results:')
        print(f'Train Loss: {average_train_loss}\tValidation Loss: {metrics["average_val_loss"]}')
        print(f'Accuracy: {metrics["accuracy"]}\tPrecision: {metrics["precision"]}\tRecall: {metrics["recall"]}\tF1-score: {metrics["f1"]}')

        log_results(logfile, metrics)

        # save best model
        acc = metrics["accuracy"]
        if acc > best_accuracy:
            torch.save(model.state_dict(), runs_dir + "/" + time + "/best.pt")
            best_accuracy = acc

        torch.save(model.state_dict(), runs_dir + "/" + time + "/last.pt")

    # test model and print/log testing metrics
    print("Testing Model")
    metrics = validate(model, test_loader, loss_func)
    print("Testing Results")
    print(f'Accuracy: {metrics["accuracy"]}\tPrecision: {metrics["precision"]}\tRecall: {metrics["recall"]}\tF1-score: {metrics["f1"]}')
    print(f'Test Loss: {metrics["average_val_loss"]}')

    test_logfile = open(runs_dir + "/" + time + "/test_metrics.txt", "a")
    log_results(test_logfile, metrics)