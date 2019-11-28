#!/usr/bin/python
import sys
import pickle
import warnings

sys.path.append("../tools/")
sys.path.append("../final_project/")
import numpy as np
import matplotlib.pyplot as plt
from pprint import pprint as pp
from feature_format import featureFormat, targetFeatureSplit
from tester import dump_classifier_and_data, test_classifier

# Sklearn libraries
from sklearn.model_selection import train_test_split
from sklearn.model_selection import cross_val_score
from sklearn.model_selection import GridSearchCV
from sklearn.feature_selection import SelectKBest, f_classif
from sklearn.preprocessing import MinMaxScaler
from sklearn.pipeline import Pipeline
from sklearn.svm import SVC
from sklearn.tree import DecisionTreeClassifier
from sklearn.naive_bayes import GaussianNB
from sklearn.neighbors import KNeighborsClassifier
from sklearn.ensemble import AdaBoostClassifier
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, classification_report

warnings.filterwarnings("ignore", category=DeprecationWarning)
# Task 1: Select what features you will use.
# features_list is a list of strings, each of which is a feature name

# Feature Selection

features_list = [
    "poi",  # POI must be first
    "bonus",
    "deferral_payments",
    "deferred_income",
    "director_fees",
    "exercised_stock_options",
    "expenses",
    "from_messages",
    "from_poi_to_this_person",
    "from_this_person_to_poi",
    "loan_advances",
    "long_term_incentive",
    "other",
    "restricted_stock",
    "restricted_stock_deferred",
    "salary",
    "shared_receipt_with_poi",
    "to_messages",
    "total_payments",
    "total_stock_value",
]


def dump_results(clf_f, features_test, labels_test):
    """
    Prints out a summary of scores
    :param clf_f: ML algorithm
    :param features_test: f_test
    :param labels_test: l_test
    :return: None
    """
    print(f"\nClassifier:\t{clf.__str__()}")
    print(f"Accuracy of Model:\t{clf_f.score(features_test, labels_test)*100:.1f}%")
    print(f"Accuraacy Score:\t{accuracy_score(clf_f.predict(features_test), labels_test)*100:.1f}%")
    print(classification_report(labels_test, pred, target_names=["Not POI", "POI"]))
    print(f"_ _" * 35 + "\n")


# Load the data dictionary from the pickle
with open("final_project_dataset_unix.pkl", "rb") as data_file:
    data_dict = pickle.load(data_file)


print(f"Total number of people in dataset:\t{len(data_dict)}")
print(f"Total number of features available:\t{len(features_list)}")

num_of_poi = 0
for person in data_dict:
    if data_dict[person]["poi"]:
        num_of_poi += 1
print(f"Number of points of interest:\t{num_of_poi}")

# Task 2: Remove outliers
for point, values in data_dict.items():
    x = [int(values["salary"]) if values["salary"] != "NaN" else np.nan]
    y = [int(values["bonus"]) if values["bonus"] != "NaN" else np.nan]
    plt.scatter(x, y)
plt.xlabel("salary")
plt.ylabel("bonus")

num_of_nan = {}
for person, values in data_dict.items():
    for num, feature in enumerate(features_list):
        if values[feature] == "NaN":
            if feature in num_of_nan.keys():
                num_of_nan[feature] += 1
            else:
                num_of_nan[feature] = 1
print(f"NaN Count \t Feature")
for feature, value in num_of_nan.items():
    print(f"{value}  \t \t {feature}")

person = {}
for pers, val in data_dict.items():
    for feat, values in val.items():
        if values == "NaN":
            if pers in person.keys():
                person[pers] += 1
            else:
                person[pers] = 1

for x, y in person.items():
    if y >= 18:
        print(f"Persons with more than 18 or more missing features:\t{x}")

print("Removing the above outliers, along with Total and the CEO")
for x, y in person.items():
    if y >= 18:
        data_dict.pop(x)
data_dict.pop("TOTAL")
data_dict.pop("LAY KENNETH L")


# Task 3: Create new feature(s
def calc_ratio(numer, denom):
    frac = 0
    if numer == "NaN" or denom == "NaN":
        frac = 0
    else:
        frac = float(numer) / float(denom)
        if frac == "NaN":
            frac = 0
    return frac


