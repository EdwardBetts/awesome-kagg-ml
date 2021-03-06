__author__ = 'User'
import pandas as pd
import numpy as np
from os import path, listdir
import Helpers
from sklearn import svm
from sklearn import linear_model
import scipy as sp
from sklearn import cluster
from sklearn.cluster import DBSCAN
from sklearn import metrics
from sklearn.datasets.samples_generator import make_blobs
from sklearn.base import ClassifierMixin, BaseEstimator
from sklearn.ensemble import RandomForestClassifier, BaggingClassifier, AdaBoostClassifier, ExtraTreesClassifier, ExtraTreesRegressor, GradientBoostingClassifier


class EnsembleClassifier(BaseEstimator, ClassifierMixin):
    def __init__(self, classifiers=None):
        self.classifiers = classifiers
        self.predictions_ = list()

    def fit(self, x, y):
        for classifier in self.classifiers:
            classifier.fit(x, y)

    def predict_proba(self, x):
        for classifier in self.classifiers:
            self.predictions_.append(classifier.predict_proba(x))
            m = np.mean(self.predictions_, axis=0)
        return m

def create_submission_file(df):
    """
    Create a submission file for kaggle from a data frame
    """

    # Find file number for new file
    file_num = 0
    while path.isfile('submission-Extra-{}.csv'.format(file_num)):
        file_num += 1

    # Write final submission
    df.to_csv('submission-Extra-{}.csv'.format(file_num), index = False)


def calc_prob(df_features_driver, df_features_other):

    df_train = df_features_driver.append(df_features_other)
    df_train.reset_index(inplace = True)
    df_train.Driver = df_train.Driver.astype(int)

    # So far, the best result was achieved by using a RandomForestClassifier with Bagging
    # model = BaggingClassifier(base_estimator = ExtraTreesClassifier())
    # model = BaggingClassifier(base_estimator = svm.SVC(gamma=2, C=1))
    # model = BaggingClassifier(base_estimator = linear_model.LogisticRegression())
    # model = BaggingClassifier(base_estimator = linear_model.LogisticRegression())
    # model = BaggingClassifier(base_estimator = AdaBoostClassifier())
    #model = RandomForestClassifier(200)
    # model = BaggingClassifier(base_estimator = [RandomForestClassifier(), linear_model.LogisticRegression()])
    # model = EnsembleClassifier([BaggingClassifier(base_estimator = RandomForestClassifier()),
    #                             GradientBoostingClassifier])
    #model = GradientBoostingClassifier(n_estimators = 10000)
    model = ExtraTreesClassifier(n_estimators=100,max_features='auto',random_state=0, n_jobs=2, criterion='entropy', bootstrap=True)
    # model = ExtraTreesClassifier(500, criterion='entropy')

    feature_columns = df_train.iloc[:, 4:]

    # Train the classifier
    model.fit(feature_columns, df_train.Driver)
    df_submission = pd.DataFrame()

    df_submission['driver_trip'] = create_first_column(df_features_driver)

    probs_array = model.predict_proba(feature_columns[:200]) # Return array with the probability for every driver
    probs_df = pd.DataFrame(probs_array)

    df_submission['prob'] = np.array(probs_df.iloc[:, 1])

    return df_submission

def create_first_column(df):
    """
    Create first column for the submission csv, e.g.
    driver_trip
    1_1
    1_2
    """
    return df.Driver.apply(str) + "_" + df.Trip.apply(str)


def main():

    features_path_1 = path.join('..', 'features')
    features_files_1 = listdir(features_path_1)

    #features_path_2 = path.join('..', 'features_2')
    #features_files_2 = listdir(features_path_2)

    # Get data frame that contains each trip with its features
    features_df_list_1 = [pd.read_hdf(path.join(features_path_1, f), key = 'table') for f in features_files_1]
    feature_df_1 = pd.concat(features_df_list_1)

    #features_df_list_2 = [pd.read_hdf(path.join(features_path_2, f), key = 'table') for f in features_files_2]
    #feature_df_2 = pd.concat(features_df_list_2)
    #feature_df_2x = feature_df_2[['Driver', 'Trip', 'mean_speed_times_acceleration', 'pauses_length_mean']]

    # feature_df = pd.merge(feature_df_1, feature_df_2x, on=['Driver', 'Trip'], sort = False)

    feature_df = feature_df_1

    feature_df.reset_index(inplace = True)
    df_list = []

    for i, (_, driver_df) in enumerate(feature_df.groupby('Driver')):

        indeces = np.append(np.arange(i * 200), np.arange((i+1) * 200, len(feature_df)))
        other_trips = indeces[np.random.randint(0, len(indeces) - 1, 200)]
        others = feature_df.iloc[other_trips]
        others.Driver = int(0)

        submission_df = calc_prob(driver_df, others)
        df_list.append(submission_df)

    submission_df = pd.concat(df_list)
    create_submission_file(submission_df)


if __name__ == "__main__":
    main()