# -*- coding: utf-8 -*-
"""DWABI CW2 Mohammadamin Shams.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1GrX1w8_-EBrOGQnKyHm-tbbNK1Ido7x2

Code is done with google colab environment and i uploaded the file there and then only mentioned the name in the pandas read csv function

First we need to import our libraries and install the libraries that its not installed
"""

!pip install squarify	
! pip install pandas_profiling

# Commented out IPython magic to ensure Python compatibility.
#from pandas_profiling import ProfileReport
import pandas as pd
import sqlite3
from sklearn.metrics import silhouette_score
from yellowbrick.cluster import KElbowVisualizer, SilhouetteVisualizer
import datetime
import matplotlib.pyplot as plt	
import scipy.cluster.hierarchy as shc
from sklearn.cluster import AgglomerativeClustering
import squarify
import scipy.cluster.hierarchy as sch
from sklearn.cluster import AgglomerativeClustering
from sklearn.cluster import KMeans
import numpy as np

import seaborn as sns
from sklearn.preprocessing import StandardScaler
from mpl_toolkits.mplot3d import Axes3D
# %matplotlib inline

"""Import the dataset"""

retail_data=pd.read_excel('Online Retail.xlsx')

"""Get a profile report
This part is done with pycharm
"""

#report = ProfileReport(retail_data, title='Pandas Profiling Report2', explorative=True)
#report.to_file(output_file="CW2_Data_statistics.html")

"""Basic data properties"""

retail_data.head()

retail_data.shape

retail_data.info()

retail_data.describe()

retail_data.isna().sum()

retail_data[retail_data.duplicated()]

retail_data.duplicated().sum()

"""Checking the number of unique transactions"""

retail_data.InvoiceNo.nunique()

"""Checking the unique stock ids in the data or number of unqiue item sold by retailer"""

retail_data.StockCode.nunique()

"""Looking at the distribution of the quantity
. There is negative value which might indicate return orders
"""

retail_data.Quantity.describe()

"""Unique customer"""

retail_data.CustomerID.nunique()

retail_data.Description.nunique()

"""Top 10 item sold"""

retail_data.Description.value_counts().head(10)

"""Top 10 item sold with their quantity"""

retail_data.groupby('Description').agg({"Quantity":"sum"}).sort_values("Quantity",ascending=False).head(10)

"""Distribution of data among the countries shows us what was obviuos and the retailer obviusly is located in UK"""

retail_data.Country.value_counts(normalize=True)

"""Distribution of unit price"""

retail_data.UnitPrice.describe(percentiles=[0.25,0.5,0.75,0.9,0.95,0.99])

"""The time period of all purchases are between this time interval"""

print('The minimum date is:',retail_data.InvoiceDate.min())
print('The maximum date is:',retail_data.InvoiceDate.max())

"""Removing the duplicate rows"""

print(retail_data.shape)
retail_data.drop_duplicates(inplace=True)
print(retail_data.shape)

"""Connect to database"""

conn = sqlite3.connect("RFMdb")
cur = conn.cursor() 

# load data into the RFMdb database
retail_data.to_sql("Online_Retail", conn)

# Check if the data is inserted in data/RFMdb
retail_data_sql = pd.read_sql('SELECT * FROM Online_Retail', conn)
retail_data_sql

"""Clean data """

retail_data_sql_cleaned= pd.read_sql(''' SELECT *
      FROM Online_Retail
      WHERE InvoiceNo NOT LIKE '%C%'
      AND CustomerID IS NOT NULL
      AND Description IS NOT NULL
      AND Description NOT LIKE '%?%'
      AND UnitPrice >= 0
      AND Quantity >= 0''', conn)

# Write clean CRM data into the database
retail_data_sql_cleaned.to_sql("retail_data_sql_cleaned", conn)
retail_data_sql_cleaned

"""Making sure there is no duplicated rows and remove if there is duplicate rows."""

print(retail_data_sql_cleaned.shape)
retail_data_sql_cleaned.drop_duplicates(inplace=True)
print(retail_data_sql_cleaned.shape)

"""Do the preproccessing stages again for data that is been cleaned for the rfm segmentation proccessing"""

retail_data_sql_cleaned.info()

retail_data_sql_cleaned.isnull().sum()

"""Distribution of InvoiceNo"""

plt.figure(figsize=(10, 6))
sns.set(style = 'whitegrid')
sns.distplot(retail_data_sql_cleaned['InvoiceNo'])
plt.title('Distribution of InvoiceNo', fontsize = 20)
plt.xlabel('Range of InvoiceNo')
plt.ylabel('Count')

