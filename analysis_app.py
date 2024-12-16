import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# Streamlit App
st.title("Salary Cap vs Total Points Analysis (Multiple Files)")
st.write("""
This app allows you to upload multiple Excel files, select which ones to analyze, and compare the salary cap vs total points for different datasets.
""")

# File Upload
uploaded_files = st.file_uploader(
    "Upload Excel Files (you can select multiple)",
    type=["xlsx"],
    accept_multiple_files=True
)

if uploaded_files:
    # Store dataframes from uploaded files
    file_data = {}

    # Process each uploaded file
    for uploaded_file in uploaded_files:
        st.write(f"Loading data from: {uploaded_file.name}...")
        try:
            jockeys_df = pd.read_excel(uploaded_file, sheet_name="Jockeys")
            trainers_df = pd.read_excel(uploaded_file, sheet_name="Trainers")
            sires_df = pd.read_excel(uploaded_file, sheet_name="Sires")

            # Combine data and add a source column for file name
            combined_data = pd.concat([
                jockeys_df.assign(Role="Jockey"),
                trainers_df.assign(Role="Trainer"),
                sires_df.assign(Role="Sire")
            ])
            combined_data["Source"] = uploaded_file.name  # Add file name as a column

            # Save data to the file_data dictionary
            file_data[uploaded_file.name] = combined_data

        except Exception as e:
            st.error(f"Error processing file {uploaded_file.name}: {e}")

    # Allow user to select files to analyze
    selected_files = st.multiselect(
        "Select files to analyze:",
        options=list(file_data.keys()),
        default=list(file_data.keys())
    )

    # Combine data from selected files
    if selected_files:
        st.write("### Selected Files:")
        st.write(selected_files)

        combined_selected_data = pd.concat([file_data[file] for file in selected_files])

        st.write("### Combined Data from Selected Files:")
        st.dataframe(combined_selected_data)

        # Ensure relevant columns exist and drop missing values
        correlation_data = combined_selected_data[['Final_Salary', 'Total_Points', 'Source']].dropna()

        # Calculate correlation for each file
        st.write("### Correlation Analysis:")
        correlation_by_file = correlation_data.groupby("Source").apply(
            lambda df: df[['Final_Salary', 'Total_Points']].corr().iloc[0, 1]
        )
        st.write(correlation_by_file)

        # Overall correlation across all selected files
        overall_correlation = correlation_data[['Final_Salary', 'Total_Points']].corr().iloc[0, 1]
        st.write(f"Overall Pearson Correlation Coefficient: {overall_correlation:.2f}")

        # Visualization: Scatter plot of Salary vs Points for all selected files
        st.write("### Visualization: Salary vs Total Points (Combined Data)")
        fig, ax = plt.subplots(figsize=(10, 6))
        sns.scatterplot(
            data=correlation_data,
            x="Final_Salary",
            y="Total_Points",
            hue="Source",
            alpha=0.7,
            ax=ax
        )
        ax.set_title("Salary vs Total Points")
        ax.set_xlabel("Final Salary")
        ax.set_ylabel("Total Points")
        st.pyplot(fig)

        # Visualization: Salary Distribution for each file
        st.write("### Visualization: Salary Distribution by File")
        fig, ax = plt.subplots(figsize=(10, 6))
        sns.histplot(
            data=combined_selected_data,
            x="Final_Salary",
            hue="Source",
            kde=True,
            ax=ax,
            multiple="stack"
        )
        ax.set_title("Salary Distribution")
        ax.set_xlabel("Final Salary")
        st.pyplot(fig)

        # Visualization: Points Distribution for each file
        st.write("### Visualization: Points Distribution by File")
        fig, ax = plt.subplots(figsize=(10, 6))
        sns.histplot(
            data=combined_selected_data,
            x="Total_Points",
            hue="Source",
            kde=True,
            ax=ax,
            multiple="stack"
        )
        ax.set_title("Points Distribution")
        ax.set_xlabel("Total Points")
        st.pyplot(fig)