for person in data_dict:
    salary_to_bonus_ratio = calc_ratio(data_dict[person]["salary"], data_dict[person]["bonus"])
    data_dict[person]["salary_bonus_ratio"] = salary_to_bonus_ratio

    exercised_total_ratio = calc_ratio(
        data_dict[person]["exercised_stock_options"], data_dict[person]["total_stock_value"]
    )
    data_dict[person]["exercised_total_ratio"] = exercised_total_ratio

    tot_pay_tot_stock_ratio = calc_ratio(data_dict[person]["total_payments"], data_dict[person]["total_stock_value"])
    data_dict[person]["tot_pay_stock_ratio"] = tot_pay_tot_stock_ratio

    from_pers_to_poi_ratio = calc_ratio(
        data_dict[person]["from_this_person_to_poi"], data_dict[person]["from_messages"]
    )
    data_dict[person]["from_person_ratio"] = from_pers_to_poi_ratio

    to_pers_poi_ratio = calc_ratio(data_dict[person]["from_poi_to_this_person"], data_dict[person]["to_messages"])
    data_dict[person]["to_person_ratio"] = to_pers_poi_ratio

# create duplicate dataset to allow easier exporting
my_dataset = data_dict
# Selected Features
features_list = [
    "poi",  # POI must be first
    "expenses",
    "other",
    "from_person_ratio",
    "to_person_ratio",
    "tot_pay_stock_ratio",
]


# Extract features and labels from dataset
data = featureFormat(my_dataset, features_list, sort_keys=True)
labels, features = targetFeatureSplit(data)


# Task 4: Try a variety of classifiers

# Apply feature scaling using MinMaxScaler
scaler = MinMaxScaler()
features = scaler.fit_transform(features)

# SelectKBest to determine features to use
selector = SelectKBest(f_classif, k=5)
selector.fit(features, labels)
features = selector.transform(features)
features_scores = zip(features_list[1:], selector.scores_)


sorted_feat_scores = sorted(features_scores, key=lambda feature: feature[1], reverse=True)
for item in sorted_feat_scores:
    print(item[0], item[1])


clf = DecisionTreeClassifier(criterion="entropy", random_state=42)
clf.fit(features, labels)
d_tree_scores = zip(features_list[1:], clf.feature_importances_)
sorted_d_tree_scores = sorted(d_tree_scores, key=lambda feature: feature[1], reverse=True)
for item in sorted_d_tree_scores:
    print(item[0], item[1])


# Task 5: Tune your classifier (hyperparameters) to acheive better
# than a .3 precision and recall
features_train, features_test, labels_train, labels_test = train_test_split(
    features, labels, test_size=0.3, random_state=42
)


""" Code Analysis Completed Below """
# Naive Bayes Gaussian
clf = GaussianNB()
clf.fit(features_train, labels_train)
pred = clf.predict(features_test)
dump_results(clf, features_test, labels_test)

# Support Vector Machine
clf = SVC()
clf.fit(features_train, labels_train)
pred = clf.predict(features_test)
dump_results(clf, features_test, labels_test)

# Decision Tree
clf = DecisionTreeClassifier()
clf.fit(features_train, labels_train)
pred = clf.predict(features_test)
dump_results(clf, features_test, labels_test)

# Adaboost
clf = AdaBoostClassifier(n_estimators=5)
clf.fit(features_train, labels_train)
pred = clf.predict(features_test)
dump_results(clf, features_test, labels_test)

# KNeighbors
clf = KNeighborsClassifier(n_neighbors=10)
clf.fit(features_train, labels_train)
pred = clf.predict(features_test)
dump_results(clf, features_test, labels_test)

# GridSearchCV with parameters
parameters = {
    "splitter": ["random", "best"],
    "criterion": ["entropy", "gini"],
    "max_depth": [2, 3, 5, 10, 15],
    "min_samples_split": [2, 3, 5],
    "min_samples_leaf": [1, 5, 8],
    "max_features": ["sqrt", "log2", "auto"],
}
clf_grid = GridSearchCV(DecisionTreeClassifier(), parameters)
clf_grid.fit(features_train, labels_train)
print(clf_grid.best_estimator_)
# Task 6: Dump your classifier, dataset, and features_list
# so the evaluator can duplicate the analysis
# Chosen Classifier with parameters tuned
clf = DecisionTreeClassifier(
    class_weight=None,
    criterion="entropy",
    max_depth=5,
    max_features="log2",
    max_leaf_nodes=None,
    min_impurity_decrease=0.0,
    min_impurity_split=None,
    min_samples_leaf=8,
    min_samples_split=2,
    min_weight_fraction_leaf=0.0,
    presort=False,
    random_state=42,
    splitter="best",
)

dump_classifier_and_data(clf, my_dataset, features_list)
test_classifier(clf, my_dataset, features_list)
