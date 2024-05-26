import requests
from bs4 import BeautifulSoup

''' 
    City1 = ["City1", "INSERT_CITY1_WEATHER.COM_URL_HERE"]
    City2 = ["City2", "INSERT_CITY2_WEATHER.COM_URL_HERE"]
    City3 = ["City3", "INSERT_CITY3_WEATHER.COM_URL_HERE"]
    
    locations = [City1, City2, City3]
'''

#Working on making this integrated into a class
class Weather_App():
    def __init__(self, location):
        self.location = location
        page = requests.get(location[1])
        soup = BeautifulSoup(page.content, 'html.parser')
        self.page_content = soup.find(id="MainContent")

    '''Prints current location of data scraping
        @Params:    self:               Weather_App object
        @Returns:   none'''
    def current_location(self):
        print(f"Your current location for weather is {str(self.location[0])}")

    '''Sets the location to scrape the weather data from
        @Params:    self:               Weather_App object
        @Returns:   none'''
    def set_location(self, location):
        self.location = location
        page = requests.get(location[1])
        soup = BeautifulSoup(page.content, 'html.parser')
        self.page_content = soup.find(id="MainContent")
        print(f"Set current location to {str(self.location[0])}")

    '''Returns the current weather condition, temperature, and time of poll
        @Params:    self:               Weather_App object
        @Returns:   weather_conditions: List with current time, temperature, condition, and location'''
    def current_weather(self):
        #Test for html updates in the website
        location = self.page_content.find(class_="CurrentConditions--location--1YWj_")
        if location == None:
            print("HTML has been updated. Please fix")
            return ["titles", "update", "Please", "HTML"]

        #Data gathering section
        location = self.page_content.find(class_="CurrentConditions--location--1YWj_").get_text()     #Gets the location text from the Current Conditions section
        timestamp = self.page_content.find(class_="CurrentConditions--timestamp--1ybTk").get_text()   #Gets the timestamp text from the Current Conditions section

        temp = self.page_content.find(class_="CurrentConditions--tempValue--MHmYY").get_text()        #Gets the temperatue text from the Current Conditions section
        condition = self.page_content.find(class_="CurrentConditions--phraseValue--mZC_p").get_text() #Gets the condition text from the Current Conditions section

        timestamp = timestamp.replace("\xa0As of ", "")

        weather_conditions = [timestamp, temp, condition, location]
        return weather_conditions

    '''Formats the current weather into a sentence: relies on output from current_weather()
        @Params:    self:               Weather_App object
        @Returns:   current_weather:    String of current temp, weather condition, location, time'''
    def format_current_weather(self):
        currentweather = self.current_weather()
        currentweather[0] = currentweather[0].replace("As", "as")
        weather_str = f"It is currently {currentweather[2]} and {currentweather[1]} F in {currentweather[3]} as of {currentweather[0]}"
        return weather_str

    '''Returns the high and low temperature for today
        @Params:    self:               Weather_App object
        @Returns:   statement           String with readable high and low temperatures'''
    def todays_high_and_low(self):
        highandlow = self.page_content.find(class_="CurrentConditions--tempHiLoValue--3T1DG").get_text()

        highandlow = highandlow.replace("Day", "")
        highandlow = highandlow.replace("Night", "")
        highandlow = highandlow.strip()

        iterator = 0
        high = ""
        low = ""
        for i in highandlow:
            if iterator < 4:
                high += i
            if iterator >= 7 and iterator < len(highandlow):
                low += i
            iterator += 1
        high = high.strip()
        low = low.strip()
        high_low = [high, low]
        return f"Today's high: {high_low[0]} F\nToday's low: {high_low[1]} F"

    '''This formats the strings for the chance of rain
        Method is called in get_precip()
        @Params:    self:               Weather_App object
                    chances:            List of rain chances
        @Returns:   precip:             List with formatted chances of rain'''
    def format_precip(self, chances):
        for i in chances:
            if i == "--":
                i = "?"
        return chances

    '''Returns the highest integer rain chance of the morning, afternoon, evening, overnight sections of today
        @Params:    self:               Weather_App object
                    chances:            List of rain chances
        @Returns:   chance_of_rain:     List with highgest rain chance and time of rain'''
    def highest_rain_chance(self, chances):
        rainchance = 0
        for i in chances:
            if i == "?":
                i = -1
            else:
                if int(i) > rainchance:
                    rainchance = i
        time_of_day = ["Morning","Afternoon","Evening","Overnight"]
        time_of_rain = time_of_day[chances.index(int(rainchance))]
        chance_of_rain = [str(rainchance), time_of_rain]
        return chance_of_rain

    '''This outputs a string stating the highest chance of rain for today
        @Params:    self:               Weather_App object
        @Calls:     format_precip()
                    highest_rain_chance()
        @Returns:   statement:          String with readable highest chance of rain statement'''
    def get_precip(self):
        rain = self.page_content.find(class_="WeatherTable--columns--6JrVO WeatherTable--wide--KY3eP").get_text() #Gotten from "Today's Forecast for location" section

        rain = rain.replace("--","Chance of Rain -1%").split("Chance of Rain")         #Splits rain into 4 parts
        morning = int(rain[1].split("%")[0])             #Takes the beginning of each part
        afternoon = int(rain[2].split("%")[0])
        evening = int(rain[3].split("%")[0])
        night = int(rain[4].split("%")[0])
        chances = [morning, afternoon, evening, night]


        highest_rain = self.highest_rain_chance(self.format_precip(chances))

        rain_output = f"Highest chance of rain is {highest_rain[0]}% in the {highest_rain[1]}"
        return rain_output