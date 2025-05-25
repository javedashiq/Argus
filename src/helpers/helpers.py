import pandas as pd
import re


def cleanUpAndTransformInput(uploadedFile):
    df = pd.read_excel(
            uploadedFile,
            skiprows=12,
            usecols=[
                "Transaction Date",
                "Transaction Remarks",
                "Withdrawal Amount (INR )",
                "Deposit Amount (INR )",
                "Balance (INR )",
            ],
        )
    columnNames = ['Transaction Date','Transaction Remarks','Withdraw Amount','Deposit Amount','Balance']
    df.columns = columnNames
    df["Withdraw Amount"] = (
        pd.to_numeric(df["Withdraw Amount"], errors="coerce")
        .fillna(0)
        .astype(float)
    )
    df["Deposit Amount"] = (
        pd.to_numeric(df["Deposit Amount"], errors="coerce")
        .fillna(0)
        .astype(float)
    )
    df["Transaction Date"] = pd.to_datetime(
        df["Transaction Date"], errors='coerce', dayfirst=True
    )
    df["Balance"] = pd.to_numeric(
        df["Balance"], errors="coerce"
    ).astype(float)

    df.dropna(subset=['Transaction Date'], inplace=True) # Dropping all data with date as null, those will be invalid anyways

    return df

def categorizeData(data_frame, category_list):
    data_map = {}
    withdrawal_transactions = data_frame[data_frame["Deposit Amount"] == 0].copy()
    transactions_remaining_for_others = withdrawal_transactions.reset_index(drop=True).copy()

    for category in category_list:
        if not category:
            continue
        pattern = r'.*/.*/' + re.escape(category) + r'.*'
        current_category_mask = transactions_remaining_for_others["Transaction Remarks"].str.contains(
            pattern, case=False, na=False
        )
        current_filtered_df = transactions_remaining_for_others[current_category_mask].copy()
        data_map[category] = current_filtered_df

        transactions_remaining_for_others = transactions_remaining_for_others[
            ~current_category_mask
        ].reset_index(drop=True).copy()

    data_map["Uncategorized"] = transactions_remaining_for_others.copy()
    return data_map