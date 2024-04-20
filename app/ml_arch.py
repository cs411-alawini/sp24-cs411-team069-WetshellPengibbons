import numpy as np
import pandas as pd
import sqlalchemy
import pandas as pd
from gensim.models import Word2Vec
from gensim.models import FastText
import nltk
import fasttext


def get_word_embeddings(pool):
    # Intialize NLTK
    nltk.download('punkt')
    # Get data from GCS and store in df
    with pool.connect() as db_conn:
        query = sqlalchemy.text("SELECT CourseTitle, CourseDescription FROM CourseInfo")
        result_proxy = db_conn.execute(query)
        result_set = result_proxy.fetchall()
        df = pd.DataFrame(result_set, columns=result_proxy.keys())
    
    # Compute tokens of course descriptions
    df['all_text'] = df.apply(lambda x: ' '.join(x.dropna().astype(str)), axis=1)
    # Get vectorized data
    df['all_text'].to_csv('training_data.txt', index=False, header=False)
    # Train Model
    model = fasttext.train_unsupervised('training_data.txt', model='skipgram')
    # Save Model
    model.save_model('fasttext_model.bin')


