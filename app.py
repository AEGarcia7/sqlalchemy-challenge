import numpy as np
import datetime as dt

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

from flask import Flask, jsonify

# Database Setup

engine = create_engine("sqlite:///hawaii.sqlite")
Base = automap_base()
Base.prepare(engine, reflect=True)

# Base.classes.keys()
# Same names as in the first part 

Measurement = Base.classes.measurement
Station = Base.classes.station


# Flask Setup

app = Flask(__name__)



# Flask Routes

@app.route("/")
def welcome():
    """List all available api routes."""
    return (
        f"Available Routes:<br/>"
        f"Precipitation: /api/v1.0/precipitation<br/>"
        f"List of Stations: /api/v1.0/stations<br/>"
        f"Temperature for one year: /api/v1.0/tobs<br/>"
        f"Temperature min, max and average from the start date (in yyyy-mm-dd format): /api/v1.0/yyyy-mm-dd<br/>"
        f"Temperature min, max and average from start to end dates (in yyyy-mm-dd format): /api/v1.0/yyyy-mm-dd/yyyy-mm-dd"
    )
#Dates in order with amount of percipitation per day

@app.route('/api/v1.0/precipitation')
def precipitation():
    session = Session(engine)
    sel = [Measurement.date,Measurement.prcp]
    queryslct = session.query(*sel).all()
    session.close()

    precipitation = []
    for date, prcp in queryslct:
        prcpdict = {}
        prcpdict["Date"] = date
        prcpdict["Precipitation"] = prcp
        precipitation.append(prcpdict)

    return jsonify(precipitation)

#Station names, ID, Elevation, and Latitude & Longitude

@app.route('/api/v1.0/stations')
def stations():
    session = Session(engine)
    sel = [Station.station,Station.name,Station.latitude,Station.longitude,Station.elevation]
    queryslct = session.query(*sel).all()
    session.close()

    stations = []
    for station,name,lat,lon,el in queryslct:
        stationdict = {}
        stationdict["Station"] = station
        stationdict["Name"] = name
        stationdict["Lat"] = lat
        stationdict["Lon"] = lon
        stationdict["Elevation"] = el
        stations.append(stationdict)

    return jsonify(stations)

# Date in order with tobs

@app.route('/api/v1.0/tobs')
def tobs():
    session = Session(engine)
    latest_date = session.query(Measurement.date).order_by(Measurement.date.desc()).first()[0]
    dateagain = dt.datetime.strptime(latest_date, '%Y-%m-%d')
    datediv = dt.date(dateagain.year -1, dateagain.month, dateagain.day)
    sel = [Measurement.date,Measurement.tobs]
    queryslct = session.query(*sel).filter(Measurement.date >= datediv).all()
    session.close()

    tobsall = []
    for date, tobs in queryslct:
        tobsdict = {}
        tobsdict["Date"] = date
        tobsdict["Tobs"] = tobs
        tobsall.append(tobsdict)

    return jsonify(tobsall)

#Temperature min, max and average from start date

@app.route('/api/v1.0/<start>')
def get_t_start(start):
    session = Session(engine)
    measuredata = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
        filter(Measurement.date >= start).all()
    session.close()

    tobsdata = []
    for min,avg,max in measuredata:
        tobsdict = {}
        tobsdict["Min"] = min
        tobsdict["Average"] = avg
        tobsdict["Max"] = max
        tobsdata.append(tobsdict)

    return jsonify(tobsdata)

#Temperature min, max and average from start to end dates

@app.route('/api/v1.0/<start>/<stop>')
def get_t_start_stop(start,stop):
    session = Session(engine)
    measuredata = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
        filter(Measurement.date >= start).filter(Measurement.date <= stop).all()
    session.close()

    tobsall = []
    for min,avg,max in measuredata:
        tobsdict = {}
        tobsdict["Min"] = min
        tobsdict["Average"] = avg
        tobsdict["Max"] = max
        tobsall.append(tobsdict)

    return jsonify(tobsall)

if __name__ == '__main__':
    app.run(debug=True)