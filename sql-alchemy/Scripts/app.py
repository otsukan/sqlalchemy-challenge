# Importing necessary modules to analyze and visualize the climate of Honolulu, Hawaii.
from matplotlib import style
style.use('fivethirtyeight')
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd 
import datetime as dt
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func, inspect
from sqlalchemy.sql import label
import pandas as pd
import matplotlib.dates as mdates
from datetime import datetime

# setting path to hawaii.sqlite file.
database_path = "Resources/hawaii.sqlite"

# creating a variable that creates and holds the starting point and home base of interaction between us(python) and the hawaii.sqlite database/local files.
engine = create_engine(f"sqlite:///{database_path}")

# using the automap_base  and prepare functions to create an automated mapping of the hawaii.sqlite database, such as a general layout of how the data is structured and related.
Base = automap_base()
# Using the prepare function to reflect the mapping.
Base.prepare(engine, reflect=True)

# Using the functional Base variable created above to find out the names of the hawaii.sqlite classes/tables the automapping above created.
Base.classes.keys()

# saving the tabels that the automapping is referencing to variables for operation later on.
Measurement = Base.classes.measurement
Station = Base.classes.station

# creating a session variable that will allow the our python scripts to communicate with the hawaii database.
session = Session(engine)

# using the __dict__ function to get a feel for the mapping of the Measurement table.
first_row = session.query(Measurement).first()
first_row.__dict__

# using the __dict__ function like above to see the station data.
first_row = session.query(Station).first()
first_row.__dict__

# seeing how  many years of data we have(2011-2017).
session.query(Measurement.date).order_by(Measurement.date.desc()).first()

# obtaining only the date and precipiation columns and filtering out so we only have the last 12 months of data.
data_2017 = session.query(Measurement.date, Measurement.prcp).    filter(Measurement.date >= "2016-08-23").    filter(Measurement.date <= "2017-08-23").all()
# previewing data.
data_2017[0:10]


# creating a prcp dataframe out of the data_2017 data created above.
prcp_data_2017 = pd.DataFrame(data_2017)

# reformatting the date column from object to datestamp
prcp_data_2017["date"] = prcp_data_2017["date"].astype("datetime64[ns]")

# previewing prcp_data_2017 data
prcp_data_2017.head()

# setting prcp_data_2017 index as date.
prcp_data_2017 = prcp_data_2017.set_index("date")

# sorting the pandas_data_2017 to have all dates appear in order.
sorted_prcp_data_2017 = prcp_data_2017.sort_index()

# verifying the data is sorted by dates.
sorted_prcp_data_2017.head()

# dropping all rows with NaN entries/cleaning up the data. 
sorted_prcp_data_2017 = sorted_prcp_data_2017.dropna()

# previewing the changes made worked.
sorted_prcp_data_2017.head()

# creating a dictionary out of sorted_prcp dataframe with dates as the keys, which is for the purpose of creating an api page that will be done towards the bottom.
prcp_dict = sorted_prcp_data_2017.reset_index()
# converting date column to string.
prcp_dict["date"] = prcp_dict["date"].astype(str)
# using pivot funtion to put all precipitations by station recored on same date into own column by that date, instead of data only in one column. 
prcp_dict = prcp_dict.pivot(columns="date", values="prcp")
# looping through columns to not include NaN entries and subsequently creating a dictionary.
prcp_dict = {col: prcp_dict[col].dropna().to_dict() for col in prcp_dict}
# previewing results.
prcp_dict["2016-08-23"]


# creating a barchart that measures precipitation levels throughout the last 12 months by stations.
fig, ax = plt.subplots()
sorted_prcp_data_2017.plot(ax=ax)
# creating labels for the barchart.
plt.title("Precipitation levels throughout Hawaii (2016-2017)")
plt.ylabel("Precipitation Levels")
# #set ticks every month
ax.xaxis.set_major_locator(mdates.MonthLocator())
# #set major ticks format
ax.xaxis.set_major_formatter(mdates.DateFormatter('%b'))
plt.setp(ax.xaxis.get_majorticklabels(), rotation=-0, ha="left" )
# saving bargraph as png file.
# plt.savefig("Precipitation levels throughout Hawaii in last 12 months")

# calculating the total number of weather stations in our database in hawaii.
number_of_stations = session.query(Station.id, Station.name).count()
# printing out the results into readable form.
print(f"There are {number_of_stations} stations in our hawaii database")

# counting the number of observations(temperature observations data) of each station from 2010-2017 and recording them in order from greatest to least in a list variable.
observation_count = session.query(Station.name, Measurement.station, func.count(Measurement.tobs)).    filter(Measurement.station == Station.station).group_by(Measurement.station).order_by(func.count(Measurement.tobs).desc()).all()

# checking the results of the observation count query preformed above that is contained in a list variable.
observation_count

# printing what station had most temperature observations from 2010-2017 and the corresponding number of recordings.
print(f"Station {observation_count[0][0]} had the most temperature observation data recordings totaling {observation_count[0][2]} from 2011-2017.")

# counting the number of temperature observations for last 12 months of data according to each station and ordering them from greatest to least within a list variable.
tobs_data = session.query(Station.name, Measurement.station, Measurement.tobs, func.count(Measurement.tobs)).    filter(Measurement.station == Station.station).    filter(Measurement.date >= "2016-08-23").    filter(Measurement.date <= "2017-08-23").group_by(Measurement.station).order_by(func.count(Measurement.tobs).desc()).all()

# checking the results of the above procudure held in the tobs_data variable.
tobs_data

# verifing name of the station with most frequent temp observations.
tobs_data[0][0]

