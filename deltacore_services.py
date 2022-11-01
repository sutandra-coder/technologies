from flask import Flask, request, jsonify, json
from flask_api import status
from jinja2._compat import izip
from datetime import datetime,timedelta,date
import pymysql
from flask_cors import CORS, cross_origin
from flask import Blueprint
from flask_restplus import Api, Resource, fields
from database_connections import connect_meeprotect
import requests
import calendar
import json

app = Flask(__name__)
cors = CORS(app)

deltacore_services = Blueprint('deltacore_services_api', __name__)

api = Api(deltacore_services, version='1.0', title='DeltaCore API',
    	description='DeltaCore API')
name_space = api.namespace('DeltaCoreAPI', description='DeltaCore')

UPLOAD_FOLDER = '/tmp'

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

BASE_URL = "http://ec2-18-191-221-235.us-east-2.compute.amazonaws.com/"

#--------------------------------------------------------------------#
signup = api.model('signup', {
	"username": fields.String(),
    "emailid": fields.String(),
    "mobile": fields.String(),
    "imei": fields.String(),
    "password": fields.String(),
    "dob": fields.String(),
    "aniversary": fields.String(),
    "retid": fields.String(),
    "activecode": fields.String(),
    "w_devmodel": fields.String(),
    "w_invamt": fields.Integer(),
    "w_invno": fields.Integer()
    })

signupV2 = api.model('signupV2', {
	"username": fields.String(),
    "emailid": fields.String(),
    "mobile": fields.String(),
    "imei": fields.String(),
    "password": fields.String(),
    "dob": fields.String(),
    "aniversary": fields.String(),
    "retid": fields.String(),
    "w_devmodel": fields.String(),
    "w_invamt": fields.Integer(),
    "w_invno": fields.Integer()
    })

userprofile = api.model('userprofile', {
	"userid": fields.Integer(),
	"username": fields.String(),
    "emailid": fields.String(),
    "dob": fields.String(),
    "aniversary": fields.String(),
    "imei": fields.String(),
    "retid": fields.String()
    })

signin = api.model('signin', {
	"mobile": fields.String(),
    "imei": fields.String(),
    "password": fields.String()
    })

resetpassword = api.model('resetpassword', {
	"userid": fields.Integer(),
    "password": fields.String()
    })

devicetrack = api.model('devicetrack', {
	"lat": fields.String(),
    "long": fields.String(),
    "emailid": fields.String(),
    "primary_no": fields.String()
    })

panicmode = api.model('panicmode', {
	"lat": fields.String(),
    "long": fields.String(),
    "primary_no": fields.String(),
    "secondary_no": fields.String()
    })

login_track = api.model('login_track', {
	"username": fields.String(),
    "password": fields.String(),
    "imei": fields.String(),
    "ip_address": fields.String()
    })

addProtection = api.model('addProtection', {
	"emailid": fields.String(),
    "activecode": fields.String(),
    "w_invamt": fields.Integer(),
    "w_invno": fields.String()
    })

deviceDtls = api.model('deviceDtls', {
	"userid": fields.Integer(),
    "device_type": fields.String(),
    "device_token": fields.String()
    })

unlockfeatures = api.model('unlockfeatures', {
	"activecode": fields.String(),
    "u_mobile": fields.String()
    })

addimage = api.model('unlockfeatures', {
	"image_url": fields.String(),
    "u_mobile": fields.String()
    })

retLogin = api.model('unlockfeatures', {
	"distributorPhno": fields.String(),
    "username": fields.String(),
    "password": fields.String(),
    "ret_code": fields.String(),
    "ret_name": fields.String()
    })

intruderselfie = api.model('intruderselfie', {
	"i_image": fields.String(),
    "u_mobile": fields.String()
    })

#--------------------------------------------------------------------#
@name_space.route("/SignUp")
class SignUp(Resource):
	@api.expect(signup)
	def post(self):
		connection = connect_meeprotect()
		cursor = connection.cursor()
		details = request.get_json()
		today = date.today()

		username = details.get('username')
		emailid = details.get('emailid')
		mobile = details.get('mobile')
		imei = details.get('imei')
		password = details.get('password')
		dob = details.get('dob')
		aniversary = details.get('aniversary')
		retid = details.get('retid')
		activecode = details.get('activecode')
		w_devmodel = details.get('w_devmodel')
		w_invamt = details.get('w_invamt')
		w_invno = details.get('w_invno')

		moblen = len(mobile)
		if moblen>10:
			msg = "Enter Valid Phone Number!!!"

		cursor.execute("""SELECT au_username FROM tbl_channel_users where 
	    	au_code=%s""",(retid))
		retailerDtls = cursor.fetchone()

		if retailerDtls:
			cursor.execute("""SELECT u_userid FROM tbl_user WHERE 
	    		u_mobile=%s""",(mobile))
			userContactDtls = cursor.fetchone()

			if userContactDtls == None:
				cursor.execute("""SELECT u_userid FROM tbl_user WHERE 
		    		u_email_id=%s""",(emailid))
				userEmailIdDtls = cursor.fetchone()

				if userEmailIdDtls == None:
					cursor.execute("""SELECT act_pack_code FROM `tbl_activations` 
						WHERE `act_code` =%s and `is_used`=0""",(activecode))
					activationDtls = cursor.fetchone()
					if activationDtls:
						if activationDtls['act_pack_code'] == 'YRLY':
							u_pack_code = 'YRLY'
							validity_start = date.today()
							validity_end = validity_start.replace(year=validity_start.year + 1)
							
						else:
							u_pack_code = 'LFTM'
							validity_start = date.today()
							validity_end = '0000-00-00'

						tbl_userquery = ("""INSERT INTO tbl_user(u_name,
							u_email_id,u_userid,u_pass,u_date_of_birth,
							u_aniversary,u_ret_code,u_mobile,u_date,u_imei,
							u_activ_code,validity_start,validity_end,u_pid,
							u_pack_code,u_pack_price,u_ret_parent) VALUES (%s,
							%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)""")
						tbl_userdata = cursor.execute(tbl_userquery,(username,
							emailid,mobile,password,dob,aniversary,retid,
							mobile,today,imei,activecode,validity_start,
							validity_end,'',u_pack_code,'',''))

						if tbl_userdata:
							updateActivation = ("""UPDATE `tbl_activations` 
								SET `is_used`=%s where `act_code` = %s""")
							cursor.execute(updateActivation,(1,activecode))

							device_locquery = ("""INSERT INTO tbl_device_loc(dev_user,
								dev_imei,dev_lat,dev_long,is_on) VALUES (%s,%s,%s,%s,
								%s)""")
							device_locdata = cursor.execute(device_locquery,(emailid,
								imei,0,0,0))

							anti_theftquery = ("""INSERT INTO tbl_anti_theft(ant_user,
								ant_wipe,ant_ring) VALUES (%s,%s,%s)""")
							anti_theftdata = cursor.execute(anti_theftquery,(emailid,
								0,0))

							tbl_ringquery = ("""INSERT INTO tbl_ring(rin_user,
								rin_ring) VALUES (%s,%s)""")
							tbl_ringdata = cursor.execute(tbl_ringquery,(emailid,
								0))
							cursor.execute("""SELECT `u_id`,`u_name`,`u_email_id`,
								`u_userid`,`u_pass`,`image_url`,`u_date_of_birth`,
								`u_aniversary`,`u_imei`,`u_date`,`u_mobile`,`u_pack_code`,
								`u_activ_code`,`validity_start`,`validity_end` FROM 
								tbl_user WHERE u_email_id=%s""",(emailid))
							reguserDtls = cursor.fetchone()

							if reguserDtls:
								reguserDtls['u_date'] = reguserDtls['u_date'].isoformat()

								if reguserDtls['u_date_of_birth']=='0000-00-00':
									reguserDtls['u_date_of_birth'] = '0000-00-00'
								else:
									reguserDtls['u_date_of_birth'] = reguserDtls['u_date_of_birth'].isoformat()
								
								if reguserDtls['u_aniversary']=='0000-00-00':
									reguserDtls['u_aniversary'] = '0000-00-00'
								else:
									reguserDtls['u_aniversary'] = reguserDtls['u_aniversary'].isoformat()
								
								if reguserDtls['validity_start']=='0000-00-00':
									reguserDtls['validity_start'] = '0000-00-00'
								else:
									reguserDtls['validity_start'] = reguserDtls['validity_start'].isoformat()
								
								if reguserDtls['validity_end']=='0000-00-00':
									reguserDtls['validity_end'] = '0000-00-00'
								else:
									reguserDtls['validity_end'] = reguserDtls['validity_end'].isoformat()
								
							msg = "success"
						else:
							msg =""
							reguserDtls = {
			    					"activecode" :""
			    				}
				else:
					msg = "Email Id Already Exists"
					reguserDtls = {
		    					"activecode" :""
		    				}
			else:
				msg = "Phone Number Already Exists"
				reguserDtls = {
	    					"activecode" :""
	    				}
		else:
			msg = "Retailer is not activated, Licence cannot be activated"
			reguserDtls = {
	    					"activecode" :""
	    				}

		connection.commit()
		cursor.close()
		return ({"attributes": {"status_desc": "User Registration Details",
	                                "status": "success",
	                                "msg": msg
	                            },
	            "responseList": reguserDtls}), status.HTTP_200_OK

