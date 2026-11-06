"""Train a small classifier on the built-in iris dataset.

Nothing is saved to disk. Tests import train(). Run this file to print the test accuracy.
"""
from sklearn.datasets import load_iris
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler

SEED = 0


def load_data():
    return load_iris(return_X_y=True)


def train(seed=SEED):
    X, y = load_data()
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.3, stratify=y, random_state=seed
    )
    model = make_pipeline(StandardScaler(), LogisticRegression(max_iter=1000, random_state=seed))
    model.fit(X_train, y_train)
    return model, X_test, y_test


def main():
    model, X_test, y_test = train()
    print(f"test accuracy: {model.score(X_test, y_test):.3f}")


if __name__ == "__main__":
    main()
