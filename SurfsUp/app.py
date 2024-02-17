# Import the dependencies.
from flask import Flask, jsonify
import numpy as np
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
import datetime as dt
from datetime import timedelta 


#################################################
# Database Setup
#################################################

# Create engine using the `hawaii.sqlite` database file
engine = create_engine("sqlite:///Resources/hawaii.sqlite")
# Declare a Base using `automap_base()`
Base = automap_base()
# Use the Base class to reflect the database tables
Base.prepare(autoload_with=engine)

# Assign the measurement class to a variable called `Measurement` and
# the station class to a variable called `Station`
Measurement = Base.classes.measurement
Station = Base.classes.station

# Create a session
#session = Session(engine)
#################################################
# Flask Setup
#################################################
app = Flask(__name__)


#################################################
# Flask Routes
#################################################

def previous_year_date():
    #Creating Session
    session = Session(engine)
    # Defining the most recent year in the Measurement database
    recent_date = session.query(func.max(Measurement.date)).first()[0]
    f_date = dt.datetime.strptime(recent_date, "%Y-%m-%d") - dt.timedelta(days=365)
    session.close()

    # Return date
    return(f_date)

@app.route("/")
def homepage():
        """Welcome to the SQL-Alchemy App!."""
        return (
                f"The available routes are:<br/>"
                f"/api/v1.0/precipitation<br/>"
                f"/api/v1.0/stations<br/>"
                f"/api/v1.0/tobs<br/>"
                f"/api/v1.0/<start><br/>"
                f"/api/v1.0/<start>/<end><br/>"
                f"Note: to access values between a start and end date enter both dates using format: YYYY-mm-dd/YYYY-mm-dd"
        )

@app.route("/api/v1.0/precipitation")
def precipitation():
    # Creating a link from Python to the database
    session = Session(engine)
    """Returning a list of all Precipitation Data"""  

    # Query for all precipitation data
    prcp_data = session.query(Measurement.date, Measurement.prcp).all()
    
    #Closing session
    session.close()
    
    # Creating a dictonary from the row data and appending it to a list of prcp
    prcp_list = []
    for date, prcp in prcp_data:
      date_prcp_dict = {}
      date_prcp_dict["date"] = date
      date_prcp_dict["prcp"] = prcp
      prcp_list.append(date_prcp_dict)

    return jsonify(prcp_list)


@app.route("/api/v1.0/stations")
def stations():
    #Creating a link from Python to the database
    session = Session(engine)
    """"Returning a list of all the Stations"""  

    # Query for all the stations
    results = session.query(Station.station, Station.name).all()
    session.close()
    # Creating a dictonary from the row data and appending it to a list of stations
    all_stations = []
    for station, name in results:
         all_stations_dict = {}
         all_stations_dict["station"] = station
         all_stations_dict["name"] = name
         all_stations.append(all_stations_dict)
    return jsonify(all_stations)

@app.route("/api/v1.0/tobs")
def tobs(): 
    # Creating a link from Python to the database
    session = Session(engine)

    # Finding the last date in the Measurements database
    last_date = session.query(Measurement.date).order_by(Measurement.date.desc()).first()

    # Extracting the date from the result
    last_date_str = last_date.date
    # Converting last_date to a datetime object
    last_date_obj = dt.datetime.strptime(last_date_str, "%Y-%m-%d")
    formatted_date = (last_date_obj - dt.timedelta(days=365)).strftime("%Y-%m-%d")
    
    # Finding the most active station in the database
    most_active_station = session.query(Measurement.station, func.count(Measurement.station)).group_by(Measurement.station).\
        order_by(func.count(Measurement.station).desc()).first()

    """Returning a list of dates and temperature of the most active stations for the last year"""
    # Querying the dates and tempareture of the most active station for the last 12 months
    results = session.query(Measurement.tobs).filter(Measurement.date >= formatted_date).\
    filter(Measurement.station == most_active_station[0]).all()
    session.close()

    #Tuples to list conversion
    active_station = list(np.ravel(results))

    return jsonify(active_station)

@app.route("/api/v1.0/<start>")
def start_date(start):
    # Creating a link from Python to the database
    session = Session(engine)

    """Returning a list of minimum, maximum and average temperatures for a given date"""

    # Querying for min, max and avg temp for all the dates greater than equal to the given date
    results_start = session.query(
    Measurement.date,
    func.min(Measurement.tobs).label('min_temp'),
    func.avg(Measurement.tobs).label('avg_temp'),
    func.max(Measurement.tobs).label('max_temp')
    ).filter(Measurement.date >= start).group_by(Measurement.date).all()
    #results = session.query(Measurement.date, func.min(Measurement.tobs).\
        #func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
        #filter(Measurement.date >= start).all()

    session.close()

# Creating a dictionary from the row data and appending the list

    start_date_info = []
    for date, min_temp, avg_temp, max_temp in results_start:
     temp_info = {}
     temp_info["DATE"] = date
     temp_info["TMIN"] = min_temp
     temp_info["TAVG"] = avg_temp
     temp_info["TMAX"] = max_temp
     start_date_info.append(temp_info)

    return jsonify(start_date_info)


@app.route("/api/v1.0/<start>/<end>")
def start_end_date(start, end):
    # Creating a link from Python to the database
    session = Session(engine)

    """Returning a list of minimum, maximum and average temperature for a given start and end date"""

    #Querying the min, max, avg temp for given dates
    results_end = session.query(
        Measurement.date,
        func.min(Measurement.tobs).label('min_temp'),
        func.avg(Measurement.tobs).label('avg_temp'),
        func.max(Measurement.tobs).label('max_temp')
        ).filter(Measurement.date >= start).filter(Measurement.date <= end).all()

    session.close()

#Creating a dictionary from the row data and appending the information
    end_date_info = []
    for date, min_temp, avg_temp, max_temp in results_end:
     temp_info_end = {}
     temp_info_end["DATE"] = date
     temp_info_end["TMIN"] = min_temp
     temp_info_end["TAVG"] = avg_temp
     temp_info_end["TMAX"] = max_temp
     end_date_info.append(temp_info_end)

    return jsonify(end_date_info)

if __name__ == "__main__":
    app.run(debug=True)