"""Distribution of CustomerID"""

plt.figure(figsize=(10, 6))
sns.set(style = 'whitegrid')
sns.distplot(retail_data_sql_cleaned['CustomerID'])
plt.title('Distribution of CustomerID', fontsize = 20)
plt.xlabel('Range of CustomerID')
plt.ylabel('Count')

"""Correlation analysis"""

retail_data_sql_cleaned.iloc[:,1:].corr()

plt.figure(figsize=(12, 9))
s=sns.heatmap(retail_data_sql_cleaned.iloc[:,1:].corr(),
              annot=True,
              cmap='RdBu',
              vmin=-1,
              vmax=1)
s.set_yticklabels(s.get_yticklabels(),rotation=0,fontsize=12)
s.set_xticklabels(s.get_xticklabels(),rotation=90,fontsize=12)
plt.title('Correlation Heatmap')
plt.show()

"""RFM can be find in two different ways

First is to only use sqlite to create it another way is using the clean data for creating both of them are used first with sql
"""

RFM_with_sql= pd.read_sql(''' SELECT CustomerID,
          MAX(InvoiceDate) AS last_order_date,
          COUNT(*) AS count_order,
          SUM(UnitPrice*Quantity) AS Totalprice
      FROM Online_Retail
      WHERE InvoiceNo NOT LIKE '%C%'
      AND CustomerID IS NOT NULL
      AND Description IS NOT NULL
      AND Description NOT LIKE '%?%'
      AND UnitPrice >= 0
      AND Quantity >= 0
      GROUP BY CustomerID ''', conn)
# Write clean CRM data into the database
RFM_with_sql.to_sql("RFM_with_sql", conn)
RFM_with_sql

RFM_with_sql['last_order_date']=pd.to_datetime(RFM_with_sql['last_order_date']).dt.date
RFM_with_sql['last_order_date']=(RFM_with_sql.last_order_date.max()-RFM_with_sql['last_order_date']).dt.days+1
#converting the names of the columns
RFM_with_sql.rename(columns = {'last_order_date' : "Recency",'count_order' : "Frequency",
                          'Totalprice' : "Monetary"},inplace = True)
RFM_with_sql

"""Now we create it using group.by on cleaned data after sql command just for cleaning"""

retail_data_sql_cleaned['TotalAmount']=retail_data_sql_cleaned['UnitPrice']*retail_data_sql_cleaned['Quantity']
retail_data_sql_cleaned['InvoiceDate']=pd.to_datetime(retail_data_sql_cleaned['InvoiceDate']).dt.date
Latest_date=retail_data_sql_cleaned['InvoiceDate'].max()
RFM_with_python = retail_data_sql_cleaned.groupby('CustomerID').agg({'InvoiceDate' : lambda x :(Latest_date - x.max()).days+1,
                                          'InvoiceNo' : 'count','TotalAmount' : 'sum'}).reset_index()
RFM_with_python.rename(columns = {'InvoiceDate' : 'Recency',
                          'InvoiceNo' : "Frequency",
                          'TotalAmount' : "Monetary"},inplace = True)  
RFM_with_python

RFM_with_sql.info()

RFM_with_sql.describe()

"""Distribution of Frequency"""

plt.figure(figsize=(10, 6))
sns.set(style = 'whitegrid')
sns.distplot(RFM_with_sql['Frequency'])
plt.title('Distribution of Frequency', fontsize = 20)
plt.xlabel('Range of Frequency')
plt.ylabel('Count')

"""Distribution of Recency"""

plt.figure(figsize=(10, 6))
sns.set(style = 'whitegrid')
sns.distplot(RFM_with_sql['Recency'])
plt.title('Distribution of Recency', fontsize = 20)
plt.xlabel('Range of Recency')
plt.ylabel('Count')

"""Distribution of Monetary

"""

plt.figure(figsize=(10, 6))
sns.set(style = 'whitegrid')
sns.distplot(RFM_with_sql['Monetary'])
plt.title('Distribution of Monetary', fontsize = 20)
plt.xlabel('Range of Monetary')
plt.ylabel('Count')

"""Correlation analysis on data ready for segmentation with kmeans"""

RFM_with_sql.corr()

plt.figure(figsize=(12, 9))
s=sns.heatmap(RFM_with_sql.corr(),
              annot=True,
              cmap='RdBu',
              vmin=-1,
              vmax=1)
