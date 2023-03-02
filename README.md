# Retail Customer Segmentation
This script performs data analysis on retail data and applies clustering algorithms to segment customers based on their transactional behavior.

## Table of Contents
- General Info
- Technologies
- Dataset
- Content
- Preprocessing
- Clustering Algorithms
- Results
### General Info
This script is developed in Python in Google Colab environment. It reads an online retail dataset, performs exploratory data analysis, and applies clustering algorithms to segment customers based on their transactional behavior.

### Technologies
- Python 3.7
- Jupyter Notebook
### Dataset
The dataset used in this script is the Online Retail dataset from UCI Machine Learning Repository. The dataset contains transactional data of an online retailer located in the UK.

### Content
The script includes the following steps:

- Importing necessary libraries
- Reading the dataset
- Performing exploratory data analysis
- Connecting to a database and cleaning the data
- Performing further preprocessing on cleaned data
- Applying clustering algorithms on preprocessed data
-Evaluating clustering results
### Preprocessing
The following preprocessing steps are performed on the data:

- Removing duplicate rows
- Cleaning the data by removing records with negative values or missing values
### Clustering Algorithms
The following clustering algorithms are used to segment customers:

- KMeans
- Hierarchical clustering
### Results
The evaluation of the clustering results is performed using the silhouette score, which measures the similarity of each data point to its own cluster compared to other clusters. The results show that hierarchical clustering produces better segmentation results than KMeans clustering.
