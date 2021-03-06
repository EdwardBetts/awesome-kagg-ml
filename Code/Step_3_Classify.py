from __future__ import division
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
from sklearn.ensemble import RandomForestClassifier,AdaBoostClassifier, ExtraTreesClassifier, GradientBoostingClassifier, GradientBoostingRegressor
import multiprocessing as mp
import warnings
import operator
from sklearn.linear_model import Lasso, LassoCV
from sklearn import grid_search

# warnings.filterwarnings("ignore")

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

#     df[['prob']] = df[['prob']] / np.max(df[['prob']])

    # Find file number for new file
    file_num = 0
    while path.isfile('submission-89-{}.csv'.format(file_num)):
        file_num += 1

    # Write final submission
    df.to_csv('submission-89-{}.csv'.format(file_num), index = False)


def classify(f, df_list):

    feature_df = pd.read_hdf("/scratch/vstrobel/features_opti_32/" + f, key = 'table')
    feature_df.reset_index(inplace = True)
    feature_df['Driver'] = feature_df.Driver.astype('int')
    feature_df['Trip'] = feature_df.Trip.astype('int')
    sorted_df = feature_df.sort(['Driver', 'Trip'])

    calculated = []

    for i, (d, driver_df) in enumerate(sorted_df.groupby('Driver')):

        amount_others = 200    
        indeces = np.append(np.arange(i * 200), np.arange((i+1) * 200, len(feature_df)))
        other_trips = indeces[np.random.randint(0, len(indeces) - 1, amount_others)]
        others = feature_df.iloc[other_trips]
        others.Driver = np.repeat(int(0), amount_others)
    
        submission_df = calc_prob(driver_df, others)
        calculated.append(submission_df)

    df_list.append(pd.concat(calculated))

def calc_prob(df_features_driver, df_features_other):

    df_train = df_features_driver.append(df_features_other)
    df_train.reset_index(inplace = True)
    df_train.Driver = df_train.Driver.astype(int)


#    model = RandomForestClassifier(n_estimators=5000, min_samples_leaf=2, max_depth=5)

#    model = EnsembleClassifier([RandomForestClassifier(n_estimators=500, min_samples_leaf=2, max_depth=5),
#                                GradientBoostingClassifier(n_estimators=500, min_samples_leaf=2, max_depth=4, subsample = 0.7)])         


#     model = LassoCV()

    parameters = {'criterion': ['gini', 'entropy'], 'n_estimators': [500, 700, 900], 'max_features' : ['log2', 'sqrt']}

    clf = RandomForestClassifier()
    model = grid_search.GridSearchCV(clf, parameters)

    feature_columns = df_train.iloc[:, 4:]

    # Train the classifier
    model.fit(feature_columns, df_train.Driver)
        
    print(model.best_params_)

    df_submission = pd.DataFrame()

    df_submission['driver_trip'] = create_first_column(df_features_driver)

    probs_array = model.predict_proba(feature_columns[:200]) # Return array with the probability for every driver
    # probs_array = model.predict(feature_columns[:200])
    
    probs_df = pd.DataFrame(probs_array)

    df_submission['prob'] = np.array(probs_df.iloc[:, 1])
#    df_submission['prob'] = np.array(probs_df)

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

    features_path = "/scratch/vstrobel/features_opti_32/"
    features_files = sorted(listdir(features_path))

    # Get data frame that contains each trip with its features
    
    manager = mp.Manager()
    df_list = manager.list()

    jobs = []

    for f in features_files:
        p = mp.Process(target = classify, args = (f, df_list, ))
        jobs.append(p)
        p.start()
        
    [job.join() for job in jobs]

    final_list = []

    for l in df_list:
        final_list.append(l)

    submission_df = pd.concat(final_list)
    create_submission_file(submission_df)

if __name__ == "__main__":
    main()