# Based on the above filtration, filtering the data to give us only the data of the station that had the most temperature observations for last 12 months.
most_frequent_station = session.query(Measurement.station, Station.name, Measurement.tobs, Measurement.date).    filter(Measurement.station == Station.station).    filter(Measurement.date >= "2016-08-23").    filter(Measurement.date <= "2017-08-23").    filter(Station.name == tobs_data[0][0]).all()

# verifing the above process worked.
most_frequent_station[0:10]

# creating a pandas dataframe from above list in order to create a histogram.
tob_most_frequent_station = pd.DataFrame(most_frequent_station, columns=["Station", "Name of Station", "Temperature Observation", "Date"])

# removing the station columnns and date column.
tob_most_frequent_station = tob_most_frequent_station[["Name of Station", "Temperature Observation"]]

# previewing the pandas_most_frequent_data dataframe.
tob_most_frequent_station.head()

# creating a histogram that shows the most frequent temperature observations in the last 12 months at Waikiki, which had the most temperature observations out of all the weather stations.
tob_most_frequent_station.hist(bins=12)
# labeling the histogram.
plt.title("Frequency of Temperatures recorded at Waikiki for last 12 Months")
plt.ylabel("Frequency")
plt.xlabel("Temperature")
plt.xlim(60,83)
# saving histogram as png file.
# plt.savefig("Frequency of Temperatures recorded at Waikiki (station with most observations) for last 12 Months")

# From here on out creating an online webpage application using flask.

# Importing Flask and Jsonify in order to create a server.
from flask import Flask, jsonify

# Making a variable server enabled through the Flask function. 
app = Flask(__name__)

# Creating a route that will list available routes.
@app.route("/")
def home():
    # printing backend response.
    print("Server received request for 'home' page...")
    # printing frontend response.
    return (
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>" 
        f"/api/v1.0/station/api/v1.0/tobs<br/>"
        f"/api/v1.0/<start><br/>"
        f"/api/v1.0/<start>/<end>"
    )

# creating a route to precipitation data for the last 12 months in Hawaii at multiple stations.
@app.route("/api/v1.0/precipitation")
# creating the calculating function that uses the prcp_dict variable created above if you recall.
def precipitation():
    # printing the backend response.
    print("Server received request for 'precipitation' page...")
    # printing frontend information.
    return jsonify(prcp_dict)

# creating a route to find a list of that station names in Hawaii.
@app.route("/api/v1.0/stations")
# creating function.
def stations():
    # creating a session with the engine.
    session = Session(engine)
    # creating a list of the station names.
    stations = session.query(Station.id, Station.name)
    station_names = []
    for name in stations:
        station_names.append(name[1])
    # printing back of house responses.
    print("Server received request for 'stations' page...")
    # printing results on webpage.
    return jsonify(station_names)

# developing a webpage with temperature observation data in Hawaii for the last 12 months at all stations.
@app.route("/api/v1.0/tobs")
# creating function to give me the info desired.
def tobs():
    # creating a connection to the Hawaii database.
    session = Session
    # creating a list of temperature observation data throughout the last 12 months, including the station that did the recording and on what date. 
    tobs_app = session.query(Station.name, Measurement.tobs, Measurement.date).    filter(Measurement.station == Station.station).    filter(Measurement.date >= "2016-08-23").    filter(Measurement.date <= "2017-08-23").all()
    # printing backend reponse.
    print("Server received request for 'tobs' page...")
    # returning user information on webpage.
    return jsonify(tobs_app)

# developing webpage that calculates min, max, average temp from start date to very end, where user puts in start date.
@app.route("/api/v1.0/<start>")
# creating function that finds info from start date entered by user.
def start_stats(start):
    # creating new session with database.
    session = Session(engine)
    # finding the data based on user response.
    # if user uses right date format.
    try:
       # finding the data based on user date response.
        start = datetime.strptime(start, "%Y-%m-%d")
        start_stat = session.query(label('low', func.min(Measurement.tobs)), label('high', func.max(Measurement.tobs)), label('average', func.avg(Measurement.tobs))).\
            filter(Measurement.date >= start).all()
        # printing the backend response.
        print("Server received request for 'start' page...")
        # printing the results to the user.
        return jsonify(start_stat)
    # if user uses wrong date format.
    except:
        # reponse to user on webpage if used wrong date format.
        return jsonify("error: Either date not found in database or not in proper format (ie.2017-03-05) not (2014/02/12), (08/12/2017), ect...")

# creating webpage like above that calculates the min, max, average temp, but where user puts both start and end date..
@app.route("/api/v1.0/<start>/<end>")
# creating the function to calculate the above wants.
def start_end_stats(start, end):
    # creating that session again.
    session = Session(engine)
    # if user uses right date format.
    try:
        # setting date into specific format.
        start = datetime.strptime(start, "%Y-%m-%d")
        end = datetime.strptime(end, "%Y-%m-%d")
        # looking for date in database.
        start_end_stat = session.query(label('low', func.min(Measurement.tobs)), label('high', func.max(Measurement.tobs)), label('average', func.avg(Measurement.tobs))).\
            filter(Measurement.date >= start).\
            filter(Measurement.date <= end).all()
    
        # printing the backend response.
        print("Server received request for 'start and end dates' page...")
        # printing the results to the user.
        return jsonify(start_end_stat)
    # if user uses wrong date format.
    except:
        # reponse to user on webpage if used wrong date format.
        return jsonify("error: Either date not found in database or not in proper format (ie.2017-03-05) not (2014/02/12), (08/12/2017), ect...")

if __name__ == "__main__":
    app.run(debug=True)
