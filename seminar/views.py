from django.shortcuts import render
import pickle
from sklearn.metrics import accuracy_score
from sklearn.preprocessing import StandardScaler
from .models import TrafficData
from matplotlib import pyplot as plt
import joblib
# import seaborn as sns
import io
import urllib, base64

import matplotlib
matplotlib.use('agg')  # Set the Matplotlib backend to 'agg' before importing pyplot
from matplotlib import pyplot as plt

# Create your views here.
def hi(request):
    return render(request,'index.html')

# Load the trained model
# with open('models/traffic_classification_model.pkl', 'rb') as model_file:
#     clf = pickle.load(model_file)

def predict_traffic(request):
    if request.method == 'POST':
        # Get form data and preprocess it as you did before
        is_holiday = request.POST.get('is_holiday')
        temperature_celsius = float(request.POST.get('temperature'))  # Get temperature in Celsius
        temperature = temperature_celsius + 273.15  # Convert to Kelvin
        hour = int(request.POST.get('hour'))
        month_day = int(request.POST.get('month_day'))
        month = int(request.POST.get('month'))
        year = int(request.POST.get('year'))
        weekday = int(request.POST.get('weekday'))
        location = request.POST.get('location')

        # Encode 'is_holiday' as 0 or 1
        is_holiday_encoded = 0 if is_holiday == 'None' else 1

        # Map 'location' to its encoding
        location_encoded = {'urban': 2, 'rural': 1, 'remote': 0}.get(location, -1)

        if location_encoded == -1:
            return render(request, 'traffic_prediction.html', {'error_message': 'Invalid location'})

        # Create a new input data
        new_data = [[is_holiday_encoded, temperature, hour, month_day, month, year, weekday, location_encoded]]

        scaler = joblib.load('models/scaler.pkl')
        new_data = scaler.transform(new_data)

        # Make a prediction
        prediction = clf.predict(new_data)[0]

        # Data for visualization
        predicted_probabilities = clf.predict_proba(new_data)[0]
        traffic_labels = ['Heavy Traffic', 'Medium Traffic', 'Not Busy']

        # Traffic Condition Bar Chart
        plt.figure(figsize=(6, 4))
        plt.bar(traffic_labels, predicted_probabilities, color=['red', 'blue', 'green'])
        plt.ylabel('Probability')
        plt.title('Traffic Condition Prediction')

        # Encode the chart in base64
        traffic_chart_image = io.BytesIO()
        plt.savefig(traffic_chart_image, format='png')
        traffic_chart_image_base64 = base64.b64encode(traffic_chart_image.getvalue()).decode()
        plt.close()

        # Example of a Pie Chart for Weather Condition
        weather_labels = ['Rainy', 'Sunny', 'Snowy', 'Other']
        weather_probabilities = [0.25, 0.45, 0.2, 0.1]
        plt.figure(figsize=(6, 6))
        plt.pie(weather_probabilities, labels=weather_labels, autopct='%1.1f%%')
        plt.title('Weather Condition')

        # Encode the weather chart in base64
        weather_chart_image = io.BytesIO()
        plt.savefig(weather_chart_image, format='png')
        weather_chart_image_base64 = base64.b64encode(weather_chart_image.getvalue()).decode()
        plt.close()

        # Create a line chart for Temperature and Year
        plt.figure(figsize=(8, 4))
        plt.plot([year], [temperature_celsius], marker='o', color='blue', label='Temperature (°C)')
        plt.xlabel('Year')
        plt.ylabel('Temperature (°C)')
        plt.title('Temperature Over the Years')
        plt.legend()

        # Encode the chart in base64
        temperature_year_chart_image = io.BytesIO()
        plt.savefig(temperature_year_chart_image, format='png')
        temperature_year_chart_image_base64 = base64.b64encode(temperature_year_chart_image.getvalue()).decode()
        plt.close()

        # # Scatter Plot for Time and Accuracy
        # plt.figure(figsize=(8, 4))
        # plt.scatter([hour], [predicted_accuracy], c='blue', label='Time vs. Accuracy')
        # plt.xlim(0, 24)  # Adjust the x-axis limits according to your data
        # plt.ylim(0, 1)
        # plt.xlabel('Hour of the Day')
        # plt.ylabel('Accuracy')
        # plt.title('Time vs. Accuracy')
        # plt.legend()

        # # Encode the scatter plot in base64
        # time_accuracy_plot_image = io.BytesIO()
        # plt.savefig(time_accuracy_plot_image, format='png')
        # time_accuracy_plot_image_base64 = base64.b64encode(time_accuracy_plot_image.getvalue()).decode()
        # plt.close()


        # Render the result with the charts
        return render(request, 'traffic_prediction.html', {
            'prediction': prediction,
            'temperature_year_chart_image': temperature_year_chart_image_base64,
            # 'time_accuracy_plot_image_base64':time_accuracy_plot_image_base64,
            'traffic_chart_image': traffic_chart_image_base64,
            'weather_chart_image': weather_chart_image_base64,           
        })
    else:
        return render(request, 'traffic_prediction.html')