import numpy as np
import pandas as pd
import os
from sklearn import preprocessing
import logging
logger = logging.getLogger(__name__)


def transform_dataset(df):
    """

    :param df:
    :return: Tuple of the transformed dataset and the labels Y and S
    """

    df_binary = df[(df["race"] == "Caucasian") | (df["race"] == "African-American")]

    del df_binary['c_jail_in']
    del df_binary['c_jail_out']

    ##separated class from the rests of the features
    # remove unnecessary dimensions from Y -> only the decile_score remains
    Y = df_binary['decile_score']
    del df_binary['decile_score']
    Y_true = df_binary['two_year_recid']
    del df_binary['two_year_recid']
    del df_binary['score_text']

    S = df_binary['race']
    #del df_binary['race']
    #del df_binary['is_recid']

    print(df_binary.shape)

    # set sparse to False to return dense matrix after transformation and keep all dimensions homogeneous
    encod = preprocessing.OneHotEncoder(sparse=False)

    data_to_encode = df_binary.to_numpy()
    feat_to_encode = data_to_encode[:, 0]
    # print(feat_to_encode)
    # transposition
    feat_to_encode = feat_to_encode.reshape(-1, 1)
    # print(feat_to_encode)
    encoded_feature = encod.fit_transform(feat_to_encode)

    df_binary_encoded = pd.DataFrame(encoded_feature)

    feat_to_encode = data_to_encode[:, 1]
    feat_to_encode = feat_to_encode.reshape(-1, 1)
    encoded_feature = encod.fit_transform(feat_to_encode)


    df_binary_encoded = pd.concat([df_binary_encoded, pd.DataFrame(encoded_feature)], axis=1)

    feat_to_encode = data_to_encode[:, 2] == "Caucasian"
    feat_to_encode = feat_to_encode.reshape(-1, 1)
    encoded_feature = encod.fit_transform(feat_to_encode)

    df_binary_encoded = pd.concat([df_binary_encoded, pd.DataFrame(encoded_feature)], axis=1)

    # feature [2] [3] [4] [5] [6] [7] [8] has to be put between 0 and 1

    for i in range(3, 10):
        encoded_feature = data_to_encode[:, i]
        ma = np.amax(encoded_feature)
        mi = np.amin(encoded_feature)
        encoded_feature = (encoded_feature - mi) / (ma - mi)
        df_binary_encoded = pd.concat([df_binary_encoded, pd.DataFrame(encoded_feature)], axis=1)

    feat_to_encode = data_to_encode[:, 10]
    feat_to_encode = feat_to_encode.reshape(-1, 1)
    encoded_feature = encod.fit_transform(feat_to_encode)

    df_binary_encoded = pd.concat([df_binary_encoded, pd.DataFrame(encoded_feature)], axis=1)

    feat_to_encode = data_to_encode[:, 11]
    feat_to_encode = feat_to_encode.reshape(-1, 1)
    encoded_feature = encod.fit_transform(feat_to_encode)

    df_binary_encoded = pd.concat([df_binary_encoded, pd.DataFrame(encoded_feature)], axis=1)

    return df_binary_encoded, Y, S, Y_true

def transform_dataset_census(df):
    """

    :param df: the dataset "census income" from a csv file with reduced features, heterogeneous types and missing values, no header
    :return: Tuple of the transformed dataset and the labels Y and S
    """

    label_encoder = preprocessing.LabelEncoder()
    oh_encoder = preprocessing.OneHotEncoder(sparse=False)


    ##Y_true is the vector containing labels, at this point, labels (initially strings) have been transformed into integer (0 and 1) -> -5000 is now '0' and 5000+ is now '+1'

    # Y_true is the true outcome, in this case we're not using a future predictor (vs. compas)
    Y_true=[]

    #remove examples with missing values
    df_replace = df.replace(to_replace="?",value=np.nan)
    df_replace.dropna(inplace=True, axis=0)

    if df_replace.shape == df.shape:
        raise AssertionError("The removal of na values failed")
    
    df_label = df_replace.iloc[:,-1]
    Y = label_encoder.fit_transform(df_label)
    #remove last column from df
    del df_replace[df_replace.columns[-1]]

    #S is the protected attribute
    # could also be feature 7 (sex) or feature 13 (citizenship)
    S=df_replace["sex"]
    del df_replace["sex"]

    #remove feature fnlwgt
    del df_replace["fnlwgt"]
    print(df_replace.shape)
    #transform other features
    #feature age to normalize
    # df_replace.reset_index(inplace=True)
    encoded_feature = df_replace.to_numpy()[:, 0]
    mi = np.amin(encoded_feature)
    ma = np.amax(encoded_feature)
    encoded_feature = (encoded_feature - mi) / (ma - mi)
    #df_binary_encoded is the data frame containing encoded features
    df_binary_encoded = pd.DataFrame(encoded_feature)

    #feature 1 to 7 (after removal) are categorical
    for i in range(1,8):
        encod_feature = df_replace.iloc[:,i]
        encoded_feature = pd.get_dummies(encod_feature)
        df_binary_encoded = pd.concat([df_binary_encoded, pd.DataFrame(encoded_feature).reset_index(inplace=True)], axis=1)
    #feature 8 and 9 are numerical
    for i in range(8,10):
        encod_feature = df_replace.iloc[:,i]
        mi = np.amin(encod_feature)
        ma = np.amax(encod_feature)
        encoded_feature = (encod_feature - mi) / (ma - mi)
        df_binary_encoded = pd.concat([df_binary_encoded, pd.DataFrame(encoded_feature).reset_index(inplace=True)], axis=1)
    #feature 10 and 11 are categorical
    for i in range(10,12):
        encod_feature = df_replace.iloc[:,i]
        encoded_feature = pd.get_dummies(encod_feature)
        df_binary_encoded = pd.concat([df_binary_encoded, pd.DataFrame(encoded_feature).reset_index(inplace=True)], axis=1)

    return df_binary_encoded, Y, S, Y_true


