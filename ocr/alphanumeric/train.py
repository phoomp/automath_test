import copy
import time

import numpy as np
import torch
from torch import nn
from torch.utils.data import TensorDataset, DataLoader
from torchvision.models import resnet50

from fetch_dataset import get_mnist


def train_model(model, train_loader, test_loader, loss_fn, optim, device, epochs=500):
    model = model.to(device)
    start_time = time.perf_counter()

    best_weights = model.state_dict()
    best_acc = 0.0
    best_loss = 1e+10

    print(model.inplanes)

    # Training loop begins
    for epoch in range(epochs):
        epoch_avg_loss = 0.
        correct = 0
        total = 0
        print(f'Epoch {epoch}')
        for i, (img, label) in enumerate(test_loader):
            label = label.type(torch.LongTensor)
            img = img.to(device)
            label = label.to(device)

            # img = img.unsqueeze(0)

            optim.zero_grad()
            outputs = model(img)

            loss = loss_fn(outputs, label)
            loss.backward()
            optim.step()

            label = label.detach().cpu().numpy()
            outputs = nn.LogSoftmax(1)(outputs).detach().cpu()
            outputs = outputs.numpy()

            for o, l in zip(outputs, label):
                o = np.argmax(o)
                total += 1
                if o == l:
                    correct += 1

            epoch_avg_loss += loss.item()

        print('Training:')
        print(f'Accuracy: {((correct / total) * 100):.3f}')
        print(f'Loss: {(epoch_avg_loss / 41):.3f}')

        epoch_avg_loss = 0.
        correct = 0
        total = 0

        for i, (img, label) in enumerate(test_loader):
            label = label.type(torch.LongTensor)
            img = img.to(device)
            label = label.to(device)

            outputs = model(img)
            loss = loss_fn(outputs, label)

            label = label.detach().cpu().numpy()
            outputs = nn.LogSoftmax(1)(outputs).detach().cpu()
            outputs = outputs.numpy()

            for o, l in zip(outputs, label):
                o = np.argmax(o)
                total += 1
                if o == l:
                    correct += 1

            epoch_avg_loss += loss.item()

        print('Validation')
        print(f'Accuracy: {((correct / total) * 100):.3f}')
        print(f'Loss: {(epoch_avg_loss / 41):.3f}')


def main():
    print(torch.__version__)
    device = 'cuda' if torch.cuda.is_available() else 'cpu'

    x, y = get_mnist()
    print(f'Shape of x: {x.shape}')
    n_elements = x.shape[0]
    validation_split = 0.2
    n_train = int(n_elements * validation_split)

    x_train = x[n_train:]
    y_train = y[n_train:]

    x_train = torch.Tensor(x_train).to(device)
    y_train = torch.Tensor(y_train).to(device)
    train_ds = TensorDataset(x_train, y_train)
    train_loader = DataLoader(train_ds, batch_size=1024)

    x_test = x[:n_train]
    y_test = y[:n_train]

    x_test = torch.Tensor(x_test).to(device)
    y_test = torch.Tensor(y_test).to(device)
    test_ds = TensorDataset(x_test, y_test)
    test_loader = DataLoader(test_ds, batch_size=512)

    n_classes = 10

    model = resnet50()
    model.conv1 = nn.Conv2d(1, 64, kernel_size=7, stride=2, padding=3, bias=False)
    # model.inplanes = 28
    in_f = model.fc.in_features
    model.fc = nn.Linear(in_f, n_classes)

    loss_fn = nn.CrossEntropyLoss()
    optimizer = torch.optim.SGD(model.parameters(), lr=1e-4, momentum=0.9)

    train_model(model, train_loader, test_loader, loss_fn, optimizer, device)


if __name__ == '__main__':
    main()