#------------------------------------------------------------------#
@name_space.route("/SignUpV2")
class SignUpV2(Resource):
	@api.expect(signupV2)
	def post(self):
		connection = connect_meeprotect()
		cursor = connection.cursor()
		details = request.get_json()
		today = date.today()

		username = details.get('username')
		emailid = details.get('emailid')
		mobile = details.get('mobile')
		imei = details.get('imei')
		password = details.get('password')
		dob = details.get('dob')
		aniversary = details.get('aniversary')
		retid = details.get('retid')
		w_devmodel = details.get('w_devmodel')
		w_invamt = details.get('w_invamt')
		w_invno = details.get('w_invno')

		moblen = len(mobile)
		if moblen>10:
			msg = "Enter Valid Phone Number!!!"

		cursor.execute("""SELECT au_username FROM tbl_channel_users where 
	    	au_code=%s""",(retid))
		retailerDtls = cursor.fetchone()

		if retailerDtls:
			cursor.execute("""SELECT u_userid FROM tbl_user WHERE 
	    		u_mobile=%s""",(mobile))
			userContactDtls = cursor.fetchone()

			if userContactDtls == None:
				cursor.execute("""SELECT u_userid FROM tbl_user WHERE 
		    		u_email_id=%s""",(emailid))
				userEmailIdDtls = cursor.fetchone()

				if userEmailIdDtls == None:
					tbl_userquery = ("""INSERT INTO tbl_user(u_name,u_email_id,
						u_userid,u_pass,u_date_of_birth,u_aniversary,u_ret_code,
						u_mobile,u_date,u_imei,u_activ_code,u_pid,u_pack_code,
						u_pack_price,u_ret_parent) VALUES (%s,%s,%s,%s,%s,%s,%s,
						%s,%s,%s,%s,%s,%s,%s,%s)""")
					tbl_userdata = cursor.execute(tbl_userquery,(username,emailid,
						mobile,password,dob,aniversary,retid,mobile,today,imei,
						'','','','',''))
					if tbl_userdata:
						device_locquery = ("""INSERT INTO tbl_device_loc(dev_user,
							dev_imei,dev_lat,dev_long,is_on) VALUES (%s,%s,%s,%s,
							%s)""")
						device_locdata = cursor.execute(device_locquery,(emailid,
							imei,0,0,0))

						anti_theftquery = ("""INSERT INTO tbl_anti_theft(ant_user,
							ant_wipe,ant_ring) VALUES (%s,%s,%s)""")
						anti_theftdata = cursor.execute(anti_theftquery,(emailid,
							0,0))

						tbl_ringquery = ("""INSERT INTO tbl_ring(rin_user,
							rin_ring) VALUES (%s,%s)""")
						tbl_ringdata = cursor.execute(tbl_ringquery,(emailid,
							0))
						cursor.execute("""SELECT `u_id`,`u_name`,`u_email_id`,
							`u_userid`,`u_pass`,`image_url`,`u_date_of_birth`,
							`u_aniversary`,`u_imei`,`u_date`,`u_mobile`,`u_pack_code`,
							`u_activ_code`,`validity_start`,`validity_end` FROM 
							tbl_user WHERE u_email_id=%s""",(emailid))
						reguserDtls = cursor.fetchone()

						if reguserDtls:
							reguserDtls['u_date'] = reguserDtls['u_date'].isoformat()

							if reguserDtls['u_date_of_birth']=='0000-00-00':
								reguserDtls['u_date_of_birth'] = '0000-00-00'
							else:
								reguserDtls['u_date_of_birth'] = reguserDtls['u_date_of_birth'].isoformat()
							
							if reguserDtls['u_aniversary']=='0000-00-00':
								reguserDtls['u_aniversary'] = '0000-00-00'
							else:
								reguserDtls['u_aniversary'] = reguserDtls['u_aniversary'].isoformat()
							
							if reguserDtls['validity_start']=='0000-00-00':
								reguserDtls['validity_start'] = '0000-00-00'
							else:
								reguserDtls['validity_start'] = reguserDtls['validity_start'].isoformat()
							
							if reguserDtls['validity_end']=='0000-00-00':
								reguserDtls['validity_end'] = '0000-00-00'
							else:
								reguserDtls['validity_end'] = reguserDtls['validity_end'].isoformat()
							
						msg = "success"
					else:
						msg =""
						reguserDtls = {
		    					"activecode" :""
		    				}
				else:
					msg = "Email Id Already Exists"
					reguserDtls = {
		    					"activecode" :""
		    				}
			else:
				msg = "Phone Number Already Exists"
				reguserDtls = {
	    					"activecode" :""
	    				}
		else:
			msg = "Retailer is not activated, Licence cannot be activated"
			reguserDtls = {
	    					"activecode" :""
	    				}

		connection.commit()
		cursor.close()
		return ({"attributes": {"status_desc": "User Registration Details",
	                                "status": "success",
	                                "msg": msg
	                            },
	            "responseList": reguserDtls}), status.HTTP_200_OK

