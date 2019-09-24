from sklearn.pipeline import Pipeline
from sklearn.feature_extraction.text import TfidfTransformer, CountVectorizer
from sklearn.linear_model import SGDClassifier
from sklearn.model_selection import train_test_split

import pandas as pd
import numpy as np

def clean_text(list_of_text):
    cleaned = []
    for data in list_of_text:
        cleaned.append(str(data).replace("\n", " ").replace("\xa0", ""))
    
    return cleaned

# load csv files when connection to db engine is error
df = pd.read_csv("examples.csv")

# first model, classify industry based on position only
df_feature_target = df[["position", "industry"]]
# drop if any NaN data
df_feature_target = df_feature_target.dropna()
X = clean_text(list(df_feature_target["position"]))
y = list(df_feature_target["industry"])
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# we use SGD because this model use many text case and have a good results
classifier = SGDClassifier(alpha=0.0001, average=False, \
            class_weight=None, epsilon=0.1, eta0=0.0, 
            fit_intercept=True, l1_ratio=0.15, learning_rate='optimal', 
            loss='hinge', max_iter=None, n_iter=50, n_jobs=1, penalty='l2',
            power_t=0.5, random_state=None, shuffle=True, 
            tol=None, verbose=0, warm_start=False)
            
model = Pipeline([('vectorizer', CountVectorizer(ngram_range=(1,2))),
                ('tfidf', TfidfTransformer(use_idf=True)),
                ('clf', classifier)])

model.fit(X_train, y_train)
print(model.score(X_test, y_test))
