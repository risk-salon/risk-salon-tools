import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

from sklearn.metrics import pairwise_distances
from sklearn.cluster import SpectralClustering
from sklearn.cluster import KMeans
from sklearn.decomposition import PCA

class Groups(object):
    def __init__(self, attendees, topic_prefix='Topic: ', company_col='Company',
                 topics_to_ignore=['Topic: Online risk']):
        self._attendees = attendees

        if topics_to_ignore is not None:
            self.attendees_grouped = self._attendees.copy().drop(topics_to_ignore, axis='columns')
        else:
            self.attendees_grouped = self._attendees.copy()

        self._topic_feature_cols = [x for x in attendees.columns
                                    if topic_prefix in x and
                                    x not in topics_to_ignore]

        self._company_col = company_col
        self._company_feature = None

        self._x = None

        self._fitted_cluster = None

    def make_company_dissimilarity_feature(self, scaling=0.1):
        """The scaling weights the company dissimilarity column. Higher
        values mix up people from the same company into more groups, at the
        cost of clustering stability."""

        company_features = pd.get_dummies(self._attendees[self._company_col])

        # distance between companies
        distance = (pd.DataFrame(pairwise_distances(company_features)).astype(int))

        # use spectral clustering to map attendees to an approximate cluster
        n_c = len(self._attendees[self._company_col].unique())

        sc = SpectralClustering(n_clusters=n_c, affinity='precomputed')
        sc_labels = scaling*pd.Series(sc.fit_predict(distance)).\
            to_frame('company_dissimilarity').reset_index(drop=True)

        self._company_feature = pd.concat(
            [self._attendees[self._company_col].reset_index(drop=True),
             sc_labels], axis='columns')

    def cluster(self, k=5):
        self._x = pd.concat([self._attendees[self._topic_feature_cols].reset_index(drop=True),
                       self._company_feature.company_dissimilarity.reset_index(drop=True)],
                      axis='columns')

        self._fitted_cluster = KMeans(n_clusters=k, random_state=888).fit_predict(self._x) + 1
        self.attendees_grouped['Group'] = self._fitted_cluster

    def check_cluster_sizes(self):
        unique, counts = np.unique(self._fitted_cluster, return_counts=True)
        return np.asarray((unique, counts)).T

    def _split_cluster(self, i_to_split):
        """often the cluster groups will be imbalanced"""
        def increment_if_greater(i1, i2):
            if i2 > i1:
                return i2 + 1
            else:
                return i2
        # make room
        upshifted = np.array([increment_if_greater(i_to_split, i)
                              for i in self._fitted_cluster])

        # split group
        upshifted[pd.Series(np.flatnonzero(upshifted == i_to_split)).
                  sample(frac=0.5, random_state=888).values] = i_to_split+1

        return upshifted

    def randomly_split_clusters(self, clusters_to_split):
        if len(clusters_to_split) > 0:
            increment = 0
            for group in clusters_to_split:
                self._fitted_cluster = self._split_cluster(group + increment)
                increment += 1
            self.attendees_grouped['Group'] = self._fitted_cluster

    def visualize_spatial_distribution(self):
        """intended to be run from within a Jupyter notebook"""
        pca = PCA(n_components=2)
        x_r = pca.fit(self._x).transform(self._x)

        plt.figure(figsize=(15,10))
        plt.scatter(x_r[:,0], x_r[:,1], c=self._fitted_cluster, s=80)
        for label, x, y in zip(self._attendees['First Name'] + ' ' +
                               self._attendees['Last Name'],
                               x_r[:, 0], x_r[:, 1]):
            plt.annotate(
                label,
                xy = (x, y))
        plt.show()

    def visualize_topic_popularity(self):
        def highlight_max(s):
            is_max = s == s.max()
            return ['background-color: yellow' if v else '' for v in is_max]
        return (self.attendees_grouped.groupby('Group').mean() * 100).\
            style.apply(highlight_max, axis=1)
