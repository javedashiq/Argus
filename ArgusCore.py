import pandas as pd
import numpy
import re

filePath = '/Users/javedashiq/Documents/Vscode/Argus-python-MVP/OpTransactionHistoryTpr23-05-2025.xls'

df = pd.read_excel(
    filePath,
    skiprows = 12,
    usecols = ['S No.','Transaction Remarks','Withdrawal Amount (INR )','Deposit Amount (INR )','Balance (INR )']
    )

df['Withdrawal Amount (INR )'] = pd.to_numeric(df['Withdrawal Amount (INR )'], errors='coerce').fillna(0).astype(float)
df['Deposit Amount (INR )'] = pd.to_numeric(df['Deposit Amount (INR )'], errors='coerce').fillna(0).astype(float)
df['Balance (INR )'] = pd.to_numeric(df['Balance (INR )'], errors='coerce').astype(float)

categories = ['shopping','snakes','food']
dataMap = {}
withdrawalTransactions = df[df['Deposit Amount (INR )'] == 0]
otherWithdrawTransactions = withdrawalTransactions.copy()
depositTransactions = df[df['Deposit Amount (INR )'] != 0]
##print(withdrawalTransactions)
#print(df.head())

for i in categories:
    pattern = r'.*/.*/' + re.escape(i) + r'.*'
    print(f"Processing category: '{i}' with pattern: '{pattern}'")

    currentCategoryMask = withdrawalTransactions['Transaction Remarks'].str.contains(pattern, case=False, na=False)
    currentFilterDf = withdrawalTransactions[currentCategoryMask].copy()
    dataMap[i] = currentFilterDf

    otherWithdrawTransactions = otherWithdrawTransactions[~currentCategoryMask].copy()

dataMap['others'] = otherWithdrawTransactions

print("Filtering complete. Summary of filtered data:")
for category, filtered_df in dataMap.items():
    totalSpent = filtered_df['Withdrawal Amount (INR )'].sum()
    print(f"On category '{category}' you spent {totalSpent:.2f} Rupees")

netExpenditure = withdrawalTransactions['Withdrawal Amount (INR )'].sum() - depositTransactions['Deposit Amount (INR )'].sum()
print(f"total expenditure is  '{netExpenditure:.2f}' ruppes")

