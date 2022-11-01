from flask import Flask, request, jsonify, json
from flask_api import status
from jinja2._compat import izip
from datetime import datetime,timedelta,date
import pymysql
from flask_cors import CORS, cross_origin
from flask import Blueprint
from flask_restplus import Api, Resource, fields
from database_connections import connect_mobileprotection,connect_meeprotect
import requests
import calendar
import json

app = Flask(__name__)
cors = CORS(app)

mobile_protection = Blueprint('mobile_protection_api', __name__)

api = Api(mobile_protection, version='1.0', title='DeltaCore API',
        description='DeltaCore API')
name_space = api.namespace('MobileProtectionAPI', description='MobileProtection')


# BASE_URL = "http://ec2-18-218-68-83.us-east-2.compute.amazonaws.com/flaskapp/"
#--------------------------------------------------------------------#
claimreq = api.model('claimreq', {
    "ret_code": fields.String(),
    "userid": fields.Integer(),
    "status_id": fields.Integer(),
    "imageurl": fields.String(),
    "remarks": fields.String()
    })

protectionsetting = api.model('protectionsetting', {
    "ret_code": fields.String(),
    "logo": fields.String(),
    "text": fields.String()
    })

updatesetting = api.model('updatesetting', {
    "ret_code": fields.String(),
    "logo": fields.String(),
    "text": fields.String()
    })
#--------------------------------------------------------------------#
@name_space.route("/MobileProtectionSettingDetailsByRetCode/<string:retcode>")
class MobileProtectionSettingDetailsByRetCode(Resource):
    def get(self,retcode):
        connection = connect_mobileprotection()
        cursor = connection.cursor()

        cursor.execute("""SELECT * FROM `mobile_protection_setting` WHERE 
            `retcode`=%s""",(retcode))
        settingDtls = cursor.fetchone()

        if settingDtls:
            
            settingDtls['last_update_ts'] = settingDtls['last_update_ts'].isoformat()
        else:
            settingDtls = {}

        connection.commit()
        cursor.close()

        return ({"attributes": {"status_desc": "Mobile Protection Setting Details",
                            "status": "success"
                            },
             "responseList": settingDtls}), status.HTTP_200_OK

#--------------------------------------------------------------#
@name_space.route("/MobileProtectionClaimStatusDesc")
class MobileProtectionClaimStatusDesc(Resource):
    def get(self):
        connection = connect_mobileprotection()
        cursor = connection.cursor()

        cursor.execute("""SELECT * FROM `status_master`""")
        statusDtls = cursor.fetchall()

        if statusDtls:
            
            for i in range(len(statusDtls)):
                statusDtls[i]['last_update_ts'] = statusDtls[i]['last_update_ts'].isoformat()
        else:
            statusDtls = []

        connection.commit()
        cursor.close()

        return ({"attributes": {"status_desc": "Mobile Protection Status Description",
                            "status": "success"
                            },
             "responseList": statusDtls}), status.HTTP_200_OK

#--------------------------------------------------------------#
@name_space.route("/ProtectionClaimRequest")
class ProtectionClaimRequest(Resource):
    @api.expect(claimreq)
    def post(self):
        connection = connect_mobileprotection()
        cursor = connection.cursor()

        details = request.get_json()
        today = date.today()

        ret_code = details.get('ret_code')
        userid = details.get('userid')
        status_id = details.get('status_id')
        imageurl = details.get('imageurl')
        remarks = details.get('remarks')
        
        cursor.execute("""SELECT * FROM `protection_claimrequest` WHERE `userid`=%s
         and `ret_code`=%s""",(userid,ret_code))
        claimreqDtls = cursor.fetchone()
        
        if claimreqDtls:
            updateclaimreq = ("""UPDATE `protection_claimrequest` SET status_id=%s
                WHERE `userid`=%s and `ret_code`=%s""")
            updateclaimreqdata = cursor.execute(updateclaimreq,(status_id,
                userid,ret_code))

            claim_requestid = claimreqDtls['claim_requestid']
            details['claim_requestid'] = claim_requestid

            claimreqquery = ("""INSERT INTO `claimrequest_dtls`(`claim_requestid`, 
                `status_id`,`imageurl`, `remarks`) VALUES (%s,%s,%s,%s)""")
            claimreqdata = cursor.execute(claimreqquery,(claim_requestid,status_id,
                imageurl,remarks))
            
        else:
            reqquery = ("""INSERT INTO `protection_claimrequest`(`ret_code`,
                `userid`, `status_id`) VALUES (%s,%s,%s)""")
            reqdata = cursor.execute(reqquery,(ret_code,userid,1))

            claim_requestid = cursor.lastrowid
            details['claim_requestid'] = claim_requestid

            claimreqquery = ("""INSERT INTO `claimrequest_dtls`(`claim_requestid`, 
                `status_id`,`imageurl`, `remarks`) VALUES (%s,%s,%s,%s)""")
            claimreqdata = cursor.execute(claimreqquery,(claim_requestid,status_id,
                imageurl,remarks))

        connection.commit()
        cursor.close()
        return ({"attributes": {"status_desc": "Protection Claim Details",
                                "status": "success"
                                },
                "responseList": details}), status.HTTP_200_OK

