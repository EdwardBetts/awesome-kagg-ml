import pandas as pd
import numpy as np
from scipy import spatial


class Features:

    def __init__(self, df, features):
        self.df = df
        self.features = features
        self.driver = df.index.get_level_values('Driver')[0]
        self.trip = df.index.get_level_values('Trip')[0]
        self.euclidean_distances = self.euclidean_helper(df)
        self.x_start = df['x'][0]
        self.y_start = df['y'][0]
        self.y_start = df['y'][0]
        self.x_finish = df['x'][-1]
        self.y_finish = df['y'][-1]

    def euclidean_helper(self, df):
        """
        Calculate euclidean distance
        """
        # TODO: Think about that again
        diff1 = np.diff(self.df.x[2:]) ** 2
        diff2 = np.diff(self.df.y[2:]) ** 2
        return np.sqrt(diff1 + diff2)

    def trip_time(self, df):
        """
        Calculate total trip time in seconds
        """
        return len(self.df.index)

    def trip_air_distance(self, df):
        """"
        Calculate air distance from starting point to end point
        """
        start = [[self.x_start, self.y_start]]
        finish = [[self.x_finish, self.y_finish]]

        dist = spatial.distance.cdist(start, finish, 'euclidean')
        return dist[0][0]

    def trip_air_distance_manhattan(self, df):
        """"
        Calculate air distance from starting point to end point
        """

        start = [[self.x_start, self.y_start]]
        finish = [[self.x_finish, self.y_finish]]

        dist = spatial.distance.cdist(start, finish, 'minkowski', 1)
        return dist[0][0]

    def trip_distance(self, df):
        """
        Calculate speed quantiles
        """
        # TODO: Think about that again
        return self.euclidean_distances.sum()

    def average_speed(self, df):
        """
        Calculate speed quantiles
        """
        # TODO: Think about that again
        return self.euclidean_distances.mean()

    def average_acceleration(self, df):
        acc_and_dec = np.diff(self.euclidean_distances)
        acc = acc_and_dec[acc_and_dec > 0].mean()
        return acc

    def average_deceleration(self, df):
        acc_and_dec = np.diff(self.euclidean_distances)
        acc = acc_and_dec[acc_and_dec < 0].mean()
        return acc

    def max_speed(self, df):
        # TODO: Remove outliers
        return self.euclidean_distances.max()

    def extract_all_features(self):

        # Data frame for collecting the features
        series_features = pd.Series()
        series_features['Driver'] = self.driver
        series_features['Trip'] = self.trip

        for feature in self.features:
            feature_method = getattr(self, feature)
            # Calculate value of feature
            series_features[feature] = feature_method(self.df)


        return series_features
