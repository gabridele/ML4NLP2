"""
This example demonstrates how to use the active learning interface with Pytorch.
The example uses Skorch, a scikit learn wrapper of Pytorch.
For more info, see https://skorch.readthedocs.io/en/stable/
"""

import numpy as np
import torch
from modAL.models import ActiveLearner
from skorch import NeuralNetClassifier
from torch import nn
from torch.utils.data import DataLoader
from torchvision.datasets import KMNIST
from torchvision.transforms import ToTensor


# build class for the skorch API

class VGG11_Dropout(nn.Module):
    def __init__(self, num_classes=10, dropout_enabled=True):
        super(VGG11_Dropout, self).__init__()
        self.dropout_enabled = dropout_enabled

        self.convs = nn.Sequential(
            nn.Conv2d(1, 64, kernel_size=3, padding=1),
            nn.ReLU(),
            nn.Dropout2d(0.25) if dropout_enabled else nn.Identity(),  # Added dropout
            nn.MaxPool2d(2, 2),
            nn.Conv2d(64, 128, kernel_size=3, padding=1),
            nn.ReLU(),
            nn.Dropout2d(0.25) if dropout_enabled else nn.Identity(),  # Added dropout
            nn.MaxPool2d(2, 2),
        )

        self.fc = nn.Sequential(
            nn.Linear(128 * 7 * 7, 256),
            nn.ReLU(),
            nn.Dropout(0.5) if dropout_enabled else nn.Identity(),  # Added dropout
            nn.Linear(256, num_classes)
        )

    def forward(self, x):
        out = self.convs(x)
        out = out.view(out.size(0), -1)
        
        # Apply dropout only during training if enabled
        if self.dropout_enabled:
            out = nn.functional.dropout(out, training=self.training)
        
        out = self.fc(out)
        return out

# create the classifier
device = "cuda" if torch.cuda.is_available() else "cpu"
classifier = NeuralNetClassifier(VGG11_Dropout,
                                 # max_epochs=100,
                                 criterion=nn.CrossEntropyLoss,
                                 optimizer=torch.optim.SGD,
                                 train_split=None,
                                 verbose=1,
                                 device=device)

"""
Data wrangling
1. Reading data from torchvision
2. Assembling initial training data for ActiveLearner
3. Generating the pool
"""

kmnist_data = KMNIST(root='/Users/gabrieledele', download=True, transform=ToTensor())
dataloader = DataLoader(kmnist_data, shuffle=True, batch_size=60000)
X, y = next(iter(dataloader))

# read training data
X_train, X_test, y_train, y_test = X[:50000], X[50000:], y[:50000], y[50000:]
X_train = X_train.reshape(50000, 1, 28, 28)
X_test = X_test.reshape(10000, 1, 28, 28)

# assemble initial data
n_initial = 1000
initial_idx = np.random.choice(range(len(X_train)), size=n_initial, replace=False)
X_initial = X_train[initial_idx]
y_initial = y_train[initial_idx]

# generate the pool
# remove the initial data from the training dataset
X_pool = np.delete(X_train, initial_idx, axis=0)
y_pool = np.delete(y_train, initial_idx, axis=0)


"""
Training the ActiveLearner
"""

# initialize ActiveLearner
learner = ActiveLearner(
    estimator=classifier,
    X_training=X_initial, y_training=y_initial,
)

# the active learning loop
n_queries = 10
for idx in range(n_queries):
    query_idx, query_instance = learner.query(X_pool, n_instances=100)
    learner.teach(X_pool[query_idx], y_pool[query_idx], only_new=True)
    # remove queried instance from pool
    X_pool = np.delete(X_pool, query_idx, axis=0)
    y_pool = np.delete(y_pool, query_idx, axis=0)

# the final accuracy score
print("Learner/Accuracy score is:", learner.score(X_test, y_test))