#------------------------------------------------------------------#
@name_space.route("/SignIn")
class SignIn(Resource):
	@api.expect(signin)
	def post(self):
		connection = connect_meeprotect()
		cursor = connection.cursor()
		details = request.get_json()
		
		mobile = details.get('mobile')
		password = details.get('password')
		imei = details.get('imei')

		cursor.execute("""SELECT `u_id`,`u_name`,`u_email_id`,
			`u_userid`,`u_pass`,`image_url`,`u_date_of_birth`,
			`u_aniversary`,`u_imei`,`u_date`,`u_mobile`,`u_pack_code`,
			`u_activ_code`,`validity_start`,`validity_end` FROM 
			tbl_user WHERE u_mobile=%s""",(mobile))
		reguserDtls = cursor.fetchone()

		if reguserDtls:
			if reguserDtls['u_pass'] == password and reguserDtls['u_imei'] == imei:
				if reguserDtls['u_email_id'] == reguserDtls['u_mobile']:
					msg = "Login Successfull"
					reguserDtls['flag'] = "0"
				else:
					msg = "Login Successfull"
					reguserDtls['flag'] = "1"
					
				reguserDtls['u_date'] = reguserDtls['u_date'].isoformat()

				if reguserDtls['u_date_of_birth']=='0000-00-00':
					reguserDtls['u_date_of_birth'] = '0000-00-00'
				else:
					reguserDtls['u_date_of_birth'] = reguserDtls['u_date_of_birth'].isoformat()
				
				if reguserDtls['u_aniversary']=='0000-00-00':
					reguserDtls['u_aniversary'] = '0000-00-00'
				else:
					reguserDtls['u_aniversary'] = reguserDtls['u_aniversary'].isoformat()
				
				if reguserDtls['validity_start']=='0000-00-00':
					reguserDtls['validity_start'] = '0000-00-00'
				else:
					reguserDtls['validity_start'] = reguserDtls['validity_start'].isoformat()
				
				if reguserDtls['validity_end']=='0000-00-00':
					reguserDtls['validity_end'] = '0000-00-00'
				else:
					reguserDtls['validity_end'] = reguserDtls['validity_end'].isoformat()
			
			elif reguserDtls['u_imei'] != imei:
				msg = "Oops!!! Someone is already using"
				reguserDtls = {}

			elif reguserDtls['u_pass'] != password and reguserDtls['u_imei'] == imei:
				msg = "Incorrect Password!!!"
				reguserDtls = {}
		else:
			msg = "Incorrect Phone No!!!"
			reguserDtls = {}

		connection.commit()
		cursor.close()
		return ({"attributes": {"status_desc": "User SignIn Details",
	                                "status": "success",
	                                "msg": msg
	                            },
	            "responseList": reguserDtls}), status.HTTP_200_OK

#------------------------------------------------------------------#
@name_space.route("/DeviceTracking")
class DeviceTracking(Resource):
	@api.expect(devicetrack)
	def post(self):
		connection = connect_meeprotect()
		cursor = connection.cursor()
		details = request.get_json()
		
		lats = details.get('lat')
		longitude = details.get('long')
		emailid = details.get('emailid')
		primary_no = details.get('primary_no')

		location="https://www.google.es/maps/place/{},{}".format(lats,longitude)
		if primary_no != "0":
			device_trackquery = ("""INSERT INTO `tbl_device_track`(dev_user,
				`u_phoneno`,dev_lat,dev_long,is_on) VALUES (%s,%s,%s,%s,%s)""")
			device_trackdata = cursor.execute(device_trackquery,(emailid,
				primary_no,lats,longitude,1))

	 		#------------------------mail-service------------------#
			URL = BASE_URL + "meprotect_mail/CommunicationAPI/mailForDeviceTrack"

			headers = {'Content-type':'application/json', 'Accept':'application/json'}

			payload = {"toMail":emailid,
						"location":location
					}
				
			mailResponse = requests.post(URL,data=json.dumps(payload), headers=headers).json()
			# print(mailResponse)
	        #------------------------mail-service------------------#
	        
			#----------------------------sms-----------------------#
			# url = "http://cloud.smsindiahub.in/vendorsms/pushsms.aspx?"
			# user = 'creamsonintelli'
			# password = 'denver@1234'
			# msisdn = primary_no
			# sid = 'CRMLTD'
			# msg = 'Dear User, Your device location is '+location+'. Thank you for choosing Meprotect.'
			# fl = '0'
			# gwid = '2'
			# payload ="user={}&password={}&msisdn={}&sid={}&msg={}&fl={}&gwid={}".format(user,password,
			# 	msisdn,sid,msg,fl,gwid)
			# postUrl = url+payload
			# # print(msg)
			# response = requests.request("POST", postUrl)

			# sms_response = json.loads(response.text)['ErrorMessage']
			# # print(sms_response)
			# res = {"status":sms_response}
			# if res['status'] == 'Success':
			# 	sent = 'Y'
			# else:
			# 	sent = 'N'
			#----------------------------sms-----------------------#
			msg = "Data Inserted!!!"
		else:
  			updatedeviceTrack = ("""UPDATE `tbl_device_loc` SET `dev_lat`=%s,
  				dev_long =%s,is_on =%s where `dev_user` = %s""")
  			cursor.execute(updatedeviceTrack,(lats,longitude,1,emailid))

  			msg = "Data Updated!!!"

		connection.commit()
		cursor.close()
		return ({"attributes": {"status_desc": "Device Tracking Details",
                                "status": "success",
	                            "msg": msg    
	                            },
	            "responseList": details}), status.HTTP_200_OK