#-------------------------------------------------------------#
@name_space.route("/MobileProtectionClaimDetailsByRequestId/<int:claimreq_id>")
class MobileProtectionClaimDetailsByRequestId(Resource):
    def get(self,claimreq_id):
        connection = connect_mobileprotection()
        cursor = connection.cursor()

        conn = connect_meeprotect()
        cur = conn.cursor()

        cursor.execute("""SELECT `reqdtls_id`,`userid`,pcr.`claim_requestid`,
            ret_code,status_desc,`imageurl`,`remarks`,crd.`last_update_ts` FROM 
            `protection_claimrequest` pcr INNER join `claimrequest_dtls` crd on 
            pcr.`claim_requestid`= crd.`claim_requestid` 
            INNER join `status_master` sm on crd.`status_id`= sm.`statusid` WHERE 
            pcr.`claim_requestid`=%s order by reqdtls_id desc""",(claimreq_id))
        claimDtls = cursor.fetchall()

        if claimDtls:
            
            for i in range(len(claimDtls)):
                claimDtls[i]['last_update_ts'] = claimDtls[i]['last_update_ts'].isoformat()

                cur.execute("""SELECT u_name,u_email_id,u_mobile FROM `tbl_user` 
                    WHERE `u_id`=%s""",(claimDtls[i]['userid']))
                username = cur.fetchone()
                claimDtls[i]['username'] = username['u_name']
                claimDtls[i]['u_email_id'] = username['u_email_id']
                claimDtls[i]['u_mobile'] = username['u_mobile']
        else:
            claimDtls = []

        conn.commit()
        cur.close()
        connection.commit()
        cursor.close()

        return ({"attributes": {"status_desc": "Mobile Protection Claim Details",
                            "status": "success"
                            },
             "responseList": claimDtls}), status.HTTP_200_OK

#--------------------------------------------------------------#
@name_space.route("/MobileProtectionClaimDetailsByRetailerCode/<string:retcode>")
class MobileProtectionClaimDetailsByRetailerCode(Resource):
    def get(self,retcode):
        connection = connect_mobileprotection()
        cursor = connection.cursor()

        conn = connect_meeprotect()
        cur = conn.cursor()

        cursor.execute("""SELECT distinct(`userid`),`reqdtls_id`,pcr.`claim_requestid`,ret_code,
            `imageurl`,status_desc,`remarks`,crd.`last_update_ts` FROM `protection_claimrequest` pcr INNER join 
            `claimrequest_dtls` crd on pcr.`claim_requestid`= crd.`claim_requestid` 
            and pcr.`status_id`= crd.`status_id`
            INNER join `status_master` sm on crd.`status_id`= sm.`statusid` WHERE 
            `ret_code`=%s order by reqdtls_id desc""",(retcode))
        claimDtls = cursor.fetchall()

        if claimDtls:
            
            for i in range(len(claimDtls)):
                claimDtls[i]['last_update_ts'] = claimDtls[i]['last_update_ts'].isoformat()

                cur.execute("""SELECT u_name,u_email_id,u_mobile FROM `tbl_user` 
                    WHERE `u_id`=%s""",(claimDtls[i]['userid']))
                username = cur.fetchone()
                claimDtls[i]['username'] = username['u_name']
                claimDtls[i]['u_email_id'] = username['u_email_id']
                claimDtls[i]['u_mobile'] = username['u_mobile']
        else:
            claimDtls = []

        conn.commit()
        cur.close()
        connection.commit()
        cursor.close()

        return ({"attributes": {"status_desc": "Mobile Protection Claim Details",
                            "status": "success"
                            },
             "responseList": claimDtls}), status.HTTP_200_OK