s.set_yticklabels(s.get_yticklabels(),rotation=0,fontsize=12)
s.set_xticklabels(s.get_xticklabels(),rotation=90,fontsize=12)
plt.title('Correlation Heatmap')
plt.show()

"""Plot recency, monetary and frequency based on each other"""

plt.figure(figsize=(15,5))
plt.subplot(1,3,1)
plt.scatter(RFM_with_sql.Recency, RFM_with_sql.Frequency, color='grey', alpha=0.3)
plt.title('Recency vs Frequency', size=15)
plt.subplot(1,3,2)
plt.scatter(RFM_with_sql.Monetary, RFM_with_sql.Frequency, color='grey', alpha=0.3)
plt.title('Monetary vs Frequency', size=15)
plt.subplot(1,3,3)
plt.scatter(RFM_with_sql.Recency, RFM_with_sql.Monetary, color='grey', alpha=0.3)
plt.title('Recency vs Monetary', size=15)
plt.show()

"""Seeing the outliers with boxplot"""

column = ['Recency','Frequency','Monetary']
plt.figure(figsize=(15,5))
for i,j in enumerate(column):
    plt.subplot(1,3,i+1)
    sns.boxplot(RFM_with_sql[j], color='skyblue')
    plt.xlabel('')
    plt.title('{}'.format(j.upper()), size=13)
plt.show()

"""Kmeans algorithm is sensitive to the scale and also outliers can mess up the distiribution, it is possible to remove them

Create a function for detecting outliers and use the 10 and 90 percentile to get rid of the outliers
"""

def outliers(dataframe, feature):
    q1 = dataframe[feature].quantile(0.10)
    q3 = dataframe[feature].quantile(0.90)
    iqr = q3 - q1
    lower_bound = q1 - 1.5 * iqr
    upper_bound = q3 + 1.5 * iqr

    ls = dataframe.index[ (dataframe[feature] < lower_bound) | (dataframe[feature] > upper_bound) ]
    return ls

''' Create a list to see the indexes of outliers for dataset and also only detect outliers 
for the columns that are going to be used in analysis'''

outliers_index = []
for column in ['Recency','Frequency','Monetary']:
  outliers_index.extend(outliers(RFM_with_sql, column))
outliers_index,len(outliers_index)

# Create a function for deleting outliers based on their indexes

def remove(df,ls):
    ls = sorted(set(ls))
    df = df.drop(ls)
    return df
RFM_with_sql_cleaned = remove(RFM_with_sql,outliers_index)
RFM_with_sql_cleaned.reset_index(drop=True, inplace=True)

# See howe many outliers were detected and deleted

print(len(RFM_with_sql_cleaned))
print(len(RFM_with_sql))

column = ['Recency','Frequency','Monetary']
plt.figure(figsize=(15,5))
for i,j in enumerate(column):
    plt.subplot(1,3,i+1)
    sns.boxplot(RFM_with_sql_cleaned[j], color='skyblue')
    plt.xlabel('')
    plt.title('{}'.format(j.upper()), size=13)
plt.show()

RFM_with_sql_kmeans = RFM_with_sql_cleaned.iloc[:,1:]
# scaling the variables and store it in different df for kmeans
scaler = StandardScaler()
RFM_with_sql_kmeans_norm = scaler.fit_transform(RFM_with_sql_kmeans)

# converting it into dataframe
RFM_with_sql_kmeans_norm = pd.DataFrame(RFM_with_sql_kmeans_norm)
RFM_with_sql_kmeans_norm.columns = ['Recency','Frequency','Monetary']
RFM_with_sql_kmeans_norm.head()

"""Finding the number of clusters with elbow method and silhoutte score"""

wcss=[]
for i in range(1,11):
    kmeans=KMeans(n_clusters=i, init='k-means++',n_init=10,max_iter=300)
    kmeans.fit(RFM_with_sql_kmeans_norm)
    wcss.append(kmeans.inertia_)
#The elbow curve
plt.figure(figsize=(12,6))
plt.plot(range(1,11),wcss)
plt.plot(range(1,11),wcss, linewidth=2, color="red", marker ="8")
plt.xlabel("K Value")
plt.xticks(np.arange(1,11,1))
plt.ylabel("WCSS")
plt.show()

# Elbow method with Yellowbrick Visualiser
visualizer = KElbowVisualizer(kmeans, k=(2, 11))
visualizer.fit(RFM_with_sql_kmeans_norm)
visualizer.show()