#-----------------------------------------------------------------#
@name_space.route("/PanicMode")
class PanicMode(Resource):
	@api.expect(panicmode)
	def post(self):
		connection = connect_meeprotect()
		cursor = connection.cursor()
		details = request.get_json()
				
		lats = details.get('lat')
		longitude = details.get('long')
		primary_no = details.get('primary_no')
		secondary_no = details.get('secondary_no')
		
		location="https://www.google.es/maps/place/"+ format(lats)+","+format(longitude);
		if secondary_no == "0":
			panicquery = ("""INSERT INTO `tbl_panic`(`u_phoneno`,`dev_lat`,
				`dev_long`) VALUES (%s,%s,%s)""")
			panicdata = cursor.execute(panicquery,(primary_no,lats,longitude))

			msg = "Data Inserted"
			
			cursor.execute("""SELECT `u_name`,`u_email_id` FROM tbl_user WHERE 
				u_mobile=%s""",(primary_no))
			userEmail = cursor.fetchone()

			if userEmail:	

				emailid = userEmail['u_email_id']
				#------------------------mail-service------------------#
				URL = BASE_URL + "meprotect_mail/CommunicationAPI/mailForPanic"

				headers = {'Content-type':'application/json', 'Accept':'application/json'}

				payload = {"toMail":emailid,
							"location":location
						}

				mailResponse = requests.post(URL,data=json.dumps(payload), headers=headers).json()
				# print(mailResponse)
		        #------------------------mail-service------------------#

		        #----------------------------sms-----------------------#
				url = "http://cloud.smsindiahub.in/vendorsms/pushsms.aspx?"
				user = 'creamsonintelli'
				password = 'denver@1234'
				msisdn = primary_no
				sid = 'CRMLTD'
				msg = 'Dear '+userEmail['u_name']+', I am in danger.Please help.My location is '+location+'. Thank you for choosing Meprotect.'
				fl = '0'
				gwid = '2'
				payload ="user={}&password={}&msisdn={}&sid={}&msg={}&fl={}&gwid={}".format(user,password,
					msisdn,sid,msg,fl,gwid)
				postUrl = url+payload
				# print(msg)
				response = requests.request("POST", postUrl)

				sms_response = json.loads(response.text)['ErrorMessage']
				# print(sms_response)
				res = {"status":sms_response}
				if res['status'] == 'Success':
					sent = 'Y'
				else:
					sent = 'N'
				#----------------------------sms-----------------------#

			else:
		        #----------------------------sms-----------------------#
				url = "http://cloud.smsindiahub.in/vendorsms/pushsms.aspx?"
				user = 'creamsonintelli'
				password = 'denver@1234'
				msisdn = primary_no
				sid = 'CRMLTD'
				msg = 'Dear '+'User'+', I am in danger.Please help.My location is '+location+'. Thank you for choosing Meprotect.'
				fl = '0'
				gwid = '2'
				payload ="user={}&password={}&msisdn={}&sid={}&msg={}&fl={}&gwid={}".format(user,password,
					msisdn,sid,msg,fl,gwid)
				postUrl = url+payload
				# print(msg)
				response = requests.request("POST", postUrl)

				sms_response = json.loads(response.text)['ErrorMessage']
				# print(sms_response)
				res = {"status":sms_response}
				if res['status'] == 'Success':
					sent = 'Y'
				else:
					sent = 'N'
				#----------------------------sms-----------------------#
		else:
			mobileno = [primary_no,secondary_no]
			
			for i in range(len(mobileno)):
				panicquery = ("""INSERT INTO `tbl_panic`(`u_phoneno`,`dev_lat`,
					`dev_long`) VALUES (%s,%s,%s)""")
				panicdata = cursor.execute(panicquery,(mobileno[i],lats,longitude))

				cursor.execute("""SELECT `u_name`,`u_email_id` FROM tbl_user 
					WHERE u_mobile=%s""",(mobileno[i]))
				userEmail = cursor.fetchone()

				if userEmail:
					emailid = userEmail['u_email_id']
					#------------------------mail-service------------------#
					URL = BASE_URL + "meprotect_mail/CommunicationAPI/mailForPanic"

					headers = {'Content-type':'application/json', 'Accept':'application/json'}

					payload = {"toMail":emailid,
								"location":location
							}

					mailResponse = requests.post(URL,data=json.dumps(payload), headers=headers).json()
					# print(mailResponse)
					#------------------------mail-service------------------#

					#----------------------------sms-----------------------#
					url = "http://cloud.smsindiahub.in/vendorsms/pushsms.aspx?"
					user = 'creamsonintelli'
					password = 'denver@1234'
					msisdn = mobileno[i]
					sid = 'CRMLTD'
					msg = 'Dear '+userEmail['u_name']+', I am in danger.Please help.My location is '+location+'. Thank you for choosing Meprotect.'
					fl = '0'
					gwid = '2'
					payload ="user={}&password={}&msisdn={}&sid={}&msg={}&fl={}&gwid={}".format(user,password,
						msisdn,sid,msg,fl,gwid)
					postUrl = url+payload
					# print(msg)
					response = requests.request("POST", postUrl)

					sms_response = json.loads(response.text)['ErrorMessage']
					# print(sms_response)
					res = {"status":sms_response}
					if res['status'] == 'Success':
						sent = 'Y'
					else:
						sent = 'N'
				#----------------------------sms-----------------------#
				else:

					#----------------------------sms-----------------------#
					url = "http://cloud.smsindiahub.in/vendorsms/pushsms.aspx?"
					user = 'creamsonintelli'
					password = 'denver@1234'
					msisdn = mobileno[i]
					sid = 'CRMLTD'
					msg = 'Dear '+'User'+', I am in danger.Please help.My location is '+location+'. Thank you for choosing Meprotect.'
					fl = '0'
					gwid = '2'
					payload ="user={}&password={}&msisdn={}&sid={}&msg={}&fl={}&gwid={}".format(user,password,
						msisdn,sid,msg,fl,gwid)
					postUrl = url+payload
					# print(msg)
					response = requests.request("POST", postUrl)

					sms_response = json.loads(response.text)['ErrorMessage']
					# print(sms_response)
					res = {"status":sms_response}
					if res['status'] == 'Success':
						sent = 'Y'
					else:
						sent = 'N'
				#----------------------------sms-----------------------#
			msg = "Data Inserted"

		connection.commit()
		cursor.close()
		return ({"attributes": {"status_desc": "Panic Mode Details",
	                                "status": "success",
	                                "msg": msg
	                            },
	            "responseList": details}), status.HTTP_200_OK

#----------------------------------------------------------------------#
@name_space.route("/UserAccessTracking")
class UserAccessTracking(Resource):
	@api.expect(login_track)
	def post(self):
		connection = connect_meeprotect()
		cursor = connection.cursor()
		details = request.get_json()
		today = date.today()

		username = details.get('username')
		password = details.get('password')
		imei = details.get('imei')
		ip_address = details.get('ip_address')
		
		
		cursor.execute("""SELECT `u_id`,`u_userid`,`u_pass`,u_imei FROM 
			`tbl_user` WHERE u_mobile=%s""",(username))
		credentialDtls = cursor.fetchone()
		
		if credentialDtls:
			if credentialDtls['u_userid'] == username and credentialDtls['u_pass'] == password and credentialDtls['u_imei'] == imei:
				accessquery = ("""INSERT INTO `access_log_table`(`User_ID`,`User_imei`, 
					`User_Name`,`Password`,`Status`,`Application_Name`,`IP Address`) 
					VALUES (%s,%s,%s,%s,%s,%s,%s)""")
				accessdata = cursor.execute(accessquery,(credentialDtls['u_id'],imei,
					username,password,'Success','Delta Core',''))
				msg = "Successfully Accessed"

			elif credentialDtls['u_userid'] == username and credentialDtls['u_pass'] == password and credentialDtls['u_imei'] != imei:
				accessquery = ("""INSERT INTO `access_log_table`(`User_ID`,`User_imei`, 
					`User_Name`,`Password`,`Status`,`Application_Name`,`IP Address`) 
					VALUES (%s,%s,%s,%s,%s,%s,%s)""")
				accessdata = cursor.execute(accessquery,(credentialDtls['u_id'],imei,
					username,password,'Mismatch Imei','Delta Core',''))
				msg = "Mismatch Imei"
			
			elif credentialDtls['u_userid'] == username and credentialDtls['u_pass'] != password and credentialDtls['u_imei'] == imei:
				accessquery = ("""INSERT INTO `access_log_table`(`User_ID`,`User_imei`, 
					`User_Name`,`Password`,`Status`,`Application_Name`,`IP Address`) 
					VALUES (%s,%s,%s,%s,%s,%s,%s)""")
				accessdata = cursor.execute(accessquery,(credentialDtls['u_id'],imei,
					username,password,'Incorrect Password','Delta Core',''))
				msg = "Incorrect Password"	
			
		else:
			accessquery = ("""INSERT INTO `access_log_table`(`User_ID`,`User_imei`, 
				`User_Name`,`Password`,`Status`,`Application_Name`,`IP Address`) 
				VALUES (%s,%s,%s,%s,%s,%s,%s)""")
			accessdata = cursor.execute(accessquery,(0,imei,username,password,
				'Failure','Delta Core',''))
			msg = "Incorrect Username"

		connection.commit()
		cursor.close()
		return ({"attributes": {"status_desc": "Access Log Details",
                                "status": "success",
                                "msg": msg
	                            },
	            "responseList": details}), status.HTTP_200_OK

#-----------------------------------------------------------------------------#

