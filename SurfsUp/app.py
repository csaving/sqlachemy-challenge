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
        f"/api/v1.0/<start><br/>"
        f"/api/v1.0/<start>/<end>"
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


if __name__ == '__main__':
    app.run(debug=True)