def transform_dataset_credit(df):
    """
    For more info on the features:
    https://archive.ics.uci.edu/ml/datasets/Statlog+%28German+Credit+Data%29

    :param df: the dataset "german credit" from a space separated file
    :return: Tuple of the transformed dataset and the labels Y and S
    """

    label_encoder = preprocessing.LabelEncoder()
    oh_encoder = preprocessing.OneHotEncoder(sparse=False)

    Y = np.array(df.iloc[:,-1] == 2)

    ##Y_true is the vector containing labels, at this point, labels (initially strings) have been transformed into integer (0 and 1) -> -5000 is now '0' and 5000+ is now '+1'
    #remove last column from df
    del df[df.columns[-1]]

    # Y_true is the true outcome, in this case we're not using a future predictor (vs. compas)
    Y_true=[]

    #S is the protected attribute
    S=df.iloc[:,12] > 25
    #del df["Age"]

    #remove examples with missing values
    df_replace = df.replace(to_replace="?",value=np.nan)
    df_replace.dropna(inplace=True, axis=1)

    print(df_replace.shape)

    #transform other features
    #feature age to normalize
    encoded_feature = df_replace.to_numpy()[:, 1]
    mi = np.amin(encoded_feature)
    ma = np.amax(encoded_feature)
    encoded_feature = (encoded_feature - mi) / (ma - mi)

    #df_binary_encoded is the data frame containing encoded features
    df_binary_encoded = pd.DataFrame(encoded_feature)

    # categorical attributes
    for i in [0, 2, 3, 5, 6, 8, 9, 11, 13, 14, 16, 18,19]:
        encod_feature = df_replace.iloc[:,i]
        encoded_feature = pd.get_dummies(encod_feature)
        df_binary_encoded = pd.concat([df_binary_encoded, pd.DataFrame(encoded_feature)], axis=1)

    # Numerical attributes
    for i in [1, 7, 10, 15, 17]:
        encod_feature = df_replace.iloc[:,i]
        mi = np.amin(encod_feature)
        ma = np.amax(encod_feature)
        encoded_feature = (encod_feature - mi) / (ma - mi)
        df_binary_encoded = pd.concat([df_binary_encoded, pd.DataFrame(encoded_feature)], axis=1)

    print(S)

    return df_binary_encoded, Y, S, Y_true


