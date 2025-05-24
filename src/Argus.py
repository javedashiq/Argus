import pandas as pd
import re
import streamlit as st
import altair as alt

from helpers.helpers import cleanUpAndTransformInput, categorizeData

st.set_page_config(layout="wide")
st.title("Argus : Transaction History Analyzer")
st.write(
    """
    Upload your Bank Statement in an Excel file to get insights into your spending!
    """
)

dataFrame = None
categories = []

st.subheader("Configure Categories")
if 'num_input' not in st.session_state:
    st.session_state.num_input = 1

for i in range(st.session_state.num_input):
    input_value = st.text_input(f"Input {i + 1}:", key=f"dynamic_input_{i}")
    categories.append(input_value)
col1, col2 = st.columns(2)
with col1:
    if st.button("Add Another Category", disabled=(st.session_state.num_input == 10),use_container_width = True):
        st.session_state.num_input += 1
        st.rerun()
with col2:
    if st.button("Remove Last Input", disabled=(st.session_state.num_input <= 1),use_container_width = True):
        st.session_state.num_input -= 1
        st.rerun()
categories = [cat.strip() for cat in categories if cat.strip()]

uploadedFile = st.file_uploader(
    "Choose an Excel file", type=["xls", "xlsx"])
if uploadedFile is not None:
    try:
        dataFrame = cleanUpAndTransformInput(uploadedFile)
    except Exception as e:
        st.error(f"An error occurred uploading the file: {e}")
        st.info(
            """
            Please ensure your Excel file is in the correct format with the expected columns:
            'S No.', 'Transaction Remarks', 'Withdrawal Amount (INR )', 'Deposit Amount (INR )', 'Balance (INR )'.
            Also, check if the 'skiprows' parameter (currently set to 12) needs to be adjusted
            based on your file's header structure.
            """
        )


    
if dataFrame is not None and not dataFrame.empty:
    st.success("File uploaded and processed successfully!")
    
    startDate = dataFrame['Transaction Date'].min().date()
    endDate = dataFrame['Transaction Date'].max().date()
    START_END_DATE_TEXT =  f" On {startDate}" if startDate == endDate else +f" From {startDate} To {endDate}"


    st.subheader("Transaction Data Preview" + START_END_DATE_TEXT)
    st.dataframe(dataFrame.head())

    if not categories:
        st.warning("Please enter at least one category to proceed with analysis.")
    else:
        st.write("Analyzing for categories: ", ", ".join(categories))

        dataMap = categorizeData(dataFrame, categories)

### Add Ability to Categoeize Uncategorized data here

        st.header("Spending Summary by Category" + START_END_DATE_TEXT)
        
        summary_data = []
        for category, filtered_df in dataMap.items():
            totalSpent = filtered_df["Withdraw Amount"].sum()
            summary_data.append({"Category": category.capitalize(), "Total Spent (INR)": f"{totalSpent:.2f}"})
        
        st.table(pd.DataFrame(summary_data))


        summary_df = pd.DataFrame(summary_data)
        
        if not summary_df.empty:
            chart = alt.Chart(summary_df).mark_bar().encode(
                x=alt.X('Category:N', sort='-y'),
                y=alt.Y('Total Spent (INR):Q', title='Amount (INR)')
            ).interactive()

            st.altair_chart(chart, use_container_width=True)
        else:
            st.warning("No spending data available to generate a chart.")
        
        totalAmountWithdrawn = dataFrame["Withdraw Amount"].sum()
        totalAmountDeposited = dataFrame["Deposit Amount"].sum()
        netExpenditure = totalAmountWithdrawn - totalAmountDeposited

        with st.sidebar:
            st.markdown(f"### **Summary For Transactions** {START_END_DATE_TEXT}")
            st.markdown("---") 
            st.metric(
                label="Total Amount Withdrawn",
                value=f"{totalAmountWithdrawn:.2f} Rupees",
                help="This is the total sum of all withdrawal transactions."
            )

            st.metric(
                label="Total Amount Deposited",
                value=f"{totalAmountDeposited:.2f} Rupees",
                help="This is the total sum of all deposit transactions."
            )

            st.metric(
                label="Total Net Expenditure",
                value=f"{netExpenditure:.2f} Rupees",
                help="Calculated as Total Withdrawals - Total Deposits.",
                border=True
            )

            st.markdown("---")
            st.markdown(
                """
                *Transactions within the selected date range are included.*
                *The Net Expenditure indicates your overall spending*
                """
            )


        st.subheader("Detailed Transactions by Category" + START_END_DATE_TEXT)
        selected_category_detail = st.selectbox( 
            "Select a category to view detailed transactions:", 
            list(dataMap.keys())
        )
        if selected_category_detail:
            st.dataframe(dataMap[selected_category_detail])


        