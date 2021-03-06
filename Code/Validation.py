import pandas as pd
import numpy as np
from os import path, listdir
import matplotlib.pyplot as plt
import time
import Helpers
import AUC
from sklearn import svm
from sklearn import linear_model
import scipy as sp
from sklearn import cluster
from sklearn.cluster import DBSCAN
from sklearn import metrics
from sklearn.datasets.samples_generator import make_blobs
from sklearn.ensemble import RandomForestClassifier, BaggingClassifier, AdaBoostClassifier, ExtraTreesClassifier

def validation(df_features_driver, df_features_other_train, df_features_other_test):

    df_train = df_features_driver.append(df_features_other_train)
    df_train.reset_index(inplace = True)
    df_train.Driver = df_train.Driver.astype(int)
    
    df_test = df_features_driver.append(df_features_other_test)
    df_test.reset_index(inplace = True)
    df_test.Driver = df_test.Driver.astype(int)

    # So far, the best result was achieved by using a RandomForestClassifier with Bagging
    # model = BaggingClassifier(base_estimator = ExtraTreesClassifier())
    # model = BaggingClassifier(base_estimator = svm.SVC(gamma=2, C=1))
    # model = BaggingClassifier(base_estimator = linear_model.LogisticRegression())
    # model = BaggingClassifier(base_estimator = linear_model.LogisticRegression())
    # model = BaggingClassifier(base_estimator = AdaBoostClassifier())
    # model = RandomForestClassifier()
    model = BaggingClassifier(base_estimator = RandomForestClassifier(n_estimators=10, max_depth=None, min_samples_split=1, random_state=0))
    feature_columns_train= df_train.iloc[:, 4:]
    feature_columns_test= df_test.iloc[:, 4:]

    # Train the classifier
    model.fit(feature_columns_train, df_train.Driver)
    
    probs_array = model.predict_proba(feature_columns_test) # Return array with the probability for every driver
    probs_df = pd.DataFrame(probs_array)

    probs_list = np.array(['1', probs_df.ix[0, 1]])
    for x in range(1, 200):
        # Column 1 should contain the driver of interest
        probs_list = np.vstack((probs_list, ['1', probs_df.ix[x, 1]]))
    for x in range(200,len(probs_df)):
        # Column 1 should contain the driver of interest
        probs_list = np.vstack((probs_list, ['0', probs_df.ix[x, 1]]))
    
    
    df_auc = AUC.AUC(probs_list)    
    
    return df_auc  
    
    
def main():

    features_path = path.join('..', 'features')
    features_files = listdir(features_path)

    # Get data frame that contains each trip with its features
    features_df_list = [pd.read_hdf(path.join(features_path, f), key = 'table') for f in features_files]
    feature_df = pd.concat(features_df_list)
    feature_df.reset_index(inplace = True)
    df_list = []
    nAnom = 200
    t0 = time.time()    
    
    for i, (_, driver_df) in enumerate(feature_df.groupby('Driver')):
        
        print(driver_df)
        break
        indeces = np.append(np.arange(0,int(i)*200,1),np.arange((int(i)+1)*200,len(feature_df),1))
        # Get 400 other trips
        other_trips = indeces[np.random.randint(0, len(indeces) - 1, 200)]
        other_trips_2 = indeces[np.random.randint(0, len(indeces) - 1, nAnom)]

        others = feature_df.iloc[other_trips]
        others_2 = feature_df.iloc[other_trips_2]

        others.Driver = int(0)
        others_2.Driver = int(0)

        validation_df = validation(driver_df, others, others_2)
        df_list.append(validation_df)
        print(time.time() - t0)
        

    plt.hist(df_list, bins=100, normed=1)
    plt.show()
    print(np.mean(df_list))


if __name__ == "__main__":
    main()