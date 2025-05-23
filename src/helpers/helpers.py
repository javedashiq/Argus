import pandas as pd


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
        
