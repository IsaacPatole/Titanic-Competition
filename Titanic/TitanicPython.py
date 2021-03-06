#importing the libraries
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

# let's read the daatset
train   = pd.read_csv(r"C:\Users\MY\Desktop\Titanic\train.csv")
test    = pd.read_csv(r"C:\Users\MY\Desktop\Titanic\test.csv")
df_data = [train,test]

#let's add parch and sibsp column to see what impacet does it have on survival.
for df in df_data:
    df['Family']= df['Parch']+df['SibSp']
    df['Family'].loc[df['Family'] == 0] = 0
    df['Family'].loc[df['Family'] == 1] = 1
    df['Family'].loc[df['Family'] == 2] = 2
    df['Family'].loc[(df['Family'] > 2)&(df['Family'] <= 4)] = 3
    df['Family'].loc[df['Family'] > 4] = 4
    
    
print("What Family column can tell us?")
print(train[['Family', 'Survived']].groupby(['Family'], as_index=False).mean())

#fill Nan Values by using 'ffill'.  which fill's NaN values by its previouse value
for df in df_data:
    df['Embarked'] = df[['Embarked']].fillna(method='ffill')
    df['Fare'] = df[['Fare']].fillna(method='ffill')
    
#extracting titles from name column
dataset_title = [i.split(",")[1].split(".")[0].strip() for i in test["Name"]]
for df in df_data:
    df["Title"] = pd.Series(dataset_title)
    df["Title"] = df["Title"].replace(['Lady', 'the Countess','Countess','Capt', 'Col','Don', 'Dr', 'Major', 'Rev', 'Sir', 'Jonkheer', 'Dona'], 'Rare')
    df.Title = df.Title.replace('Mlle', 'Miss')
    df.Title = df.Title.replace('Ms', 'Miss')
    df.Title = df.Title.replace('Mme', 'Mrs')
 # Fill in missing data with a placeholder.
    df.Title = df.Title.fillna('Missing')

print("What titles survived?")
print(train[['Title', 'Survived']].groupby(['Title'], as_index=False).mean())

for df in df_data:
#lets see the average age corresponding to each title
    df.groupby('Title').Age.mean()
#using the same thing again to see the count+mean
    df.groupby('Title').Age.agg(['count','median'])
#lets fill missing na values in a Age column corresponding to average of each based on each title
#inputing the values on Age Na's
    df.loc[df.Age.isnull(), 'Age'] = df.groupby(['Title']).Age.transform('median')
 #converting the ages values into different bins 
from sklearn.preprocessing import LabelEncoder  
for df in df_data: 
    df['AgeBin'] = pd.qcut(df['Age'], 4)
    label = LabelEncoder()
    df['AgeBin_Code'] = label.fit_transform(df['AgeBin'])

#converting fare's into different bins
    df['FareBin'] = pd.qcut(df['Fare'], 5)
    label = LabelEncoder()
    df['FareBin_Code'] = label.fit_transform(df['FareBin'])
    

title_mapping = {"Mr": 1, "Miss": 2, "Mrs": 3, "Master": 4, "Rare": 5, "Missing": 0}
for df in df_data:
    df['Title'] = df['Title'].map(title_mapping)
    df["Title"] = df["Title"].astype(int)
#dropping the columns(you can try using other columns as well)
    df.drop(['PassengerId','Name','SibSp','Parch','Ticket','Cabin','Age','Fare'
             ,'AgeBin','FareBin'] , axis =1 , inplace=True)

#converting into numeric values
    df['Sex']= df[['Sex']].replace(['male','female'],[0,1])
    df['Embarked']= df['Embarked'].replace(['C','Q','S'],[0,1,2])
    
print("What genderer of passenger survived the most?")
print(train[['Sex', 'Survived']].groupby(['Sex'], as_index=False).mean())

print("What Embarked can tell us?")
print(train[['Embarked', 'Survived']].groupby(['Embarked'], as_index=False).mean())
    
    
#we dont need passengerId and survived column in our independent variables so we are ignoring them
X       = train.iloc[:,1:8].values
#using dependent variable survived
y       = train.iloc[:,0].values

