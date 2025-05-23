import pandas as pd
import numpy as np
import re
import streamlit as st
import altair as alt

st.set_page_config(layout="wide")

st.title("Argus : Transaction History Analyzer")

st.write(
    """
    Upload your transaction history Excel file to get insights into your spending!
    """
)

uploaded_file = st.file_uploader(
    "Choose an Excel file", type=["xls", "xlsx"])

if uploaded_file is not None:
    try:
        df = pd.read_excel(
            uploaded_file,
            skiprows=12,
            usecols=[
                "S No.",
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
        df["Balance (INR )"] = pd.to_numeric(
            df["Balance (INR )"], errors="coerce"
        ).astype(float)

        st.success("File uploaded and processed successfully!")

        st.subheader("Transaction Data Preview")
        st.dataframe(df.head())

        st.sidebar.header("Configure Categories")
        
        default_categories = "shopping,snacks,food"
        category_input = st.sidebar.text_area(
            "Enter categories separated by commas:", 
            value=default_categories,
            height=100
        )
        categories = [cat.strip() for cat in category_input.split(',') if cat.strip()]

        if not categories:
            st.warning("Please enter at least one category in the sidebar to proceed with analysis.")
        else:
            st.sidebar.write("Analyzing for categories: ", ", ".join(categories))

            dataMap = {}
            withdrawalTransactions = df[df["Deposit Amount (INR )"] == 0].copy()
            otherWithdrawTransactions = withdrawalTransactions.copy()
            depositTransactions = df[df["Deposit Amount (INR )"] != 0].copy()

            for i in categories:

                pattern = r'.*/.*/' + re.escape(i) + r'.*'
            
                currentCategoryMask = withdrawalTransactions["Transaction Remarks"].str.contains(
                    pattern, case=False, na=False
                )
                currentFilterDf = withdrawalTransactions[currentCategoryMask].copy()
                dataMap[i] = currentFilterDf

                otherWithdrawTransactions = otherWithdrawTransactions[
                    ~currentCategoryMask
                ].copy()

            dataMap["Uncategorized"] = otherWithdrawTransactions

            st.header("Spending Summary by Category")
            
            summary_data = []
            for category, filtered_df in dataMap.items():
                totalSpent = filtered_df["Withdrawal Amount (INR )"].sum()
                summary_data.append({"Category": category.capitalize(), "Total Spent (INR)": f"{totalSpent:.2f}"})
            
            st.table(pd.DataFrame(summary_data))


            summary_df = pd.DataFrame(summary_data)
            
            if not summary_df.empty:
                chart = alt.Chart(summary_df).mark_bar().encode(
                    x=alt.X('Category:N', sort='-y'),
                    y=alt.Y('Total Spent (INR):Q', title='Amount (INR)'),
                    tooltip=['Category', alt.Tooltip('Total Spent (INR)', format=',.2f', title='Amount')]
                ).interactive()

                st.altair_chart(chart, use_container_width=True)
            else:
                st.warning("No spending data available to generate a chart.")
            

            netExpenditure = (
                withdrawalTransactions["Withdrawal Amount (INR )"].sum()
                - depositTransactions["Deposit Amount (INR )"].sum()
            )
            st.markdown(
                f"---"
            )
            st.subheader(f"Total Net Expenditure: :red[{netExpenditure:.2f}] Rupees")
            st.markdown(
                f"*(This is calculated as total withdrawals minus total deposits)*"
            )

            st.subheader("Detailed Transactions by Category")
            selected_category_detail = st.selectbox(
                "Select a category to view detailed transactions:", 
                list(dataMap.keys())
            )
            if selected_category_detail:
                st.dataframe(dataMap[selected_category_detail])


    except Exception as e:
        st.error(f"An error occurred: {e}")
        st.info(
            """
            Please ensure your Excel file is in the correct format with the expected columns:
            'S No.', 'Transaction Remarks', 'Withdrawal Amount (INR )', 'Deposit Amount (INR )', 'Balance (INR )'.
            Also, check if the 'skiprows' parameter (currently set to 12) needs to be adjusted
            based on your file's header structure.
            """
        )