@name_space.route("/ProtectionDetailsByEmailId/<string:emailid>")
class ProtectionDetailsByEmailId(Resource):
    def get(self,emailid):
        connection = connect_meeprotect()
        cursor = connection.cursor()

        cursor.execute("""SELECT `w_invno`,`w_invamt` FROM `tbl_warranty` WHERE 
			`w_uid`= %s""",(emailid))
        warrentyDtls = cursor.fetchone()

        if warrentyDtls == None:
        	warrentyDtls = {
        					"w_invamt": "",
					        "w_invno": "0"
					    }
        	msg = "Have No Protection+ Details"
        	return ({"attributes": {"status_desc": "User Protection Details",
                                "status": "success",
                                "msg": msg
                                },
                 "responseList": warrentyDtls}), status.HTTP_200_OK
        else:
        	cursor.execute("""SELECT `u_name`,`u_email_id`,`u_imei`,`u_mobile`,
        		`u_activ_code`,`u_pack_code` FROM `tbl_user` WHERE 
        		`u_email_id`=%s""",(emailid))
        	userDtls = cursor.fetchall()

        	for i in range(len(userDtls)):
        		if userDtls[i]['u_pack_code'] =='Semiannually':
        			cursor.execute("""SELECT u_id,`u_name`,`u_email_id`,`u_imei`,
        				`u_mobile`,`u_activ_code`,`u_pack_code`,`w_invno`,
        				`w_invamt`,`protection_date`,`valid_upto` FROM 
        				`tbl_user` tu inner join `tbl_protection_data` tpd on 
        				tu.`u_email_id`=tpd.`u_emailid` inner join 
        				`tbl_warranty` tw on tu.`u_email_id`=tw.`w_uid` WHERE 
        				`u_email_id`=%s and `u_pack_code`='Semiannually'""",(emailid))
        			protectionDtls = cursor.fetchone()

        			protectionDtls['protection_date'] = protectionDtls['protection_date'].isoformat()
        			protectionDtls['valid_upto'] = protectionDtls['valid_upto'].isoformat()

        			msg = "Protection+ Details"

        		elif userDtls[i]['u_pack_code'] =='Annually':
         			cursor.execute("""SELECT u_id,`u_name`,`u_email_id`,`u_imei`,
        				`u_mobile`,`u_activ_code`,`u_pack_code`,`w_invno`,
        				`w_invamt`,`protection_date`,`valid_upto` FROM 
        				`tbl_user` tu inner join `tbl_protection_data` tpd on 
        				tu.`u_email_id`=tpd.`u_emailid` inner join 
        				`tbl_warranty` tw on tu.`u_email_id`=tw.`w_uid` WHERE 
        				`u_email_id`=%s and `u_pack_code`='Annually'""",(emailid))
         			protectionDtls = cursor.fetchone()

         			protectionDtls['protection_date'] = protectionDtls['protection_date'].isoformat()
         			protectionDtls['valid_upto'] = protectionDtls['valid_upto'].isoformat()

         			msg = "Protection+ Details"

        	return ({"attributes": {"status_desc": "User Protection Details",
                                "status": "success",
                                "msg": msg
                                },
                 "responseList": protectionDtls}), status.HTTP_200_OK

#----------------------------------------------------------------------#
@name_space.route("/AddProtection")
class AddProtection(Resource):
	@api.expect(addProtection)
	def post(self):
		connection = connect_meeprotect()
		cursor = connection.cursor()
		details = request.get_json()
		today = date.today()

		emailid = details.get('emailid')
		activecode = details.get('activecode')
		w_invamt = details.get('w_invamt')
		w_invno = details.get('w_invno')

		cursor.execute("""SELECT `u_id`,u_name,u_email_id,u_userid,u_pass,
			u_date_of_birth,u_aniversary,u_ret_code,u_mobile,u_date,u_imei,
			u_activ_code,validity_start,validity_end,u_pack_code FROM 
			`tbl_user` WHERE u_email_id=%s""",(emailid))
		credentialDtls = cursor.fetchone()
		
		if credentialDtls:
			cursor.execute("""SELECT  `act_pack_code`,`act_pack_id`,`is_used` 
				FROM `tbl_activations` WHERE `act_code`=%s""",(activecode))
			actcodeDtls = cursor.fetchone()

			if actcodeDtls:
				if actcodeDtls['act_pack_id'] ==10 or actcodeDtls['act_pack_id'] ==11 or actcodeDtls['act_pack_id'] ==13 or actcodeDtls['act_pack_id'] ==14 or actcodeDtls['act_pack_id'] ==15 or actcodeDtls['act_pack_id'] ==16 or actcodeDtls['act_pack_id'] ==17 and w_invamt < 30000:
					msg = "Non Valid Protection+ Code"

				elif actcodeDtls['is_used'] == 1 and w_invamt < 30000:
						msg = "Already used Protection+ Code"

				elif actcodeDtls['is_used'] == 0 and w_invamt < 30000:

					protectionquery = ("""INSERT INTO tbl_user(u_name,
						u_email_id,u_userid,u_pass,u_date_of_birth,u_aniversary,
						u_ret_code,u_mobile,u_date,u_imei,u_activ_code,
						validity_start,validity_end,u_pack_code) VALUES (%s,%s,%s,
						%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)""")
					protectdata = cursor.execute(protectionquery,(credentialDtls['u_name'],
						credentialDtls['u_email_id'],credentialDtls['u_userid'],
						credentialDtls['u_pass'],credentialDtls['u_date_of_birth'],
						credentialDtls['u_aniversary'],credentialDtls['u_ret_code'],
						credentialDtls['u_mobile'],today,credentialDtls['u_imei'],
						activecode,credentialDtls['validity_start'],
						credentialDtls['validity_end'],actcodeDtls['act_pack_code']))

					if protectdata:
						if w_invamt <= 15000 and actcodeDtls['act_pack_id'] == 18:
							totlamt='Rs.499'
							protectionplus_value = 499
							validity = today.replace(month=today.month + 6)

						elif w_invamt > 15000 and w_invamt < 30000 and actcodeDtls['act_pack_id'] == 18:
							totlamt='Rs.699'
							protectionplus_value = 699
							validity = today.replace(month=today.month + 6)

						elif w_invamt <= 15000 and actcodeDtls['act_pack_id'] == 19:
							totlamt='Rs.799'
							protectionplus_value = 799
							validity = today.replace(year=today.year + 1)

						elif w_invamt > 15000 and w_invamt < 30000 and actcodeDtls['act_pack_id'] == 19:
							totlamt='Rs.1199'
							protectionplus_value = 1199
							validity = today.replace(year=today.year + 1)
						
						updateactivation = ("""UPDATE `tbl_activations` SET 
				            `is_used`=%s WHERE act_code= %s""")
						updateactivationdata = cursor.execute(updateactivation,
				        	(1,activecode))

						cursor.execute("""SELECT * FROM `tbl_warranty` WHERE 
							`w_uid`=%s""",(emailid))
						warrentyDtls = cursor.fetchone()

						if warrentyDtls == None:
							warrentyquery = ("""INSERT INTO tbl_warranty(w_uid,
								w_invno,w_invamt) VALUES (%s,%s,%s)""")
							warrentydata = cursor.execute(warrentyquery,(emailid,
								w_invno,w_invamt))

							protectquery = ("""INSERT INTO `tbl_protection_data`(`u_emailid`,
								`protectionplus_value`,`protection_date`,
								`valid_upto`) VALUES(%s,%s,%s,%s)""")
							protectdata = cursor.execute(protectquery,(emailid,
								protectionplus_value,today,validity))

						else:
							updatewarrenty = ("""UPDATE `tbl_warranty` SET 
					            w_invno=%s,w_invamt=%s WHERE w_uid= %s""")
							updatewarrentydata = cursor.execute(updatewarrenty,
					        	(emailid,w_invno,w_invamt))

							protectquery = ("""INSERT INTO `tbl_protection_data`(`u_emailid`,
								`protectionplus_value`,`protection_date`,
								`valid_upto`) VALUES(%s,%s,%s,%s)""")
							protectdata = cursor.execute(protectquery,(emailid,
								protectionplus_value,today,validity))

						#----------------------------sms-----------------------#
						# url = "http://cloud.smsindiahub.in/vendorsms/pushsms.aspx?"
						# user = 'creamsonintelli'
						# password = 'denver@1234'
						# msisdn = credentialDtls['u_mobile']
						# sid = 'CRMLTD'
						# msg1 = 'Thank you for choosing Protection Plus. Protection Plus has been activated for your device with the following details:'
						# msg11 = '  \n'
						# msg2 = 'IMEI :'+ ' '+credentialDtls['u_imei'] 
						# msg3 = 'Invoice Number:'+ ' '+w_invno 
						# msg4= 'Invoice Date:'+ ' '+format(today)
						# msg5 = 'Invoice Amount:'+ ' '+format(w_invamt) 
						# msg6 = 'Total Amount paid:'+ ' '+totlamt 
						# msg7 = 'Validity :'+ ' '+format(validity)
						# msg = msg1+'\n'+msg2+'\n'+msg3+'\n'+msg4+'\n'+msg5+'\n'+msg6+'\n'+msg7
						# fl = '0'
						# gwid = '2'
						# payload ="user={}&password={}&msisdn={}&sid={}&msg={}&fl={}&gwid={}".format(user,password,
						# 	msisdn,sid,msg,fl,gwid)
						# postUrl = url+payload
						# # print(msg)
						# response = requests.request("POST", postUrl)

						# sms_response = json.loads(response.text)['ErrorMessage']
						# # print(sms_response)
						# res = {"status":sms_response}
						# if res['status'] == 'Success':
						# 	sent = 'Y'
						# else:
						# 	sent = 'N'
						#----------------------------sms-----------------------#
						msg = "Successfully Inserted"
				else:
					msg = "Invalid Amount"
			else:
				msg = "Activation Code Does Not Exists"
		else:
			msg = "User Not Exists"	

		connection.commit()
		cursor.close()
		return ({"attributes": {"status_desc": "Protection+ Details",
                                "status": "success",
                                "msg": msg
	                            },
	            "responseList": details}), status.HTTP_200_OK

