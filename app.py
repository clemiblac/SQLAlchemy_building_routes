# -*- coding: utf-8 -*-
"""
Created on Thu Jun  4 15:48:04 2020

@author: clemi
"""
from flask import Flask,jsonify,render_template
import sqlalchemy
from sqlalchemy import create_engine
import pandas as pd
from sqlalchemy.ext.automap import automap_base

#%%
### Database Setup
engine = create_engine("sqlite:///Resources/hawaii.sqlite")
#%%
#reflect an existing database into a new model
Base=automap_base()
#reflect the tables
Base.prepare(engine,reflect=True)
Base.classes.keys()
#%%
### Flask Setup
app = Flask(__name__)
#%%

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/code")
def code():
    return render_template("code.html")

@app.route("/about")
def about():
    return render_template("about.html")


# Flask Routes
### PRECIPITATION APP
@app.route("/api/v1.0/precipitation")
def precipitation():

    #Convert the query results to a dictionary using `date` as the key and `prcp` as the value
    results = pd.read_sql("SELECT date,prcp FROM measurement", engine)
    results.dropna(inplace=True)
    results_dict = dict(zip(results.date, results.prcp))

    #Return the JSON representation of your dictionary.
    results_json=jsonify( results_dict)
    return results_json
 
#%%
### STATIONS APP
@app.route("/api/v1.0/stations")
def stations():
  
    #Return a JSON list of stations from the dataset.
    results = pd.read_sql("SELECT DISTINCT(station) FROM measurement", engine)
    results_json = results['station'].to_json(orient='records')
    return results_json
   
#%%
### TEMPERATURE APP
### Dates and temperature observations for the last year of data
@app.route("/api/v1.0/tobs")
def date_temperature():
   
    #Query the dates and temperature observations of the most active station for the last year of data.
    results = pd.read_sql("SELECT * FROM measurement\
                          WHERE station='USC00519281'\
                          AND date BETWEEN\
                          date('2016-08-23') AND date('2017-08-23')\
                          ORDER BY DATE(date)", engine)

    #Return a JSON list of temperature observations (TOBS) for the previous year.
    results_json = results[['date','tobs']].to_json(orient='records')
    return results_json
            
#%%
### Start date given
@app.route("/api/v1.0/<start>")
def start_date(start):
  
    """Fetch data  for all dates greater than or equat to the start date the path variable is supplied by the use, or a 404 if not"""
    # When given the start only, calculate `TMIN`, `TAVG`, and `TMAX` for all dates greater than and equal to the start date.
    start_text=sqlalchemy.text("SELECT date, min(tobs),avg(tobs),max(tobs) FROM measurement WHERE date >= :name group by date")
    results = pd.read_sql(start_text, engine,params={'name':start})
    for row in results:
        if start<='2017-08-23':
            results_json = results.to_json(orient='records')
            return results_json
        else:
            return jsonify({"error": f" No data for date {start} was found.The last date in this dataset is '2017-08-23'"}),404

#%%
### Start date and end date given
# Return a JSON list of the minimum temperature, the average temperature, and the max temperature for a given start-end range.
@app.route("/api/v1.0/<start>/<end>")
def start_end_date(start,end):
    
    """Fetch data  for all dates greater than or equal to the start date the path variable is supplied by the use, or a 404 if not"""
    start_text=sqlalchemy.text("SELECT date, min(tobs),avg(tobs),max(tobs) FROM measurement WHERE date\
                               >= :name1 AND date <=:name2 group by date")
    # When given the start and the end date, calculate the `TMIN`, `TAVG`, and `TMAX` for dates between the start and end date inclusive.
    results = pd.read_sql(start_text, engine,params={'name1':start,'name2':end})
    for row in results:
        if start>='2010-01-01' and end<='2017-08-23':
            results_json = results.to_json(orient='records')
            return results_json
        else:
            return jsonify({"error": f" Date range must be between '2010-01-01' and '2017-08-23'. There is no data for dates outside\
                            this range."}),404


#%%



if __name__ == '__main__':
    app.run(debug=True)