#--------------------------------------------------------------#
@name_space.route("/MobileProtectionClaimDetailsByUserId/<string:userid>")
class MobileProtectionClaimDetailsByUserId(Resource):
    def get(self,userid):
        connection = connect_mobileprotection()
        cursor = connection.cursor()

        conn = connect_meeprotect()
        cur = conn.cursor()

        cursor.execute("""SELECT `reqdtls_id`,`userid`,crd.`status_id`,pcr.`claim_requestid`,
            ret_code,`imageurl`,status_desc,`remarks`,crd.`last_update_ts` FROM 
            `protection_claimrequest` pcr INNER join 
            `claimrequest_dtls` crd on pcr.`claim_requestid`= crd.`claim_requestid`
            INNER join `status_master` sm on crd.`status_id`= sm.`statusid` WHERE 
            `userid`=%s order by reqdtls_id desc""",(userid))
        claimDtls = cursor.fetchall()

        if claimDtls:
            for i in range(len(claimDtls)):
                claimDtls[i]['last_update_ts'] = claimDtls[i]['last_update_ts'].isoformat()

                cur.execute("""SELECT u_name,u_email_id,u_mobile FROM `tbl_user` 
                WHERE `u_id`=%s""",(userid))
                username = cur.fetchone()
                claimDtls[i]['username'] = username['u_name']
                claimDtls[i]['u_email_id'] = username['u_email_id']
                claimDtls[i]['u_mobile'] = username['u_mobile']
        else:
            claimDtls = []

        conn.commit()
        cur.close()
        connection.commit()
        cursor.close()

        return ({"attributes": {"status_desc": "Mobile Protection Claim Details",
                            "status": "success"
                            },
             "responseList": claimDtls}), status.HTTP_200_OK


#--------------------------------------------------------------#
@name_space.route("/MobileProtectionSetting")
class MobileProtectionSetting(Resource):
    @api.expect(protectionsetting)
    def post(self):
        connection = connect_mobileprotection()
        cursor = connection.cursor()

        details = request.get_json()
        today = date.today()

        ret_code = details.get('ret_code')
        logo = details.get('logo')
        text = details.get('text')
        
        cursor.execute("""SELECT * FROM `mobile_protection_setting` WHERE 
            `retcode`=%s""",(ret_code))
        settingDtls = cursor.fetchone()

        if settingDtls:
            settingDtls['last_update_ts'] = settingDtls['last_update_ts'].isoformat()

            connection.commit()
            cursor.close()

            return ({"attributes": {"status_desc": "Protection Setting Details",
                                    "status": "success"
                                    },
                    "responseList": settingDtls}), status.HTTP_200_OK
        else:
            setquery = ("""INSERT INTO `mobile_protection_setting`(`retcode`,`logo`,`text`) 
                VALUES (%s,%s,%s)""")
            setdata = cursor.execute(setquery,(ret_code,logo,text))

            protection_settingid = cursor.lastrowid
            details['protection_settingid'] = protection_settingid

            
            connection.commit()
            cursor.close()
            return ({"attributes": {"status_desc": "Protection Setting Details",
                                    "status": "success"
                                    },
                    "responseList": details}), status.HTTP_200_OK

#-----------------------------------------------------------#
@name_space.route("/UpdateMobileProtectioSetting")
class UpdateMobileProtectioSetting(Resource):
    @api.expect(updatesetting)
    def put(self):
        connection = connect_mobileprotection()
        cursor = connection.cursor()
        details = request.get_json()
        
        ret_code = details.get('ret_code')
        logo = details.get('logo')
        text = details.get('text')

        updateDtls = ("""UPDATE `mobile_protection_setting` SET `logo`=%s,
            `text`=%s WHERE `retcode`= %s""")
        updatedata = cursor.execute(updateDtls,(logo,
            text,ret_code))
        if updatedata:
            msg = "Successfully Updated"

        else:
            msg = "Not Updated"

        connection.commit()
        cursor.close()
        return ({"attributes": {"status_desc": "Protection Setting Details",
                                "status": "success",
                                "msg": msg
                                },
                "responseList": details}), status.HTTP_200_OK