#----------------------------------------------------------------------#
@name_space.route("/AddDeviceDetails")
class AddDeviceDetails(Resource):
	@api.expect(deviceDtls)
	def post(self):
		connection = connect_meeprotect()
		cursor = connection.cursor()
		details = request.get_json()
		
		userid = details.get('userid')
		device_type = details.get('device_type')
		device_token = details.get('device_token')

		cursor.execute("""SELECT `user_device_id` FROM `user_device` WHERE user_id=%s""",
			(userid))
		deviceDtls = cursor.fetchone()
		
		if deviceDtls == None:
			devicequery = ("""INSERT INTO `user_device`(`user_id`,`device_type`,
			 `device_token`) VALUES(%s,%s,%s)""")
			devicedata = cursor.execute(devicequery,(userid,device_type,device_token))

			msg = "Successfully Inserted"

		else:
			updatedevice = ("""UPDATE `user_device` SET device_type=%s,
				`device_token`=%s WHERE user_id= %s""")
			updatedevicedata = cursor.execute(updatedevice,(device_type,
				device_token,userid))
			msg = "Successfully Updated"

		connection.commit()
		cursor.close()
		return ({"attributes": {"status_desc": "Device Details",
                                "status": "success",
                                "msg": msg
                                },
	            "responseList": details}), status.HTTP_200_OK

#-----------------------------------------------------------------------------#
@name_space.route("/UnlockFeatures")
class UnlockFeatures(Resource):
	@api.expect(unlockfeatures)
	def put(self):
		connection = connect_meeprotect()
		cursor = connection.cursor()
		details = request.get_json()
		
		u_mobile = details.get('u_mobile')
		activecode = details.get('activecode')

		cursor.execute("""SELECT `u_id`,u_name,u_email_id,u_userid,u_pass,
			u_date_of_birth,u_aniversary,u_ret_code,u_mobile,u_date,u_imei,
			u_activ_code,validity_start,validity_end,u_pack_code FROM 
			`tbl_user` WHERE u_mobile=%s""",(u_mobile))
		CredentialDtls = cursor.fetchone()
		
		if CredentialDtls:
			
			cursor.execute("""SELECT  `act_pack_code`,`au_id` ,`code_expire` FROM 
				`tbl_activations` WHERE `act_code`=%s and `is_used`=0""",(activecode))
			actcodeDtls = cursor.fetchone()

			if actcodeDtls:
				if actcodeDtls['act_pack_code'] =='YRLY' and actcodeDtls['au_id'] == 0:
					validity_start = date.today()
					validity_end = validity_start.replace(year=validity_start.year + 1)
								
					updateuser = ("""UPDATE `tbl_user` SET `u_activ_code`=%s,
						`validity_start`=%s,`validity_end`=%s where `u_id`=%s""")
					updateuserdata = cursor.execute(updateuser,(activecode,validity_start,
						validity_end,CredentialDtls['u_id']))

					if updateuserdata:
						updateactivation = ("""UPDATE `tbl_activations` SET `is_used`=%s 
							where `act_code`=%s""")
						updateactivationdata = cursor.execute(updateactivation,(1,activecode))
						msg = "Successfully Updated"

					else:
						msg = "Not Updated"

				elif actcodeDtls['act_pack_code'] =='YRLY' and actcodeDtls['au_id'] != 0:
					currentdatetime = datetime.today()
					code_expire = actcodeDtls['code_expire']
					
					if code_expire > currentdatetime:

						validity_start = date.today()
						validity_end = validity_start.replace(year=validity_start.year + 1)
									
						updateuser = ("""UPDATE `tbl_user` SET `u_activ_code`=%s,
							`validity_start`=%s,`validity_end`=%s where `u_id`=%s""")
						updateuserdata = cursor.execute(updateuser,(activecode,validity_start,
							validity_end,CredentialDtls['u_id']))

						if updateuserdata:
							updateactivation = ("""UPDATE `tbl_activations` SET `is_used`=%s 
								where `act_code`=%s""")
							updateactivationdata = cursor.execute(updateactivation,(1,activecode))
							msg = "Successfully Updated"

						else:
							msg = "Not Updated"

					else:
						msg = "Inactive Yearly Activation Code For Delta Core"

				if actcodeDtls['act_pack_code'] =='LFTM' and actcodeDtls['au_id'] == 0:
					validity_start = date.today()
					validity_end = '0000-00-00'

					updateuser = ("""UPDATE `tbl_user` SET `u_activ_code`=%s,
						`validity_start`=%s,`validity_end`=%s where `u_id`=%s""")
					updateuserdata = cursor.execute(updateuser,(activecode,validity_start,
						validity_end,CredentialDtls['u_id']))

					if updateuserdata:
						updateactivation = ("""UPDATE `tbl_activations` SET `is_used`=%s 
							where `act_code`=%s""")
						updateactivationdata = cursor.execute(updateactivation,(1,activecode))
						msg = "Successfully Updated"

					else:
						msg = "Not Updated"

				elif actcodeDtls['act_pack_code'] =='LFTM' and actcodeDtls['au_id'] != 0:
					currentdatetime = datetime.today()
					code_expire = actcodeDtls['code_expire']
					
					if code_expire > currentdatetime:

						validity_start = date.today()
						validity_end = '0000-00-00'

						updateuser = ("""UPDATE `tbl_user` SET `u_activ_code`=%s,
							`validity_start`=%s,`validity_end`=%s where `u_id`=%s""")
						updateuserdata = cursor.execute(updateuser,(activecode,validity_start,
							validity_end,CredentialDtls['u_id']))

						if updateuserdata:
							updateactivation = ("""UPDATE `tbl_activations` SET `is_used`=%s 
								where `act_code`=%s""")
							updateactivationdata = cursor.execute(updateactivation,(1,activecode))
							msg = "Successfully Updated"

						else:
							msg = "Not Updated"

					else:
						msg = "Inactive Lifetime Activation Code For Delta Core"
			
			else:
				msg = "Already Used Activation Code"
			
		cursor.execute("""SELECT `u_id`,u_name,u_email_id,u_userid,u_pass,
			u_date_of_birth,u_aniversary,u_ret_code,u_mobile,u_date,u_imei,
			u_activ_code,validity_start,validity_end,u_pack_code FROM 
			`tbl_user` WHERE u_mobile=%s""",(u_mobile))
		credentialDtls = cursor.fetchone()
		
		if credentialDtls:
			credentialDtls['u_date'] = credentialDtls['u_date'].isoformat()
			
			if credentialDtls['u_date_of_birth']=='0000-00-00':
				credentialDtls['u_date_of_birth'] = '0000-00-00'
			else:
				credentialDtls['u_date_of_birth'] = credentialDtls['u_date_of_birth'].isoformat()
			
			if credentialDtls['u_aniversary']=='0000-00-00':
				credentialDtls['u_aniversary'] = '0000-00-00'
			else:
				credentialDtls['u_aniversary'] = credentialDtls['u_aniversary'].isoformat()
				
			if credentialDtls['validity_start']=='0000-00-00':
				credentialDtls['validity_start'] = '0000-00-00'
			else:
				credentialDtls['validity_start'] = credentialDtls['validity_start'].isoformat()
				
			if credentialDtls['validity_end']=='0000-00-00':
				credentialDtls['validity_end'] = '0000-00-00'
			else:
				credentialDtls['validity_end'] = credentialDtls['validity_end'].isoformat()
		
		connection.commit()
		cursor.close()
		return ({"attributes": {"status_desc": "Unlock Features Details",
                                "status": "success",
                                "msg": msg
	                            },
	            "responseList": credentialDtls}), status.HTTP_200_OK

