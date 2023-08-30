# Import the dependencies.
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm         import Session
from sqlalchemy             import create_engine, func
from flask                  import Flask, jsonify

import datetime as dt
import sqlalchemy

engine = create_engine('sqlite:///Resources/hawaii.sqlite')
#################################################
# Database Setup
#################################################


# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(engine, reflect=True)

# Save references to each table
Measurement = Base.classes.measurement
Station     = Base.classes.station

# Create our session (link) from Python to the DB
session = Session(engine)

#################################################
# Flask Setup
#################################################
app = Flask(__name__)



#################################################
# Flask Routes
#################################################
@app.route('/')
def homepage():
    return ("All routes <br/>"
            "/api/v1.0/precipitation : dates and precipitation route <br/>"
            "/api/v1.0/Stations : Stations from the data <br/>"
            "/api/v1.0/tobs : list dates and tobs from an year for the last data point (2017-08-23) <br/>"
            "/api/v1.0/startdate : show min, avg, and max temperature for a specified start date <br/>"
            "/api/v1.0/startdate/enddate : show min, avg, and max temperature for a specified start and end date <br/><br/>")

@app.route("/api/v1.0/precipitation")
def precipitation():
    
    session = Session(engine)
    
    year_ago = dt.date(2017, 8, 23) - dt.timedelta(days = 365)
    prcp_data = session.query(Measurement.date, Measurement.prcp).filter(Measurement.date >= year_ago).all()
    dict_prcp = dict(prcp_data)
    
    session.close()

    return jsonify(dict_prcp)

@app.route("/api/v1.0/stations")
def stations():
    session  = Session(engine)
    
    stations_tuple = session.query(Station.station).all()
    session.close()
    
    stations_list = list(np.ravel(stations_tuple))

    return jsonify(stations_list)


@app.route("/api/v1.0/tobs")
def tobs():
    session = Session(engine)
    
    latest_date = dt.date(2017,8, 23)
    
    year_ago = latest_date - dt.timedelta(days=365)
    year_ago = (year_ago.strftime("%Y-%m-%d"))
    
    last_12 = session.query(Measurement.date, Measurement.tobs).filter_by(station = "USC00519281").\
    filter(Measurement.date >= year_ago).all()
    
    session.close()
    
    last_12_list = []
    for date, tobs in last_12:
        tobs_dict       = {}
        tobs_dict[date] = tobs
        last_12_list.append(tobs_dict)
    
    return jsonify(last_12_list)



@app.route("/api/v1.0/<start>")
def start_date(start):
    
    session = Session(engine)
    
    temperature = session.query(Measurement.date, func.min(Measurement.tobs), func.avg(Measurement.tobs),
                                func.max(Measurement.tobs)).filter(Measurement.date >= start).group_by(Measurement.date).all()
    
    session.close()
    
    temp_list = []
    for i in temperature:
        temp_dict = {}
        
        temp_dict['Date'] = i[0]
        temp_dict['TMIN'] = i[1]
        temp_dict['TAVG'] = round(i[2], 1)
        temp_dict['TMAX'] = i[3]
        
        temp_list.append(temp_dict)
    
    return jsonify(temp_list)
        
@app.route("/api/v1.0/<start>/<end>")
def start_end_date(start, end):
    session = Session(engine)
    
    temperature = session.query(Measurement.date, func.min(Measurement.tobs), func.avg(Measurement.tobs),
                                func.max(Measurement.tobs)).filter(Measurement.date >= start).filter(Measurement.date <=
                                                                                                     end).group_by(Measurement.date).all()
    session.close()
    
    temp_list = []
    for i in temperature:
        temp_dict = {}
    
        temp_dict['Date'] = i[0]
        temp_dict['TMIN'] = i[1]
        temp_dict['TAVG'] = round(i[2], 1)
        temp_dict['TMAX'] = i[3]
        
        temp_list.append(temp_dict)
     
    return jsonify(temp_list)


if __name__ == '__main__':
    app.run(debug=True)