#------------------------------------------------------------#
@name_space.route("/MobileProtectionClaimCountDetailsByRetailerCode/<string:retcode>")
class MobileProtectionClaimCountDetailsByRetailerCode(Resource):
    def get(self,retcode):
        connection = connect_mobileprotection()
        cursor = connection.cursor()

        cursor.execute("""SELECT count(distinct(pcr.`claim_requestid`))as total
            FROM `protection_claimrequest` pcr 
            INNER join `claimrequest_dtls` crd on pcr.`claim_requestid`= crd.`claim_requestid` 
            INNER join `status_master` sm on pcr.`status_id`= sm.`statusid` WHERE 
            pcr.`status_id`=1 and `ret_code`=%s order by reqdtls_id desc""",(retcode))
        acceptedCount = cursor.fetchone()
            
        if acceptedCount:
            accepted_by_retailer = acceptedCount['total']
        else:
            accepted_by_retailer = 0

        cursor.execute("""SELECT count(distinct(pcr.`claim_requestid`))as total
            FROM `protection_claimrequest` pcr 
            INNER join `claimrequest_dtls` crd on pcr.`claim_requestid`= crd.`claim_requestid` 
            INNER join `status_master` sm on pcr.`status_id`= sm.`statusid` WHERE 
            pcr.`status_id`=2 and `ret_code`=%s order by reqdtls_id desc""",(retcode))
        readyCount = cursor.fetchone()
        if readyCount:
            ready_to_pickup = readyCount['total']
        else:
            ready_to_pickup = 0

        cursor.execute("""SELECT count(distinct(pcr.`claim_requestid`))as total
            FROM `protection_claimrequest` pcr 
            INNER join `claimrequest_dtls` crd on pcr.`claim_requestid`= crd.`claim_requestid` 
            INNER join `status_master` sm on pcr.`status_id`= sm.`statusid` WHERE 
            pcr.`status_id`=3 and `ret_code`=%s order by reqdtls_id desc""",(retcode))
        completedCount = cursor.fetchone()
        if completedCount:
            completed= completedCount['total']
        else:
            completed = 0

        connection.commit()
        cursor.close()

        return ({"attributes": {"status_desc": "Claim Count Details",
                            "status": "success"
                            },
             "responseList": {
                                "accepted_by_retailer": accepted_by_retailer,
                                "ready_to_pickup": ready_to_pickup,
                                "completed":completed
                            }
                            }), status.HTTP_200_OK

#------------------------------------------------------------#
@name_space.route("/UserProtectionClaimDetailsByRetailerCodeStatusId/<string:retcode>/<int:statusid>")
class UserProtectionClaimDetailsByRetailerCodeStatusId(Resource):
    def get(self,retcode,statusid):
        connection = connect_mobileprotection()
        cursor = connection.cursor()

        conn = connect_meeprotect()
        cur = conn.cursor()
        
        cursor.execute("""SELECT `reqdtls_id`,`userid`,pcr.`claim_requestid`,ret_code,
            `imageurl`,`remarks` FROM `protection_claimrequest` pcr INNER join 
            `claimrequest_dtls` crd on pcr.`claim_requestid`= crd.`claim_requestid`
            and pcr.`status_id`= crd.`status_id` INNER join `status_master` sm on 
            pcr.`status_id`= sm.`statusid` WHERE crd.`status_id`=%s and 
            `ret_code`=%s order by crd.`last_update_ts` desc""",(statusid,retcode))
        userclaimDtls = cursor.fetchall()

        if userclaimDtls:
            
            for i in range(len(userclaimDtls)):
                cur.execute("""SELECT u_name,u_email_id,u_mobile FROM `tbl_user` 
                    WHERE `u_id`=%s""",(userclaimDtls[i]['userid']))
                username = cur.fetchone()
                userclaimDtls[i]['username'] = username['u_name']
                userclaimDtls[i]['u_email_id'] = username['u_email_id']
                userclaimDtls[i]['u_mobile'] = username['u_mobile']

                if statusid == 1:
                    cursor.execute("""SELECT `last_update_ts` FROM claimrequest_dtls 
                        where `claim_requestid`=%s ORDER BY last_update_ts desc limit 1""",
                        (userclaimDtls[i]['claim_requestid']))
                    claimrequest_ts = cursor.fetchone()

                    userclaimDtls[i]['claimrequest_ts'] = claimrequest_ts['last_update_ts'].isoformat()

                elif statusid == 2:
                    cursor.execute("""SELECT `last_update_ts` FROM claimrequest_dtls 
                        where `claim_requestid`=%s ORDER BY last_update_ts desc limit 1""",
                        (userclaimDtls[i]['claim_requestid']))
                    pickup_ts = cursor.fetchone()
                    userclaimDtls[i]['pickup_ts'] = pickup_ts['last_update_ts'].isoformat()
                else:
                    cursor.execute("""SELECT `last_update_ts` FROM claimrequest_dtls 
                        where `claim_requestid`=%s ORDER BY last_update_ts desc limit 2""",
                        (userclaimDtls[i]['claim_requestid']))

                    completed_ts = cursor.fetchall()
                    
                    for j in range(len(completed_ts)):
                        userclaimDtls[i]['completed_ts'] = completed_ts[0]['last_update_ts'].isoformat()
                        userclaimDtls[i]['pickup_ts'] = completed_ts[1]['last_update_ts'].isoformat()

        else:
            userclaimDtls = []

        conn.commit()
        cur.close()
        connection.commit()
        cursor.close()

        return ({"attributes": {"status_desc": "User Claim Details",
                            "status": "success"
                            },
             "responseList": userclaimDtls }), status.HTTP_200_OK

