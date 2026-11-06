"""Model tests for the iris classifier in train.py. Run from this folder with: pytest -q"""
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from train import load_data, train  # noqa: E402

ACCURACY_THRESHOLD = 0.90
VALID_LABELS = {0, 1, 2}


def test_accuracy_is_above_threshold():
    model, X_test, y_test = train()
    assert model.score(X_test, y_test) >= ACCURACY_THRESHOLD


def test_same_seed_gives_same_predictions():
    model_a, X_test, _ = train(seed=0)
    model_b, _, _ = train(seed=0)
    assert np.array_equal(model_a.predict(X_test), model_b.predict(X_test))


def test_one_prediction_per_row():
    model, X_test, _ = train()
    assert model.predict(X_test).shape == (len(X_test),)


def test_predicted_labels_are_valid():
    model, X_test, _ = train()
    assert set(model.predict(X_test).tolist()) <= VALID_LABELS


def test_no_nan_in_predictions_or_probabilities():
    model, X_test, _ = train()
    probabilities = model.predict_proba(X_test)
    assert np.isfinite(probabilities).all()
    assert not np.isnan(model.predict(X_test).astype(float)).any()


def test_probabilities_sum_to_one():
    model, X_test, _ = train()
    assert np.allclose(model.predict_proba(X_test).sum(axis=1), 1.0)


def test_each_species_average_is_predicted_as_that_species():
    # A boundary-style check: the average flower of each species should be
    # classified as that species. It is a typical point, not a guarantee.
    model, _, _ = train()
    X, y = load_data()
    for species in VALID_LABELS:
        centre = X[y == species].mean(axis=0).reshape(1, -1)
        assert model.predict(centre)[0] == species


def test_dataset_quality():
    X, y = load_data()
    assert X.shape == (150, 4)
    assert not np.isnan(X).any()
    assert [int((y == k).sum()) for k in sorted(VALID_LABELS)] == [50, 50, 50]
