# Import the dependencies.

import numpy as np

import sqlalchemy
import datetime as dt
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, inspect, func
from sqlalchemy.ext.declarative import declarative_base
from flask import Flask, jsonify


#################################################
# Database Setup
#################################################

#Establish connection to Hawaii sqlite file
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()

# reflect the tables
Base.prepare(engine, reflect=True)

# Save references to each table
measurement = Base.classes.measurement
Station = Base.classes.station

# Create our session (link) from Python to the DB
session = Session(engine)

#################################################
# Flask Setup
#################################################

#Initialize Flask
app = Flask(__name__)

#################################################
# Flask Routes
#################################################
@app.route("/")
def home():
    print("Server received request for 'Home' page...")

    """List all available api routes."""
    return (
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/start<br/>"
        f"/api/v1.0/start/end<br/>"
    )


#2. Create a route to the precipitation analysis queries and convert to a dictionary using date as the key and prcp as the value
#Return the JSON representation of your dictionary.

@app.route("/api/v1.0/precipitation")
def precipitation():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    """Return a list of precipitation (prcp)and date (date) data"""
    
    # Query results
    # Create new variable to store results from query to Measurement table for prcp and date columns
    precipitation_results = session.query(measurement.prcp, measurement.date).all()

    # Close session
    session.close()
    
     # Create an empty list of precipitation query values 
    precipitaton_values = []
     # Use a for loop to iterate through query results
    for prcp, date in precipitation_results:
         #create dictionary and append values to list created
        precipitation_dict = {}
        precipitation_dict["Date"] = date
        precipitation_dict["Precipitation"] = prcp
        precipitaton_values.append(precipitation_dict)

    return jsonify(precipitaton_values)
    
#3. /api/v1.0/stations

    # Return a JSON list of stations from the dataset.
    
@app.route("/api/v1.0/stations")
def station():

    session = Session(engine)
    # Create new variable to store results from query to measurement table for date and precipitation columns
    """Return a list of stations from the database"""
    station_results = session.query(Station.station,Station.id).all()

    session.close()
    
    stations_values = []
    for station, id in station_results:
        stations_values_dict = {}
        stations_values_dict['Station'] = station
        stations_values_dict['ID'] = id
        stations_values.append(stations_values_dict)
        
    return jsonify (stations_values)
    
#4./api/v1.0/tobs
#    Query the dates and temperature observations of the most-active station for the previous year of data.
@app.route("/api/v1.0/tobs")
def tobs():

    session = Session(engine)
    previous_year_results = session.query(measurement.date).all()

    session.close()

## Create query to find the most recent date in the database
    
    last_year_query_results = session.query(measurement.date).\
        order_by(measurement.date.desc()).first()

    print(last_year_query_results)
    # last_year_date returns row ('2017-08-23',), use this to create a date time object to find start query date
    
    # check to see if last year was correctly returned by creating dictionary to return last year value to browser in JSON format
    last_year_query_values = []
    for date in last_year_query_results:
        last_year_dict = {}
        last_year_dict["Date"] = date
        last_year_query_values.append(last_year_dict)
    print(last_year_query_values)
    # output: 'Date': '2017-08-23'

    # Create query_start_date by finding the difference between date time object of "2017-08-23" - 365 days
    query_start_date = dt.date(2017, 8, 23)-dt.timedelta(days =365)
    print(query_start_date)
    # output: '2016-08-23'

    # Create query to find most active station in the database

    active_station= session.query(measurement.station, func.count(measurement.station)).\
        order_by(func.count(measurement.station).desc()).\
        group_by(measurement.station).first()
    most_active_station = active_station[0]

    session.close()
     # active_station returns: ('USC00519281', 2772), index to get the first position to isolate most active station number
    print(most_active_station)
    # output: USC00519281

    # Create a query to find dates and tobs for the most active station (USC00519281) in the most recent year (> 2016-08-23)

    dates_tobs_last_year_query_results = session.query(measurement.date, measurement.tobs, measurement.station).\
        filter(measurement.date > query_start_date).\
        filter(measurement.station == most_active_station)
    

    # Create a list of dates,tobs,and stations to append to dictionary queried above.
    dates_tobs_last_year_query_values = []
    for date, tobs, station in dates_tobs_last_year_query_results:
        dates_tobs_dict = {}
        dates_tobs_dict["Date"] = date
        dates_tobs_dict["Tobs"] = tobs
        dates_tobs_dict["Station"] = station
        dates_tobs_last_year_query_values.append(dates_tobs_dict)
        
    return jsonify(dates_tobs_last_year_query_values)
#    Return a JSON list of temperature observations for the previous year.

#5. /api/v1.0/<start> and /api/v1.0/<start>/<end>
#    Return a JSON list of the minimum, average, and  maximum temperature for a specified start or start-end range.

@app.route("/api/v1.0/<start>")
# Define function, set "start" date entered by user as parameter for 'start_date' 
def start_date(start):
    session = Session(engine)

    """Return a JSON list of the minimum temperature, the average temperature, and the max temperature for a given start date."""

#    For a specified start, calculate TMIN, TAVG, and TMAX for all the dates greater than or equal to the start date.
    # Create query for minimum, average, and max tobs where query date is greater than or equal to the date the user submits in URL
    start_tobs_results = session.query(func.min(measurement.tobs),func.avg(measurement.tobs),func.max(measurement.tobs)).\
        filter(measurement.date >= start).all()
    
    session.close()

    # Create a list of min, avg,and max temps. Append with dictionary values in above query
    start_tobs_values =[]
    for TMIN, TAVG, TMAX in start_tobs_results:
        start_tobs_dict = {}
        start_tobs_dict["Minimum Temperature"] = TMIN
        start_tobs_dict["Average Temperature"] = TAVG
        start_tobs_dict["Maximum Temperature"] = TMAX
        start_tobs_values.append(start_tobs_dict)
    
    return jsonify(start_tobs_values)

# Create a route that returns the minimum, average, and maximum temperature observed for all dates greater than or equal to user-entered start date 

@app.route("/api/v1.0/<start>/<end>")

# Define function, set start and end dates entered by user as parameters for 'start/end_date' 
def Start_end_date(start, end):
    session = Session(engine)

    """Return a list of min, avg and max tobs between start and end dates entered"""
   
    #    For a specified start date and end date, calculate TMIN, TAVG, and TMAX for the dates from the start date to the end date, inclusive.
    # Create query for minimum, average, and max tobs where query date is greater than or equal to the start date and less than or equal to end date.

    start_end_tobs_results = session.query(func.min(measurement.tobs), func.avg(measurement.tobs), func.max(measurement.tobs)).\
        filter(measurement.date >= start).\
        filter(measurement.date <= end).all()

    session.close()
  
    # Create a list of min, avg and max temps. Append with dictionary values in above query
    start_end_tobs_values = []
    for TMIN, TAVG, TMAX in start_end_tobs_results:
        start_end_tobs_dict = {}
        start_end_tobs_dict["Minimum Temperature"] = TMIN
        start_end_tobs_dict["Average Temperature"] = TAVG
        start_end_tobs_dict["Maximum Temperature"] = TMAX
        start_end_tobs_values.append(start_end_tobs_dict)
    

    return jsonify(start_end_tobs_values)


#*Hints: join the station and measurement tables for some of the queries and use the Flask jsonify function to convert your API data to a valid JSON response object.*

if __name__ == '__main__':
    app.run(debug=True)