#We dont need passengerId column in our independent variables so we are ignoring it
test    = test.iloc[:,0:7].values



# Splitting the dataset into the Training set and Test set 20% into test set and 80% into training set
from sklearn.model_selection import train_test_split
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size = 0.20, random_state = 0)

#Feature Scaling to avoid despersion in the data so that we get values between 0 and 1 
from sklearn.preprocessing import StandardScaler
sc_Xtrain = StandardScaler()
X_train = sc_Xtrain.fit_transform(X_train)

sc_test = StandardScaler()
test = sc_test.fit_transform(test)

# Fitting Decision Tree Classification to the Training set
from sklearn.tree import DecisionTreeClassifier
classifier = DecisionTreeClassifier(criterion = 'entropy', random_state = 0)
classifier.fit(X_train, y_train)
# Predicting the Test set results
y_pred = classifier.predict(X_test)
from sklearn.metrics import confusion_matrix
cm = confusion_matrix(y_test, y_pred)


# Fitting Random Forest Classification to the Training set
from sklearn.ensemble import RandomForestClassifier
classifier = RandomForestClassifier(random_state=77,n_estimators=120, min_samples_leaf=7, min_samples_split=50,max_depth=5)
classifier.fit(X_train, y_train)
y_pred = classifier.predict(X_test)
from sklearn.metrics import confusion_matrix
cm = confusion_matrix(y_test, y_pred)

# Fitting Gradient boosting Classification to the Training set
from sklearn.ensemble import GradientBoostingClassifier
classifier = GradientBoostingClassifier(max_depth=2,
                                        learning_rate=0.025,
                                        n_estimators=300, 
                                        subsample=0.2,
                                        min_samples_leaf=4,
                                        verbose=True,
                                      ).fit(X_train,y_train)

y_pred = classifier.predict(X_test)
from sklearn.metrics import confusion_matrix
cm = confusion_matrix(y_test, y_pred)


# Fitting XGBoost Classification to the Training set
from xgboost import XGBClassifier
classifier = XGBClassifier(learning_rate=0.1,
                           n_estimators=500,
                           max_depth=4,
                           silent = False,
                           min_child_weight=5,
                           subsample=0.50,
                           gamma=0.40,
                           colsample_bytree=0.3,
                           seed=1)

classifier.fit(X_train, y_train)
y_pred = classifier.predict(X_test)
from sklearn.metrics import confusion_matrix
cm = confusion_matrix(y_test, y_pred)

# Fitting KNeighbors Classification to the Training set
from sklearn.neighbors import KNeighborsClassifier
classifier = KNeighborsClassifier(algorithm='auto', leaf_size=26, metric='minkowski', 
                           metric_params=None, n_jobs=1, n_neighbors=6, p=2, 
                           weights='uniform')
classifier.fit(X_train, y_train)
np.mean(classifier.predict(X_test)==y_test)*100

# Using Grid Search to tune parameters of our classifiers
from sklearn.model_selection import GridSearchCV

parameters = {'n_estimators': [4, 6, 9], 
              'max_features': ['log2', 'sqrt','auto'], 
              'criterion': ['entropy', 'gini'],
              'max_depth': [2, 3, 5, 10], 
              'min_samples_split': [2, 3, 5],
              'min_samples_leaf': [1,5,8]
             }

grid_search = GridSearchCV(estimator = classifier,
                           param_grid = parameters,
                           scoring = 'accuracy',
                           cv = 10,
                           n_jobs = -1)
grid_search = grid_search.fit(X_train, y_train)
best_accuracy = grid_search.best_score_
best_parameters = grid_search.best_params_




# Now let's insert result into result.csv file by using dictionary(Key, Value pair) 
y_result = classifier.predict(test)
Passengerid = []
for i in range(892,1310):
    Passengerid.append(i)
    
Passengerid

Result = pd.DataFrame({'PassengerId':Passengerid, 'Survived':y_result})

Result.to_csv(r'C:\Users\MY\Desktop\Titanic\result.csv', index = False)