def attack_keras_model(X, Y, S, nb_attack=25, dmax=0.1):
    """
    Generates an adversarial attack on a general model.

    :param X: Original inputs on which the model is trained
    :param Y: Original outputs on which the model is trained
    :param S: Original protected attributes on which the model is trained
    :return: Adversarial dataset (i.e. new data points + original input)
    """

    from secml.data import CDataset
    from secml.array import CArray

    # secML wants all dimensions to be homogeneous (we had previously float and int in X)
    data_set_encoded_secML = CArray(X, dtype=float, copy=True)
    data_set_encoded_secML = CDataset(data_set_encoded_secML, Y)

    n_tr = round(0.66 * X.shape[0])
    n_ts = X.shape[0] - n_tr

    logger.debug(X.shape)
    logger.debug(n_tr)
    logger.debug(n_ts)

    from secml.data.splitter import CTrainTestSplit
    splitter = CTrainTestSplit(train_size=n_tr, test_size=n_ts)

    # Use training set for the classifier and then pick points from an internal test set.
    tr_set_secML, ts_set_secML = splitter.split(data_set_encoded_secML)

    # tr_set_secML = CDataset(X_train,Y_train)
    # ts_set_secML = CDataset(X_test,Y_test)

    # Create a surrogate classifier

    # Creation of the multiclass classifier
    from secml.ml.classifiers import CClassifierSVM
    from secml.ml.classifiers.multiclass import CClassifierMulticlassOVA
    from secml.ml.kernel import CKernelRBF
    clf = CClassifierMulticlassOVA(CClassifierSVM, kernel=CKernelRBF())

    # Parameters for the Cross-Validation procedure
    xval_params = {'C': [1e-4, 1e-3, 1e-2, 0.1, 1], 'kernel.gamma': [0.01, 0.1, 1, 10, 100, 1e3]}

    # Let's create a 3-Fold data splitter
    random_state = 999

    from secml.data.splitter import CDataSplitterKFold
    xval_splitter = CDataSplitterKFold(num_folds=3, random_state=random_state)

    # Select and set the best training parameters for the classifier
    logger.debug("Estimating the best training parameters...")
    best_params = clf.estimate_parameters(
        dataset=tr_set_secML,
        parameters=xval_params,
        splitter=xval_splitter,
        metric='accuracy',
        perf_evaluator='xval'
    )
    logger.debug("The best training parameters are: ", best_params)

    logger.debug(clf.get_params())
    logger.debug(clf.num_classifiers)

    # Metric to use for training and performance evaluation
    from secml.ml.peval.metrics import CMetricAccuracy
    metric = CMetricAccuracy()

    # Train the classifier
    clf.fit(tr_set_secML)
    logger.debug(clf.num_classifiers)

    # Compute predictions on a test set
    y_pred = clf.predict(ts_set_secML.X)

    # Evaluate the accuracy of the classifier
    acc = metric.performance_score(y_true=ts_set_secML.Y, y_pred=y_pred)

    logger.debug("Accuracy on test set: {:.2%}".format(acc))

    # Prepare attack configuration

    noise_type = 'l2'   # Type of perturbation 'l1' or 'l2'
    lb, ub = 0, 1       # Bounds of the attack space. Can be set to `None` for unbounded
    y_target = None     # None if `error-generic` or a class label for `error-specific`

    # Should be chosen depending on the optimization problem
    solver_params = {
        'eta': 0.1,         # grid search resolution
        'eta_min': 0.1,
        'eta_max': None,    # None should be ok
        'max_iter': 1000,
        'eps': 1e-2         # Tolerance on the stopping crit.
    }

    # Run attack

    from secml.adv.attacks.evasion import CAttackEvasionPGDLS
    pgd_ls_attack = CAttackEvasionPGDLS(
        classifier=clf,
        surrogate_classifier=clf,
        surrogate_data=tr_set_secML,
        distance=noise_type,
        dmax=dmax,
        lb=lb, ub=ub,
        solver_params=solver_params,
        y_target=y_target)

    nb_feat = X.shape[1]

    result_pts = np.empty([nb_attack, nb_feat])
    result_class = np.empty([nb_attack, 1])

    # take a point at random being the starting point of the attack and run the attack
    import random
    for nb_iter in range(0, nb_attack):
        rn = random.randint(0, ts_set_secML.num_samples - 1)
        x0, y0 = ts_set_secML[rn, :].X, ts_set_secML[rn, :].Y,

        try:
            y_pred_pgdls, _, adv_ds_pgdls, _ = pgd_ls_attack.run(x0, y0)
            adv_pt = adv_ds_pgdls.X.get_data()
            # np.asarray([np.asarray(row, dtype=float) for row in y_tr], dtype=float)
            result_pts[nb_iter] = adv_pt
            result_class[nb_iter] = y_pred_pgdls.get_data()[0]
        except ValueError:
            logger.warning("value error on {}".format(nb_iter))

    return result_pts, result_class, ts_set_secML[:nb_attack, :].Y


if __name__ == '__main__':
    df = pd.read_csv(os.path.join("..", "data", "csv", "scikit", "compas_recidive_two_years_sanitize_age_category_jail_time_decile_score.csv"))
    df, Y, S = transform_dataset(df)

    result = attack_keras_model(df, Y=Y, S=S)


    # number of attack for which the classifier gives a different response than y0
    #print(np.count_nonzero(result_class != y0))
