# Import the dependencies.
import numpy as np
import datetime as dt

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

from flask import Flask, jsonify


#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(autoload_with=engine)

# Save references to each table
m = Base.classes.measurement
s = Base.classes.station


#################################################
# Flask Setup
#################################################
app = Flask(__name__)


#################################################
# Flask Routes
#################################################
@app.route("/")
def welcome():
    """List of all available api routes."""
    return (
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/&lt;start&gt;<br/>"
        f"/api/v1.0/&lt;start&gt;/&lt;end&gt;<br/>"
    )


@app.route("/api/v1.0/precipitation")
def precipitation():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    """Return precipitation data for most recent 12 months"""
    
    # Find the most recent date in the data set.
    recent_date_str = session.query(m.date).order_by(m.date.desc()).limit(1).scalar()
    
    # Calculate the date one year from the last date in data set.
    recent_date = dt.date.fromisoformat(recent_date_str)
    year_ago = recent_date - dt.timedelta(days=365)

    # Query preciptitation data for last 12 months
    results = session.query(m.date, m.prcp).\
                filter(m.date > year_ago).\
                order_by(m.date).\
                all()

    session.close()

    # Create a dictionary from the row data and append to a list of precipitation data
    prcp_list = []
    for date, prcp in results:
        prcp_dict = {}
        prcp_dict[date] = prcp
        prcp_list.append(prcp_dict)

    return jsonify(prcp_list)


@app.route("/api/v1.0/stations")
def stations():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    """Return list of stations"""

    # Query preciptitation data for last 12 months
    results = session.query(s.station, s.name).all()

    session.close()

    # Create a dictionary from the row data and append to a list of stations
    station_list = []
    for station, name in results:
        station_dict = {}
        station_dict[station] = name
        station_list.append(station_dict)

    return jsonify(station_list)


@app.route("/api/v1.0/tobs")
def tobs():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    """Return temperature data for most active station for most recent 12 months"""
    
    # Find the most recent date in the data set.
    recent_date_str = session.query(m.date).order_by(m.date.desc()).limit(1).scalar()
    
    # Calculate the date one year from the last date in data set.
    recent_date = dt.date.fromisoformat(recent_date_str)
    year_ago = recent_date - dt.timedelta(days=365)

    # Find most active station id
    most_active = session.query(m.station).\
                    group_by(m.station).\
                    order_by(func.count(m.station).desc()).\
                    first()[0]
    
    # Using the most active station id
    # Query the last 12 months of temperature observation data for this station
    results = session.query(m.date, m.tobs).\
                    filter(m.station == most_active).\
                    filter(m.date > year_ago).\
                    all()

    session.close()

    # Create a dictionary from the row data and append to a list of temperature data
    tobs_list = []
    for date, tobs in results:
        tobs_dict = {}
        tobs_dict[date] = tobs
        tobs_list.append(tobs_dict)

    return jsonify(tobs_list)


@app.route("/api/v1.0/<start>")
def start(start):
    # Create our session (link) from Python to the DB
    session = Session(engine)

    """Return temperature stats from given start date"""

    # Query the temperature stats filtered by start date
    results = session.query(func.min(m.tobs).label("tmin"), func.max(m.tobs).label("tmax"), func.avg(m.tobs).label("tavg")).\
                        filter(m.date >= start).\
                        all()
    
    session.close()

    # Create a dictionary from the row data and append to a list of temperature data
    tobs_list = []
    for tmin, tmax, tavg in results:
        tobs_dict = {}
        tobs_dict['tmin'] = tmin
        tobs_dict['tmax'] = tmax
        tobs_dict['tavg'] = tavg
        tobs_list.append(tobs_dict)

    return jsonify(tobs_list)


@app.route("/api/v1.0/<start>/<end>")
def startend(start, end):
    # Create our session (link) from Python to the DB
    session = Session(engine)

    """Return temperature stats for data between start and end date inclusive"""

    # Query the temperature stats filtered by start and end dates
    results = session.query(func.min(m.tobs).label("tmin"), func.max(m.tobs).label("tmax"), func.avg(m.tobs).label("tavg")).\
                        filter(m.date >= start, m.date <= end).\
                        all()
    session.close()

    # Create a dictionary from the row data and append to a list of temperature data
    tobs_list = []
    for tmin, tmax, tavg in results:
        tobs_dict = {}
        tobs_dict['tmin'] = tmin
        tobs_dict['tmax'] = tmax
        tobs_dict['tavg'] = tavg
        tobs_list.append(tobs_dict)

    return jsonify(tobs_list)


if __name__ == '__main__':
    app.run(debug=True)