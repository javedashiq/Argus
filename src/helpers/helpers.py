import pandas as pd
def cleanUpAndTransformInput(uploadedFile):
    df = pd.read_excel(
            uploadedFile,
            skiprows=12,
            usecols=[
                "S No.",
                "Transaction Date",
                "Transaction Remarks",
                "Withdrawal Amount (INR )",
                "Deposit Amount (INR )",
                "Balance (INR )",
            ],
        )

    df["Withdrawal Amount (INR )"] = (
        pd.to_numeric(df["Withdrawal Amount (INR )"], errors="coerce")
        .fillna(0)
        .astype(float)
    )
    df["Deposit Amount (INR )"] = (
        pd.to_numeric(df["Deposit Amount (INR )"], errors="coerce")
        .fillna(0)
        .astype(float)
    )
    df["Transaction Date"] = pd.to_datetime(
        df["Transaction Date"], errors='coerce', dayfirst=True
    )
    df["Balance (INR )"] = pd.to_numeric(
        df["Balance (INR )"], errors="coerce"
    ).astype(float)

    df.dropna(subset=['Transaction Date'], inplace=True) # Dropping all data with date as null, those will be invalid anyways

    return df
        
