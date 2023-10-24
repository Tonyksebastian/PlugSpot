from django.test import TestCase

# Create your tests here.
from functools import reduce
import pandas as pd
from sklearn.preprocessing import OneHotEncoder
from flask import Flask, render_template, request
from sklearn.preprocessing import StandardScaler, MinMaxScaler
from scipy.stats import zscore
from sklearn.ensemble import StackingRegressor
from sklearn.neural_network import MLPClassifier
import seaborn as sns  # Corrected seaborn import
import matplotlib.pyplot as plt
import numpy as np
from datetime import datetime, timedelta
from flask import Flask, render_template, request


def unique(list1):
    ans = reduce(lambda re,x : re+[x] if x not in re else re, list1,[])
    print(ans)

n1features=[]
n2features=[]
x_scaler =MinMaxScaler()
y_scaler=MinMaxScaler()
regr =MLPClassifier(random_state=1,max_iter =500)


app=Flask(__name__,static_url_path='')

@app.route('/')
def route():
    return render_template('home.html')

@app.route('/train')
def train():
    data= pd.read_csv('Train.csv')
    data = data.sort_values(by=['date_time'],ascending=True).reset_index(drop=True)
    last_n_hours =[1,2,3,4,5,6]
    for n in last_n_hours:
        data[f'last_{n}_hour_traffic'] = data['traffic_volume'].shift(n)
    data = data. dropna().reset_index(drop=True)
    data.loc[data['is_holiday']!= 'None','is_holiday']= 1
    data.loc[data['is_holiday']!= 'None','is_holiday']= 0
    data['is_holiday'] = data['is_holiday'].astype(int)

    data['date_time'] = pd.to_datetime(data['date_time'])
    data['hour'] = data['date_time'].map(lambda x: int(x.strftime("%H")))
    data['month_date'] = data['date_time'].map(lambda x: int(x.strftime("%d")))
    data['weekday'] = data['date_time'].map(lambda x: x.weekday()+1)
    data['month'] = data['date_time'].map(lambda x: int(x.strftime("%m")))
    data['year'] = data['date_time'].map(lambda x: int(x.strftime("%Y")))
    data.to_csv("my_traffic_dataset.csv",index=None)

    sns.set()
    plt.rcParams['font.sans-serif'] =['SimHei']
    plt.rcParams['axes.unicode_minus'] =False
    Warning.filterwarnings('ignore')
    data =pd.read_csv("my_traffic_dataset.csv")
    data = data.sample(10000).reset_index(drop=True)
    label_columns = ['weather_type','weather_description']
    numeric_columns = ['is_holiday','temperature','weekday','hour','month_day','year','month']
    n1 = data['weather_type']
    n2= data['weather_description']
    unique(n1)
    unique(n2)
    n1features =['Rain','Clounds','Clear','Snow','Mist','Drizzle','Haze','Thunderstorm','Fog','Smoke','Squail']
    n2features =['light rain','few clouds','Sky is Clear','light snow','sky is clear','mist','broken clouds','moderate rain','light intensity drizzle','heavy intensity rain','overcast clouds','heavy intensity drizzle','scattered clouds','fog','proximity thunderstorm','proximity shower rain']


    n11 = []
    n22= []
    for i in range(10000):
        if(n1[i]) not in n1features:
            n11.append(0)
    else:
        n11.append((n1features.index(n1[i]))+1)
    if n2[i] not in n2features:
        n22.append(0)
    else:
        n22.append((n2features.index(n2[i]))+1)

    data['weather_type']= n11
    data['weather_description'] =n22
    features = numeric_columns+label_columns
    target = ['traffic_volume']
    x=data[features]
    y=data[target]

    print(data[features].hist(bins=20,))
    data['traffic_volume'].hist(bins=20)


    """Feature Scaling"""

    X = x_scaler.fit_transform(X)
    y= y_scaler.fit_transform(y).flatten()
    Warning.filterwarnings('ignore')


    """Train the Model"""

    regr.fit(X,y)
    print('predicted output :=',regr.predict(X[:10]))
    print('Actual output :=',y[:10])
    return render_template('indexx.html')


@app.route('/predict',methods=['POST'])
def predict():
    ip=[]
    if(request.form['is_holiday']=='yes'):
        ip.append(1)
    else:
        ip.append(0)

    ip.append(int(request.form['temperature']))
    ip.append(int(request.form['day']))
    ip.append(int(request.form['time'][:2]))
    D =request.form['date']
    ip.append(int(D[8:]))
    ip.append(int(D[:4]))
    ip.append(int(D[5:7]))
    s1 = request.form.get('x0')
    s2 = request.form.get('x1')
    if(s1) not in n1features:
        ip.append(0)
    else:
        ip.append((n1features.index(s1))+1)
    if s2 not in n2features:
        ip.append(0)
    else:
        ip.append ((n2features.index (s2)) + 36 )
    ip= x_scaler.transform([ip])
    out = regr.predict(ip)
    print('Befor inverse Scalling :',out)
    y_pred = y_scaler.inverse_transform([out])
    print('Traffic Volume :',y_pred)
    s=''
    if(y_pred <= 10000):
        print("No trafic")
        s = "No trafic "
    elif y_pred > 1000 and y_pred <=3000:
        print("Busy or Normal Traffic")
        s = "Busy or Normal Traffic"
    else:
        print ("Very Busy Traffic ")
        s = "Very Busy Traffic "

    return render_template('output.html', datal = ip, op=y_pred,statment =s)

if __name__ == '__main__':
    app.run(debug=True)


