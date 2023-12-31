# -*- coding: utf-8 -*-
"""IMDB_Bidirectional.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1s_LQqOtYr7cE9Z7MEDRjUMFV361cJSO_
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.model_selection import train_test_split
import string
from nltk.corpus import stopwords

from google.colab import drive
drive.mount('/content/drive')

path='/content/drive/MyDrive/IMDB_Dataset.csv'
data=pd.read_csv(path)

data.shape

data_IMDB=data.iloc[:30000] # Taking Big subset of data as whole data computationally expensive
data_IMDB['review'][1]
data_IMDB.shape

data_IMDB['sentiment'].value_counts()

"""## Preprocessing of data"""

data_IMDB.isnull().sum()

data_IMDB.duplicated().sum()

data_IMDB.drop_duplicates(inplace=True)

data_IMDB.duplicated().sum()

data_IMDB.shape

import nltk
nltk.download('punkt')
nltk.download('stopwords')
from nltk.corpus import stopwords
import string

# Define the text preprocessing pipeline
def preprocess_text(text):
    # Tokenize the text
    tokens = nltk.word_tokenize(text)
    # Remove stopwords
    stopwords_list = stopwords.words('english')
    filtered_tokens = [token for token in tokens if token not in stopwords_list]
    
    # Lowercase the tokens
    lowercase_tokens = [token.lower() for token in filtered_tokens]
    
    # Remove punctuation
    translator = str.maketrans('', '', string.punctuation)
    no_punct_tokens = [token.translate(translator) for token in lowercase_tokens]
    
    # Remove empty tokens
    final_tokens = [token for token in no_punct_tokens if token]
    
    # Join the tokens back into a single string
    preprocessed_text = ' '.join(final_tokens)
    
    return preprocessed_text

data_IMDB['review']= data_IMDB['review'].apply(preprocess_text)

X= data_IMDB['review']
print(X.shape)
y = data_IMDB['sentiment']

print(X)

print(y)

from sklearn.preprocessing import LabelEncoder
encoder = LabelEncoder()
y = encoder.fit_transform(y)

print(y)

"""##RNN Model"""

import tensorflow 
import keras
from tensorflow.keras.preprocessing.text import one_hot
voc_size=5000
review= [one_hot(words,voc_size) for words in data_IMDB['review']]
review

from tensorflow.keras.preprocessing import sequence
maxlen=100
padded_review = sequence.pad_sequences(review, maxlen=maxlen)

from sklearn.model_selection import train_test_split

# Split the data into train and test sets
x_train, x_test, y_train, y_test = train_test_split(padded_review, y, test_size=0.2, random_state=0)

# Split the train set into train and validation sets
x_train, x_val, y_train, y_val = train_test_split(x_train, y_train, test_size=0.25, random_state=0)

# define the model
from keras.layers import LSTM, Dense, Embedding, Bidirectional
from keras.callbacks import EarlyStopping
import numpy as np
from keras.datasets import imdb
from keras.models import Sequential
from keras.layers import LSTM, Dense, Embedding
from keras.preprocessing import sequence
from keras.callbacks import EarlyStopping
model = Sequential()
model.add(Embedding(voc_size, 32, input_length=maxlen))
model.add(Bidirectional(LSTM(64)))
model.add(Dense(1, activation='sigmoid'))

# compile the model
model.compile(loss='binary_crossentropy',
              optimizer='adam',
              metrics=['accuracy'])
# define early stopping
early_stop = EarlyStopping(monitor='val_loss', patience=2, verbose=1)
# train the model
hist = model.fit(x_train, y_train,
          batch_size= 32,
          epochs=10,
          validation_data=(x_val, y_val),callbacks=[early_stop])

# evaluate the model on the testing data
y_pred_prob = model.predict(x_test)
y_pred = (y_pred_prob > 0.5).astype(int)
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, confusion_matrix
acc = accuracy_score(y_test, y_pred)
print("Test Accuracy: ", acc)
# precision score
precision = precision_score(y_test, y_pred)
print('Precision:', precision)

# recall score
recall = recall_score(y_test, y_pred)
print('Recall:', recall)

# F1 score
f1 = f1_score(y_test, y_pred)
print('F1 score:', f1)

# confusion matrix
confusion_mat = confusion_matrix(y_test, y_pred)
print('Confusion matrix:\n', confusion_mat)

import matplotlib.pyplot as plt

# plot accuracy during training
plt.plot(hist.history['accuracy'])
plt.plot(hist.history['val_accuracy'])
plt.title('Model Accuracy')
plt.ylabel('Accuracy')
plt.xlabel('Epoch')
plt.legend(['Train', 'Validation'], loc='upper left')
plt.show()