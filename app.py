from flask import Flask, jsonify, request
import numpy as np
import keras
from keras.models import load_model
from sklearn.metrics import mean_absolute_error,median_absolute_error,mean_squared_log_error, r2_score

import flask
app = Flask(__name__)

@app.route("/")
def hello_world():
    return "Welcome to Acea Smart Water Analytics prediction"
	
@app.route("/index")
def index():
	return flask.render_template('index.html')
	
@app.route("/predict",methods=['POST'])
def predict():
	
	result1=''
	result2 = ''
	
	#waterbody type
	waterbody = request.form['waterbody']
	
	try:
		# getting input with name = rainfall in HTML form
		r = request.form.get("rainfall")
		if not(r=='' or r==None):
			rainfall = float(r)
		else:
			rainfall = float("NaN")
		# getting input with name = temp in HTML form
		t = request.form.get("temp")
		if not(t=='' or t==None):
			temp = float(t)
		else:
			temp = float("NaN")
		# getting input with name = volume in HTML form
		v = request.form.get("volume")
		if not(v=='' or v==None):
			volume = float(v)
		else:
			volume = float("NaN")
		# getting input with name = depth in HTML form 
		d = request.form.get("depth")
		if not(d=='' or d==None):
			depth = float(d)
		else:
			depth = float("NaN")
		# getting input with name = hydro in HTML form
		h = request.form.get("hydro")
		if not(h=='' or h==None):
			hydro = float(h)
		else:
			hydro = float("NaN")
		# getting input with name = flow in HTML form
		fl = request.form.get("flow")
		if not(fl=='' or fl==None):
			flow = float(fl)
		else:
			flow = float("NaN")
		# getting input with name = lake_level in HTML form 
		ll = request.form.get("lakelevel")
		if not(ll=='' or ll==None):
			lake_level = float(ll)
		else:
			lake_level = float("NaN")
	except:
		return flask.render_template("predict.html", result1='Enter valid numeric values',result2='')
	
	#store user entered values in the same order as below
	# Mean_Rainfall, Mean_Temp, Volume, Depth, Hydrometry, Flow_Rate,Lake_Level
	to_predict_list = np.array([rainfall,temp,volume,depth,hydro,flow,lake_level])
	
	# use aquifer model if Rainfall, Temperature, Volume and Hydrometry are entered and waterbody entered is aquifer
	if list(np.isnan(to_predict_list)) == [False, False, False, True, False, True, True] and waterbody == 'aquifer' :
		model = load_model('model_aquifer_save/weights.h5', compile=False)
		pred = model.predict(to_predict_list[~np.isnan(to_predict_list)].reshape(1,-1))
		target = 'Predicted Depth to Groundwater:'
	
	# use lake model if Rainfall, Temperature are entered and waterbody entered is lake
	elif list(np.isnan(to_predict_list)) == [False, False, True, True, True, True, True] and waterbody == 'lake':
		model = load_model('model_lakes_save/weights.h5', compile=False)
		pred = model.predict(to_predict_list[~np.isnan(to_predict_list)].reshape(1,-1))
		target = ['Predicted Flow Rate:','Predicted Lake Level:']
	
	# use river model if Rainfall, Temperature are entered and waterbody entered is river
	elif list(np.isnan(to_predict_list)) == [False, False, True, True, True, True, True] and waterbody == 'river':
		model = load_model('model_rivers_save/weights.h5', compile=False)
		pred = model.predict(to_predict_list[~np.isnan(to_predict_list)].reshape(1,-1))
		target = 'Predicted Hydrometry:'
	
	# use spring model if Rainfall, Temperature, Depth are entered and waterbody entered is spring
	elif list(np.isnan(to_predict_list)) == [False, False, True, False, True, True, True] and waterbody == 'spring':
		model = load_model('model_springs_save/weights.h5', compile=False)
		pred = model.predict(to_predict_list[~np.isnan(to_predict_list)].reshape(1,-1))
		target = 'Predicted Flow Rate:'
		
	else:
		return flask.render_template("predict.html", result1='Enter only valid details as per the waterbody',result2='')
	
	# single predictions returned for aquifer,river, spring and two returned for lake
	if len(pred[0])==1:
		return flask.render_template("predict.html", waterbody=waterbody.upper(), target1=target, result1=pred[0][0],target2 = '',result2='')
	else:
		return flask.render_template("predict.html", waterbody=waterbody.upper(), target1=target[0], result1=pred[0][0],target2 = target[1],result2=pred[0][1])
