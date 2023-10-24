from django import forms



from django import forms

class TrafficPredictionForm(forms.Form):
    is_holiday = forms.ChoiceField(
        choices=[('None', 'None'), ('Holiday', 'Holiday')],
        label='Is it a holiday?'
    )
    temperature = forms.FloatField(
        label='Temperature (in Kelvin)'
    )
    hour = forms.IntegerField(
        label='Hour of the day (0-23)'
    )
    month_day = forms.IntegerField(
        label='Day of the month (1-31)'
    )
    month = forms.IntegerField(
        label='Month (1-12)'
    )
    year = forms.IntegerField(
        label='Year'
    )
    weekday = forms.IntegerField(
        label='Day of the week (0-6, where 0 is Monday)'
    )
    location = forms.ChoiceField(
        choices=[
            ('urban', 'Urban'),
            ('rural', 'Rural'),
            ('remote', 'Remote')
        ],
        label='Location'
    )
    # weather_type = forms.ChoiceField(
    #     choices=[
    #         ('Rain', 'Rain'),
    #         ('Drizzle', 'Drizzle'),
    #         ('Clouds', 'Clouds'),
    #         ('Clear', 'Clear'),
    #         ('Thunderstorm', 'Thunderstorm'),
    #         ('Fog', 'Fog'),
    #         ('Mist', 'Mist')
    #     ],
    #     label='Weather Type'
    # )
    # weather_description = forms.ChoiceField(
    #     choices=[
    #         ('Mist', 'Mist'),
    #         ('Haze', 'Haze'),
    #         ('Fog', 'Fog'),
    #         ('Drizzle', 'Drizzle'),
    #         ('Light Rain', 'Light Rain'),
    #         ('Moderate Rain', 'Moderate Rain'),
    #         ('Light Intensity Drizzle', 'Light Intensity Drizzle'),
    #         ('Sky is Clear', 'Sky is Clear'),
    #         ('Scattered Clouds', 'Scattered Clouds'),
    #         ('Broken Clouds', 'Broken Clouds')
    #     ],
    #     label='Weather Description'
    