#----------------------------------------------------------------------#
@name_space.route("/AddImageUrl")
class AddImageUrl(Resource):
	@api.expect(addimage)
	def put(self):
		connection = connect_meeprotect()
		cursor = connection.cursor()
		details = request.get_json()
		
		image_url = details.get('image_url')
		u_mobile = details.get('u_mobile')

		cursor.execute("""SELECT `u_id` FROM tbl_user WHERE u_mobile=%s""",
			(u_mobile))
		userDtls = cursor.fetchone()
		
		if userDtls:
			updateuserDtls = ("""UPDATE `tbl_user` SET image_url=%s WHERE 
				u_mobile= %s""")
			updateuserdata = cursor.execute(updateuserDtls,(image_url,
				u_mobile))
			if updateuserdata:
				msg = "Successfully Updated"

			else:
				msg = "Not Updated"

		else:
			msg = "User Not Exists"

		connection.commit()
		cursor.close()
		return ({"attributes": {"status_desc": "User Image Details",
                                "status": "success",
                                "msg": msg
                                },
	            "responseList": details}), status.HTTP_200_OK

#-----------------------------------------------------------------------------#
@name_space.route("/CheckRetailerCode/<string:ret_code>")
class CheckRetailerCode(Resource):
    def get(self,ret_code):
        connection = connect_meeprotect()
        cursor = connection.cursor()
        
        cursor.execute("""SELECT * FROM tbl_channel_users WHERE au_code=%s""",
        	(ret_code))
        retailerdtls = cursor.fetchone()

        if retailerdtls:
        	msg = "Exists"

        else:
        	msg = "Not Exists"

        return ({"attributes": {"status_desc": "Retailer Code Details",
                                "status": "success"
                                },
                 "responseList": msg }), status.HTTP_200_OK

#--------------------------------------------------------------------------#
@name_space.route("/RetailerLogin")
class RetailerLogin(Resource):
	@api.expect(retLogin)
	def post(self):
		connection = connect_meeprotect()
		cursor = connection.cursor()
		details = request.get_json()
		today = date.today()

		distributorPhno = details.get('distributorPhno')
		username = details.get('username')
		password = details.get('password')
		ret_code = details.get('ret_code')
		ret_name = details.get('ret_name')
		
		cursor.execute("""SELECT `au_id` FROM tbl_channel_users WHERE 
			au_phone=%s""",(distributorPhno))
		distributorDtls = cursor.fetchone()

		if distributorDtls:
			au_parent = distributorDtls['au_id']
		
			cursor.execute("""SELECT `au_id`,`au_name`,`au_username`,`au_pass`,
				`au_code` FROM tbl_channel_users WHERE au_code=%s""",
				(ret_code))
			retailerDtls = cursor.fetchone()

			if retailerDtls:
				msg = "Retailer Exists"

				return ({"attributes": {"status_desc": "User Image Details",
                                "status": "success",
                                "msg": msg
                                },
	            "responseList": retailerDtls}), status.HTTP_200_OK

			else:
				retailerquery = ("""INSERT INTO `tbl_channel_users`(`au_name`,
					`au_email`,`au_phone`,`au_jdate`,`au_comp`,`au_country`,
					`au_code`,`au_username`,`au_pass`,`au_parent`) VALUES(%s,%s,
					%s,%s,%s,%s,%s,%s,%s,%s)""")
				retailerdata = cursor.execute(retailerquery,(ret_name,username,
					password,today,ret_name,'India',ret_code,username,password,
					distributorPhno))

				if retailerdata:
					msg = "Successfully Added"
				
				else:
					msg = "Not Added"
		else:
			msg = "Distributor Not Exists"

		connection.commit()
		cursor.close()
		return ({"attributes": {"status_desc": "Retailer Details",
                                "status": "success",
                                "msg": msg
                                },
	            "responseList": details}), status.HTTP_200_OK

