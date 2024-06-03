import pandas as pd

SPECTRUM_START_COLUMN = 16


def load(
    labels: list[str],
    include_ec=True,
    include_depth=True,
    train_split=0.75,
    normalize_Y=False,
) -> tuple[tuple[pd.DataFrame, pd.DataFrame], tuple[pd.DataFrame, pd.DataFrame]]:
    """Load the averaged NIR samples from the Neospectra dataset

    Args:
        labels (list[str]): The labels that we wish to include in Y_train and Y_test
        include_ec (bool, optional): Include soil electroconductivity as a feature. Defaults to True.
        train_split (float, optional): Split between training and test set. Defaults to 0.75.
        normalize_Y (bool, optional): Whether to normalize the labels. Defaults to False.

    Returns:
        tuple[tuple[pd.DataFrame, pd.DataFrame], tuple[pd.DataFrame, pd.DataFrame]]: _description_
    """
    dataset = pd.read_csv("mississippi_db/jRead_spec_lab.csv").set_index("file_name")


    # Drop NaNs for labels
    dataset = dataset.dropna(axis="index", subset=labels)

    # if include_ec:
    #     dataset = dataset.dropna(axis="index", subset=["ec_12pre"])

    # Split into train and test
    train_dataset = dataset.sample(frac=train_split, random_state=0)
    test_dataset = dataset.drop(train_dataset.index)

    spectra_column_names = []

    for col_name in list(dataset):
        try:
            float(col_name)
        except ValueError:
            continue
        spectra_column_names.append(col_name)

    # NOTE: We assume that a column contains spectral data IFF the column name is a float,
    # and that this column name is a wavelength in nm.
    X_train = train_dataset.loc[:, spectra_column_names]
    X_test = test_dataset.loc[:, spectra_column_names]

    if include_depth:
        # Clean up depth column
        depths = dataset["Sample_Depth"]

        start_depth = dataset["Sample_Depth"].map(lambda x: x.split('-')[0]).astype(float).rename("lay.depth.to.top")
        end_depth = dataset["Sample_Depth"].map(lambda x: x.split('-')[1]).astype(float).rename("lay.depth.to.bottom")

        dataset = dataset.join(start_depth)
        dataset = dataset.join(end_depth)

        X_train = X_train.join(start_depth)
        X_test = X_test.join(end_depth)

    Y_train = train_dataset.loc[:, labels]
    Y_test = test_dataset.loc[:, labels]

    # Save for unnormalization later
    original_test_label_std = Y_test.std()
    original_test_label_mean = Y_test.mean()

    # Normalize
    if normalize_Y:
        Y_train = (Y_train - Y_train.mean()) / Y_train.std()
        Y_test = (Y_test - Y_test.mean()) / Y_test.std()

    print(X_train.dtypes)
    
    return (X_train, Y_train), (X_test, Y_test)