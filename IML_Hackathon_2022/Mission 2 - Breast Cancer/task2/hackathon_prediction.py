import warnings
from hackathon_model import EstimatorTask0, EstimatorTask1
from hackathon_preprocessing import PreProcess
import numpy as np
import pandas as pd
from sklearn.preprocessing import MultiLabelBinarizer
from sklearn.metrics import f1_score, mean_squared_error

warnings.simplefilter(action='ignore', category=Warning)

y0_num_to_label = {0: 'BON - Bones', 1: 'LYM - Lymph nodes',
                   2: 'HEP - Hepatic', 3: 'PUL - Pulmonary',
                   4: 'PLE - Pleura', 5: 'SKI - Skin', 6: 'BRA - Brain',
                   7: 'MAR - Bone Marrow',
                   8: 'ADR - Adrenals', 9: 'PER - Peritoneum',
                   10: 'OTH - Other'}


def return_to_format(y_pred, test_unique_count):
    new_pred = []
    for i, count in enumerate(test_unique_count):
        for j in range(count):
            new_pred.append(y_pred[i])
    return new_pred


def evaluate_and_export(estimator, X: np.ndarray, type, filename: str, test_unique_count):
    """
    Export to specified file the prediction results of given estimator on given testset.

    File saved is in csv format with a single column named 'predicted_values' and n_samples rows containing
    predicted values.

    Parameters
    ----------
    estimator: BaseEstimator or any object implementing predict() method as in BaseEstimator (for example sklearn)
        Fitted estimator to use for prediction

    X: ndarray of shape (n_samples, n_features)
        Test design matrix to predict its responses

    filename:
        path to store file at

    """
    y_pred = estimator.predict(X)
    title = 'tumor_size'
    if type == 0:
        y_pred = translate_to_label(y_pred)
        title = 'location_of_distal_metastases'
    y_pred = return_to_format(y_pred, test_unique_count)
    pd.DataFrame(y_pred, columns=[title]).to_csv(filename, index=False, na_rep='[]')


def translate_to_label(response):
    newResponse = []
    for sampleResponse in response:
        indexes_of_yes = np.where(sampleResponse == 1)[0]
        currentSample = []
        if len(indexes_of_yes) != 0:
            for label in indexes_of_yes:
                currentSample.append(str(y0_num_to_label[label]))
            newResponse.append([currentSample])
        else:
            newResponse.append(currentSample)
    return newResponse


if __name__ == '__main__':
    np.random.seed(0)
    p = PreProcess("data/train.feats.csv", "data/test.feats.csv",
                   "data/train.labels.0.csv", "data/train.labels.1.csv")
    p.process()
    trainX, testX, trainY0, trainY1 = p.get_train_test()
    trainX = trainX.reset_index(drop=True)
    testX = testX.reset_index(drop=True)
    trainX = trainX.to_numpy()
    testX = testX.to_numpy()
    trainY0 = MultiLabelBinarizer().fit_transform(trainY0)

    estimator_0 = EstimatorTask0()
    estimator_0.fit(trainX, trainY0)
    evaluate_and_export(estimator_0, testX, 0, "part1/predictions.csv", p.get_unique_and_counts())

    estimator_1 = EstimatorTask1()
    estimator_1.fit(trainX, trainY1)
    evaluate_and_export(estimator_1, testX, 1, "part2/predictions.csv", p.get_unique_and_counts())