#--------------------------------------------------------------#
@name_space.route("/ProtectionPlanDetailsByRetailerCode/<string:retcode>")
class ProtectionPlanDetailsByRetailerCode(Resource):
    def get(self,retcode):
        connection = connect_mobileprotection()
        cursor = connection.cursor()

        conn = connect_meeprotect()
        cur = conn.cursor()
        
        cursor.execute("""SELECT * FROM `protection_plan` WHERE `ret_code`=%s""",
            (retcode))
        protectionplanDtls = cursor.fetchall()

        if protectionplanDtls:
            for i in range(len(protectionplanDtls)):
                protectionplanDtls[i]['last_update_ts'] = protectionplanDtls[i]['last_update_ts'].isoformat()

        else:
            protectionplanDtls = []

        # conn.commit()
        # cur.close()
        connection.commit()
        cursor.close()

        return ({"attributes": {"status_desc": "Protection Plan Details",
                            "status": "success"
                            },
             "responseList": protectionplanDtls }), status.HTTP_200_OK

#--------------------------------------------------------------#
@name_space.route("/MobileProtectionClaimDetailsByRetailerCodeRequestId/<string:retcode>/<int:claimreq_id>")
class MobileProtectionClaimDetailsByRetailerCodeRequestId(Resource):
    def get(self,retcode,claimreq_id):
        connection = connect_mobileprotection()
        cursor = connection.cursor()

        conn = connect_meeprotect()
        cur = conn.cursor()

        cursor.execute("""SELECT distinct(`userid`),`reqdtls_id`,pcr.`claim_requestid`,ret_code,
            `imageurl`,status_desc,`remarks`,crd.`last_update_ts` FROM `protection_claimrequest` pcr INNER join 
            `claimrequest_dtls` crd on pcr.`claim_requestid`= crd.`claim_requestid` 
            and pcr.`status_id`= crd.`status_id`
            INNER join `status_master` sm on crd.`status_id`= sm.`statusid` WHERE 
            `ret_code`=%s and pcr.`claim_requestid`=%s order by reqdtls_id desc""",(retcode,claimreq_id))
        claimDtls = cursor.fetchall()

        if claimDtls:
            
            for i in range(len(claimDtls)):
                claimDtls[i]['last_update_ts'] = claimDtls[i]['last_update_ts'].isoformat()

                cur.execute("""SELECT u_name,u_email_id,u_mobile FROM `tbl_user` 
                    WHERE `u_id`=%s""",(claimDtls[i]['userid']))
                username = cur.fetchone()
                claimDtls[i]['username'] = username['u_name']
                claimDtls[i]['u_email_id'] = username['u_email_id']
                claimDtls[i]['u_mobile'] = username['u_mobile']
        else:
            claimDtls = []

        conn.commit()
        cur.close()
        connection.commit()
        cursor.close()

        return ({"attributes": {"status_desc": "Mobile Protection Claim Details",
                            "status": "success"
                            },
             "responseList": claimDtls}), status.HTTP_200_OK

#--------------------------------------------------------------#