#-----------------------------------------------------------------------#
@name_space.route("/IntruderSelfie")
class IntruderSelfie(Resource):
	@api.expect(intruderselfie)
	def post(self):
		connection = connect_meeprotect()
		cursor = connection.cursor()
		details = request.get_json()

		i_image = details.get('i_image')
		u_mobile = details.get('u_mobile')
		
		cursor.execute("""SELECT u_name,u_email_id,u_mobile FROM tbl_user 
			WHERE u_mobile=%s""",(u_mobile))
		userDtls = cursor.fetchone()

		if userDtls:
			cursor.execute("""SELECT dev_lat,dev_long FROM `tbl_device_loc` 
				WHERE `dev_user`=%s""",(userDtls['u_email_id']))
			deviceLoc = cursor.fetchone()

			cursor.execute("""SELECT dev_lat,dev_long FROM `tbl_device_track` 
				WHERE `dev_user`=%s""",(userDtls['u_email_id']))
			deviceTrack = cursor.fetchone()

			if deviceTrack['dev_lat'] != deviceLoc['dev_lat'] and deviceTrack['dev_long'] != deviceLoc['dev_long']:
				location = 'https://www.google.es/maps/place/{},{}'.format(deviceTrack['dev_lat'],deviceTrack['dev_long'])

			else:
				location = 'https://www.google.es/maps/place/{},{}'.format(deviceLoc['dev_lat'],deviceLoc['dev_long'])

			intruderquery = ("""INSERT INTO `tbl_getlooker`(`u_phoneno`,
				`u_image`) VALUES(%s,%s)""")
			intruderdata = cursor.execute(intruderquery,(u_mobile,i_image))
			
			if intruderdata:
				msgg = "Successfully Added"

			else:
				msgg = "Not Added"

			#------------------------mail-service------------------#
			URL = BASE_URL + "meprotect_mail/CommunicationAPI/mailForIntruderSelfie"

			headers = {'Content-type':'application/json', 'Accept':'application/json'}

			payload = {"toMail":userDtls['u_email_id'],
						"w_user":userDtls['u_name'],
                        "w_image":i_image,
						"location":location
					}

			mailResponse = requests.post(URL,data=json.dumps(payload), headers=headers).json()
			# print(mailResponse)
	        #------------------------mail-service------------------#

			#----------------------------sms-----------------------#
			url = "http://cloud.smsindiahub.in/vendorsms/pushsms.aspx?"
			user = 'creamsonintelli'
			password = 'denver@1234'
			msisdn = userDtls['u_mobile']
			sid = 'CRMLTD'
			msg = 'Hi '+userDtls['u_name']+' is in emergency. photo '+i_image+' and location '+location+'. Thank you for choosing Meprotect.'
			fl = '0'
			gwid = '2'
			payload ="user={}&password={}&msisdn={}&sid={}&msg={}&fl={}&gwid={}".format(user,password,
				msisdn,sid,msg,fl,gwid)
			postUrl = url+payload
			# print(msg)
			response = requests.request("POST", postUrl)

			sms_response = json.loads(response.text)['ErrorMessage']
			# print(sms_response)
			res = {"status":sms_response}
			if res['status'] == 'Success':
				sent = 'Y'
			else:
				sent = 'N'
			#----------------------------sms-----------------------#
			
		else:
			intruderquery = ("""INSERT INTO `tbl_getlooker`(`u_phoneno`,
				`u_image`) VALUES(%s,%s)""")
			intruderdata = cursor.execute(intruderquery,(u_mobile,i_image))
			
			if intruderdata:
				msgg = "Successfully Added"

			else:
				msgg = "Not Added"

			#----------------------------sms-----------------------#
			location = 'https://www.google.es/maps/place/0,0'

			url = "http://cloud.smsindiahub.in/vendorsms/pushsms.aspx?"
			user = 'creamsonintelli'
			password = 'denver@1234'
			msisdn = u_mobile
			sid = 'CRMLTD'
			msg = 'Hi User'+ ' is in emergency. photo '+i_image+' and location '+location+'. Thank you for choosing Meprotect.'
			fl = '0'
			gwid = '2'
			payload ="user={}&password={}&msisdn={}&sid={}&msg={}&fl={}&gwid={}".format(user,password,
				msisdn,sid,msg,fl,gwid)
			postUrl = url+payload
			
			response = requests.request("POST", postUrl)

			sms_response = json.loads(response.text)['ErrorMessage']
			
			res = {"status":sms_response}
			if res['status'] == 'Success':
				sent = 'Y'
			else:
				sent = 'N'
			#----------------------------sms-----------------------#
			
		connection.commit()
		cursor.close()
		return ({"attributes": {"status_desc": "Intruder Details",
                                "status": "success",
                                "msg": msgg
                                },
	            "responseList": details}), status.HTTP_200_OK

#----------------------------------------------------------#
@name_space.route("/UpdateUserProfile")
class UpdateUserProfile(Resource):
	@api.expect(userprofile)
	def put(self):
		connection = connect_meeprotect()
		cursor = connection.cursor()
		details = request.get_json()
		
		userid = details.get('userid')
		username = details.get('username')
		emailid = details.get('emailid')
		dob = details.get('dob')
		aniversary = details.get('aniversary')
		retid = details.get('retid')
		imei = details.get('imei')
		
		cursor.execute("""SELECT `u_id`,u_name,u_email_id,u_userid,u_pass,
			u_date_of_birth,u_aniversary,u_ret_code,u_mobile,u_date,u_imei,
			u_activ_code,validity_start,validity_end,u_pack_code FROM 
			`tbl_user` WHERE u_id=%s""",(userid))
		CredentialDtls = cursor.fetchone()
		
		if CredentialDtls:
			
			if not username:
				username = CredentialDtls.get('u_name')

			if not emailid:
				emailid = CredentialDtls.get('u_email_id')

			if not dob:
				dob = CredentialDtls.get('u_date_of_birth')

			if not aniversary:
				aniversary = CredentialDtls.get('u_aniversary')

			if not retid:
				retid = CredentialDtls.get('u_ret_code')

			if not imei:
				imei = CredentialDtls.get('u_imei')

			update_userdata = ("""UPDATE `tbl_user` SET `u_name`=%s,
	            `u_email_id`= %s,`u_date_of_birth`= %s,`u_aniversary`= %s,
	            `u_imei`=%s,`u_ret_code`= %s WHERE `u_id`= %s""")

			updatedata = cursor.execute(update_userdata,(username,emailid,dob,
				aniversary,imei,retid,userid))

			if updatedata:
				msg = "Updated"
			else:
				msg = "Not Updated"
		else:
			msg = "User not exists"

		connection.commit()
		cursor.close()
		return ({"attributes": {"status_desc": "Update User Details",
                                "status": "success",
                                "msg": msg
	                            },
	            "responseList": details}), status.HTTP_200_OK

#----------------------------------------------------------------------#
@name_space.route("/ResetPassword")
class ResetPassword(Resource):
	@api.expect(resetpassword)
	def put(self):
		connection = connect_meeprotect()
		cursor = connection.cursor()
		details = request.get_json()
		
		userid = details.get('userid')
		password = details.get('password')

		cursor.execute("""SELECT `u_id` FROM tbl_user WHERE u_id=%s""",
			(userid))
		userDtls = cursor.fetchone()
		
		if userDtls:
			updateuserDtls = ("""UPDATE `tbl_user` SET u_pass=%s WHERE 
				u_id= %s""")
			updateuserdata = cursor.execute(updateuserDtls,(password,
				userid))
			if updateuserdata:
				msg = "Successfully Updated"

			else:
				msg = "Not Updated"

		else:
			msg = "User Not Exists"

		connection.commit()
		cursor.close()
		return ({"attributes": {"status_desc": "Reset Password Details",
                                "status": "success",
                                "msg": msg
                                },
	            "responseList": details}), status.HTTP_200_OK