# Silhouette score for finding number of clusters
for i in range(2,11):
    # intialise kmeans
    kmeans.fit(RFM_with_sql_kmeans_norm)
    
    cluster_labels = kmeans.labels_
    
    # silhouette score
    silhouette_avg = silhouette_score(RFM_with_sql_kmeans_norm, cluster_labels)
    print("For n_clusters={0}, the silhouette score is {1}".format(i, silhouette_avg))

#Taking 4 clusters
km1=KMeans(n_clusters=4, init='k-means++',n_init=10,max_iter=300)
#Fitting the input data
km1.fit(RFM_with_sql_kmeans_norm)
#predicting the labels of the input data
y=km1.predict(RFM_with_sql_kmeans_norm)
#adding the labels to a column named label
RFM_with_sql_kmeans["label"] = y
#The new dataframe with the clustering done
RFM_with_sql_kmeans

"""See the distribution of members between 4 clusters"""

RFM_with_sql_kmeans['label'].value_counts()

"""See the mean of rfm values for each cluster"""

RFM_with_sql_kmeans.groupby('label').mean()

column = ['Recency','Frequency','Monetary']
plt.figure(figsize=(15,4))
for i,j in enumerate(column):
    plt.subplot(1,3,i+1)
    sns.boxplot(y=RFM_with_sql_kmeans[j], x=RFM_with_sql_kmeans['label'], palette='spring')
    plt.title('{} wrt clusters'.format(j.upper()), size=13)
    plt.ylabel('')
    plt.xlabel('')

plt.show()

#3D Plot as we did the clustering on the basis of 3 input features
fig = plt.figure(figsize=(20,10))
ax = fig.add_subplot(111, projection='3d')
ax.scatter(RFM_with_sql_kmeans.Recency[RFM_with_sql_kmeans.label == 0], RFM_with_sql_kmeans["Frequency"][RFM_with_sql_kmeans.label == 0], RFM_with_sql_kmeans["Monetary"][RFM_with_sql_kmeans.label == 0], c='purple', s=60)
ax.scatter(RFM_with_sql_kmeans.Recency[RFM_with_sql_kmeans.label == 1], RFM_with_sql_kmeans["Frequency"][RFM_with_sql_kmeans.label == 1], RFM_with_sql_kmeans["Monetary"][RFM_with_sql_kmeans.label == 1], c='red', s=60)
ax.scatter(RFM_with_sql_kmeans.Recency[RFM_with_sql_kmeans.label == 2], RFM_with_sql_kmeans["Frequency"][RFM_with_sql_kmeans.label == 2], RFM_with_sql_kmeans["Monetary"][RFM_with_sql_kmeans.label == 2], c='blue', s=60)
ax.scatter(RFM_with_sql_kmeans.Recency[RFM_with_sql_kmeans.label == 3], RFM_with_sql_kmeans["Frequency"][RFM_with_sql_kmeans.label == 3], RFM_with_sql_kmeans["Monetary"][RFM_with_sql_kmeans.label == 3], c='green', s=60)

ax.view_init(35, 185)
plt.xlabel("Recency")
plt.ylabel("Frequency")
ax.set_zlabel('Monetary')
plt.show()

# Creating figure
fig = plt.figure(figsize = (8, 5))
ax = plt.axes(projection ="3d")

# Creating plot
ax.scatter3D(RFM_with_sql_kmeans.Recency, RFM_with_sql_kmeans.Frequency, RFM_with_sql_kmeans.Monetary, c=RFM_with_sql_kmeans.label, cmap='brg')
ax.set_xlabel('Recency')
ax.set_ylabel('Frequency')
ax.set_zlabel('Monetary')
plt.title('RFM in 3D with Clusters', size=15)
ax.set(facecolor='white')
plt.show()

plt.figure(figsize=(15,5))
plt.subplot(1,3,1)
plt.scatter(RFM_with_sql_cleaned.Recency, RFM_with_sql_cleaned.Frequency, c=y, cmap='rainbow')
plt.title('Recency vs Frequency', size=15)
plt.subplot(1,3,2)
plt.scatter(RFM_with_sql_cleaned.Monetary, RFM_with_sql_cleaned.Frequency, c=y, cmap='rainbow')
plt.title('Monetary vs Frequency', size=15)
plt.subplot(1,3,3)
plt.scatter(RFM_with_sql_cleaned.Recency, RFM_with_sql_cleaned.Monetary, c=y, cmap='rainbow')
plt.title('Recency vs Monetary', size=15)
plt.show()