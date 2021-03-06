from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from properties.p import Property
from datetime import datetime


import requests
import json
import hashlib
import urllib
import urllib2
import base64
import xlrd
import time

from Crypto.PublicKey import RSA
from Crypto import Random
from Crypto.Cipher import PKCS1_v1_5
from rest_example.wsgi import ReturnAllDict
from restapp.models import Audit

e = ReturnAllDict()
AllList = e.returnDict()
ApiHomeDict = AllList[0]
InputDict = AllList[1]
SuccessDict = AllList[2]
FailureDict = AllList[3]
JsonDict = AllList[4]
ListDict = AllList[5]

global_user_id = "UTEST3"
private_key2_pem = ""
tomcat_count = ""
BYTE_BOUNDARY = 8
BYTE_DIFFERENCE = 11
KEY_SIZE = 2048

prop = Property()
#prop_obj = prop.load_property_files('D:\\InvestAK\\investak.properties')  #hari
prop_obj = prop.load_property_files('E:\\Investak\\investak\\investak.properties')  #ranjith

def readProperty(name):
    data=prop_obj.get (name)
    return data

@api_view([readProperty('METHOD_TYPE')])
def get_initial_token(request):
    if request.method == readProperty('METHOD_TYPE'):
        content = request.body
        url = ApiHomeDict.get(readProperty('GET_INITIAL_KEY'))[0].url
        apiName = readProperty ("GET_INITIAL_KEY")
        print 'url',url
        authorization = request.META.get('HTTP_AUTHORIZATION')

        #if isNotBlank (content):
        jsonObject=checkJson(content)
        data = validation_and_manipulation (jsonObject, apiName, InputDict)
        print 'data ', data
        if 'stat' in data:
            return Response (data)
        else:
            print 'after validate '
            output = send_sequest(content, url, authorization, user_id="", tomcat_count="", jKey="", jData="")
            d = json.loads(output)
            initial_public_key1 = d[readProperty('PUBLIC_KEY')]
            tomcat_count = d[readProperty('TOMCAT_COUNT')]
            public_key1_pem = b64_decode(initial_public_key1)
            key_pair = generate_key_pair()
            public_key2_pem = get_public_key_pem(key_pair)
            private_key2_pem = get_private_key_pem(key_pair)
            public_key1 = import_key(public_key1_pem)
            jData = encrypt(public_key2_pem, public_key1, 2048)
            jKey = get_jkey(public_key1_pem)
            user_id = global_user_id

            url = ApiHomeDict.get(readProperty('GET_PRE_AUTHENTICATION_KEY'))[0].url
            content=readProperty('YES')
            output = send_sequest(content, url, authorization, user_id, tomcat_count, jKey, jData)
            initial_public_key3 = output[readProperty('PUBLIC_KEY3')]
            private_key2 = import_key(private_key2_pem)
            decrypted_public_key3 = decrypt(initial_public_key3, private_key2)
            print readProperty('SLASH_N')
            initial_token = replace_text(b64_encode(private_key2_pem),"\n","") + readProperty('HYPEN') + replace_text(b64_encode(decrypted_public_key3),"\n","") + readProperty('HYPEN') + replace_text(b64_encode(tomcat_count),"\n","")
            output = {readProperty('INITIAL_TOKEN'): initial_token}
            return Response(output)


@api_view([readProperty('METHOD_TYPE')])
def get_login_2fa(request):
    if request.method == readProperty ('METHOD_TYPE'):
        url = ApiHomeDict.get(readProperty("LOGIN_2FA"))[0].url
        apiName = readProperty ("LOGIN_2FA")
        print 'url',url
        authorization = request.META.get('HTTP_AUTHORIZATION')
        authorization=authorization.split("-")
        public_key3_pem = b64_decode(authorization[1].replace("\n",""))
        tomcat_count= b64_decode(authorization[2].replace("\n",""))
        jKey = get_jkey(public_key3_pem)
        userJSON=content = request.body
        jsonObject = checkJson (content)
        data = validation_and_manipulation (jsonObject, apiName, InputDict)
        print 'data ', data
        if 'stat' in data:
            return Response (data)
        else:
            print 'after validate '
            public_key3=import_key(public_key3_pem)
            jData = encrypt(userJSON,public_key3, 2048)
            tomcat_count=get_tomcat_count(tomcat_count)
            user_id=global_user_id
            output = send_sequest(content, url, authorization, user_id, tomcat_count, jKey, jData)
            return Response(output)


@api_view([readProperty ('METHOD_TYPE')])
def get_login(request):
    if request.method == readProperty('METHOD_TYPE'):
        url = ApiHomeDict.get(readProperty("GET_PRE_AUTHENTICATION_KEY"))[0].url
        apiName = readProperty ("GET_PRE_AUTHENTICATION_KEY")
        authorization = request.META.get('HTTP_AUTHORIZATION')
        authorization = authorization.split("-")
        public_key3_pem = b64_decode(authorization[1].replace("\n", ""))
        tomcat_count = b64_decode(authorization[2].replace("\n", ""))
        jKey = get_jkey(public_key3_pem)
        userJSON = content = request.body
        jsonObject = checkJson (content)
        data = validation_and_manipulation (jsonObject, apiName, InputDict)
        print 'data ', data
        if 'stat' in data:
            return Response (data)
        else:
            print 'after validate '
            json_data = json.dumps(data)
            public_key3 = import_key(public_key3_pem)
            jData = encrypt(json_data, public_key3, 2048)
            tomcat_count = get_tomcat_count(tomcat_count)
            user_id = global_user_id
            output = send_sequest(content, url, authorization, user_id, tomcat_count, jKey, jData)
            return Response(output)


@api_view([readProperty ('METHOD_TYPE')])
def get_normal_login(request):
    if request.method == readProperty ('METHOD_TYPE'):
        url = ApiHomeDict.get(readProperty("GET_PRE_AUTHENTICATION_KEY"))[0].url
        apiName = readProperty ("GET_PRE_AUTHENTICATION_KEY")
        authorization = request.META.get('HTTP_AUTHORIZATION')
        authorization=authorization.split("-")
        private_key2_pem=b64_decode(authorization[0].replace("\n",""))
        public_key3_pem = b64_decode(authorization[1].replace("\n",""))
        tomcat_count= b64_decode(authorization[2].replace("\n",""))
        jKey = get_jkey(public_key3_pem)
        userJSON=content = request.body
        jsonObject = checkJson (content)
        data = validation_and_manipulation (jsonObject, apiName, InputDict)
        print 'data ', data
        if 'stat' in data:
            return Response (data)
        else:
            print 'after validate '
            json_data = json.dumps(data)
            public_key3=import_key(public_key3_pem)
            jData = encrypt(json_data,public_key3, 2048)
            tomcat_count=get_tomcat_count(tomcat_count)
            user_id=global_user_id
            output = send_sequest(content, url, authorization, user_id, tomcat_count, jKey, jData)
            encrypted_data = output["jEncResp"]
            private_key2 = import_key(private_key2_pem)
            decrypted_data = decrypt(encrypted_data,private_key2)
            decrypted_json = json.loads(decrypted_data)
            print decrypted_json
            return Response(output)


@api_view([readProperty ('METHOD_TYPE')])
def get_default_login(request):
    if request.method == readProperty ('METHOD_TYPE'):
        url = ApiHomeDict.get(readProperty("DEFAULT_LOGIN"))[0].url
        apiName = readProperty ("DEFAULT_LOGIN")
        authorization = request.META.get('HTTP_AUTHORIZATION')
        authorization=authorization.split("-")
        public_key4_pem = b64_decode(authorization[1].replace("\n",""))
        tomcat_count= b64_decode(authorization[2].replace("\n",""))
        jKey = get_jkey(public_key4_pem)
        requestJSON=content = request.body
        jsonObject = checkJson (content)
        data = validation_and_manipulation (jsonObject, apiName, InputDict)
        print 'data ', data
        if 'stat' in data:
            return Response (data)
        else:
            print 'after validate '
            json_data = json.dumps(data)
            public_key4=import_key(public_key4_pem)
            jData = encrypt(json_data,public_key4, 2048)
            tomcat_count=get_tomcat_count(tomcat_count)
            user_id=global_user_id
            output = send_sequest(content, url, authorization, user_id, tomcat_count, jKey, jData)
            return Response(output)


@api_view([readProperty ('METHOD_TYPE')])
def get_valid_pwd(request):
    if request.method == readProperty ('METHOD_TYPE'):
        url = ApiHomeDict.get(readProperty("VALID_PASSWORD"))[0].url
        apiName = readProperty("VALID_PASSWORD")
        authorization = request.META.get('HTTP_AUTHORIZATION')
        authorization=authorization.split("-")
        public_key3_pem = b64_decode(authorization[1].replace("\n",""))
        tomcat_count= b64_decode(authorization[2].replace("\n",""))
        jKey = get_jkey(public_key3_pem)
        userJSON=content = request.body
        jsonObject = checkJson(content)
        data=PasswordHash(jsonObject)
        jsonObject = data
        request_id=investak_request_audit(global_user_id,jsonObject)
        print 'jsonObject ',jsonObject
        data = validation_and_manipulation (jsonObject,apiName,InputDict)
        print 'data ', data
        if 'stat' in data:
            #status=readProperty('F')
            api_response_audit(request_id,data,status)
            return Response(data)
        else:
            api_request_audit (request_id, data)
            print 'after validate '
            json_data = json.dumps (data)
            public_key3=import_key(public_key3_pem)
            jData = encrypt(json_data,public_key3, 2048)
            tomcat_count=get_tomcat_count(tomcat_count)
            user_id=global_user_id
            #output=''
            output = send_sequest(content, url, authorization, user_id, tomcat_count, jKey, jData)
            tso_response_audit (request_id, output,status)
            #data = validation_and_manipulation (output, apiName, SuccessDict)  #manipulation logic and call api_response_audit
            api_response_audit (request_id, output,status)
            return Response(output)

def investak_request_audit(userId,request):
    request_id=''
    dateNow = datetime.now ()
    Auditobj=Audit(user_id=userId,investak_request= request,investak_request_time_stamp=dateNow)
    Auditobj.save()
    request_id=Auditobj.request_id
    print 'investak_request_audit ',request
    print 'request_id ',request_id

    '''print 'dateNow ',dateNow
    Auditobj = Audit.objects.get(investak_request_time_stamp=dateNow)
    print 'Auditobj ', Auditobj.investak_request_time_stamp'''

    return request_id

def api_request_audit(request_id,request):
    dateNow = datetime.now ()

    obj, created = Audit.objects.update_or_create (
        request_id=request_id,
        defaults={'api_request': request,'api_request_time_stamp':dateNow},
    )
    print 'api_request_audit ',request

def api_response_audit(request_id,request,status):
    dateNow = datetime.now ()

    obj, created = Audit.objects.update_or_create (
        request_id=request_id,
        defaults={'api_response': request,'api_response_time_stamp':dateNow},
    )
    print 'api_response_audit ',request

def tso_response_audit(request_id,request,status):
    dateNow = datetime.now ()

    obj, created = Audit.objects.update_or_create (
        request_id=request_id,
        defaults={'tso_response': request,'tso_response_time_stamp':dateNow},
    )
    print 'tso_response_audit ',request

@api_view([readProperty ('METHOD_TYPE')])
def get_valid_ans(request):
    if request.method == readProperty('METHOD_TYPE'):
        url = ApiHomeDict.get(readProperty("VALID_ANSWER"))[0].url
        apiName = readProperty ("VALID_ANSWER")
        authorization = request.META.get('HTTP_AUTHORIZATION')
        authorization=authorization.split("-")
        private_key2_pem=b64_decode(authorization[0].replace("\n",""))
        public_key3_pem = b64_decode(authorization[1].replace("\n",""))
        tomcat_count= b64_decode(authorization[2].replace("\n",""))
        jKey = get_jkey(public_key3_pem)
        userJSON=content = request.body
        jsonObject = checkJson (content)
        data = validation_and_manipulation (jsonObject, apiName, InputDict)
        print 'data ', data
        if 'stat' in data:
            return Response (data)
        else:
            print 'after validate '
            json_data = json.dumps(data)
            public_key3=import_key(public_key3_pem)
            jData = encrypt(json_data,public_key3, 2048)
            tomcat_count=get_tomcat_count(tomcat_count)
            user_id=global_user_id
            output = send_sequest(content, url, authorization, user_id, tomcat_count, jKey, jData)
            encrypted_data=output["jEncResp"]
            private_key2 = import_key(private_key2_pem)
            decrypted_data=decrypt(encrypted_data,private_key2)
            decrypted_json = json.loads(decrypted_data)
            if decrypted_json["stat"]=="Ok":
                access_token = replace_text(b64_encode(private_key2_pem), "\n", "") + "-" \
                           + replace_text(b64_encode(decrypted_json["sUserToken"]), "\n", "") + "-" \
                           + replace_text(b64_encode(tomcat_count), "\n", "")
                output = {'access_token': access_token}
            else:
                output = {readProperty('STATUS'): "Not_Ok",readProperty('ERROR_MSG'): "Validation failed"}
            return Response(output)


@api_view([readProperty ('METHOD_TYPE')])
def get_account_info(request):
    if request.method == readProperty('METHOD_TYPE'):
        url = ApiHomeDict.get(readProperty("GET_PRE_AUTHENTICATION_KEY"))[0].url
        apiName = readProperty ("GET_PRE_AUTHENTICATION_KEY")
        authorization = request.META.get('HTTP_AUTHORIZATION')
        authorization=authorization.split("-")
        public_key4_pem = b64_decode(authorization[1].replace("\n",""))
        tomcat_count= b64_decode(authorization[2].replace("\n",""))
        jKey = get_jkey(public_key4_pem)
        requestJSON=content = request.body
        jsonObject = checkJson (content)
        data = validation_and_manipulation (jsonObject, apiName, InputDict)
        print 'data ', data
        if 'stat' in data:
            return Response (data)
        else:
            print 'after validate '
            json_data = json.dumps(data)
            public_key4=import_key(public_key4_pem)
            jData = encrypt(json_data,public_key4, 2048)
            tomcat_count=get_tomcat_count(tomcat_count)
            user_id=global_user_id
            output = send_sequest(content, url, authorization, user_id, tomcat_count, jKey, jData)
            return Response(output)


@api_view([readProperty ('METHOD_TYPE')])
def get_login_by_pass(request):
    return ''


@api_view([readProperty ('METHOD_TYPE')])
def get_load_retention_type(request):
    if request.method == readProperty ('METHOD_TYPE'):
        url = ApiHomeDict.get(readProperty("LOAD_RETENSION_TYPE"))[0].url
        apiName = readProperty ("LOAD_RETENSION_TYPE")
        authorization = request.META.get('HTTP_AUTHORIZATION')
        authorization=authorization.split("-")
        public_key4_pem = b64_decode(authorization[1].replace("\n",""))
        tomcat_count= b64_decode(authorization[2].replace("\n",""))
        jKey = get_jkey(public_key4_pem)
        requestJSON=content = request.body
        jsonObject = checkJson (content)
        data = validation_and_manipulation (jsonObject, apiName, InputDict)
        print 'data ', data
        if 'stat' in data:
            return Response (data)
        else:
            print 'after validate '
            json_data = json.dumps(data)
            public_key4=import_key(public_key4_pem)
            jData = encrypt(json_data,public_key4, 2048)
            tomcat_count=get_tomcat_count(tomcat_count)
            user_id=global_user_id
            output = send_sequest(content, url, authorization, user_id, tomcat_count, jKey, jData)
            return Response(output)


@api_view([readProperty ('METHOD_TYPE')])
def get_check_crkt_price_range(request):
    if request.method == readProperty ('METHOD_TYPE'):
        url = ApiHomeDict.get(readProperty("CHECK_CORRECT_PRICE_RANGE"))[0].url
        apiName = readProperty ("CHECK_CORRECT_PRICE_RANGE")
        authorization = request.META.get('HTTP_AUTHORIZATION')
        authorization = authorization.split("-")
        public_key4_pem = b64_decode(authorization[1].replace("\n", ""))
        tomcat_count = b64_decode(authorization[2].replace("\n", ""))
        jKey = get_jkey(public_key4_pem)
        requestJSON = content = request.body
        jsonObject = checkJson (content)
        data = validation_and_manipulation (jsonObject, apiName, InputDict)
        print 'data ', data
        if 'stat' in data:
            return Response (data)
        else:
            print 'after validate '
            json_data = json.dumps(data)
            public_key4 = import_key(public_key4_pem)
            jData = encrypt(json_data, public_key4, 2048)
            tomcat_count = get_tomcat_count(tomcat_count)
            user_id = global_user_id
            output = send_sequest(content, url, authorization, user_id, tomcat_count, jKey, jData)
            return Response(output)


@api_view([readProperty ('METHOD_TYPE')])
def get_validate_GTD(request):
    if request.method == readProperty ('METHOD_TYPE'):
        url = ApiHomeDict.get(readProperty("VALIDATE_GTD"))[0].url
        apiName = readProperty ("VALIDATE_GTD")
        authorization = request.META.get('HTTP_AUTHORIZATION')
        authorization = authorization.split("-")
        public_key4_pem = b64_decode(authorization[1].replace("\n", ""))
        tomcat_count = b64_decode(authorization[2].replace("\n", ""))
        jKey = get_jkey(public_key4_pem)
        requestJSON = content = request.body
        jsonObject = checkJson (content)
        data = validation_and_manipulation (jsonObject, apiName, InputDict)
        print 'data ', data
        if 'stat' in data:
            return Response (data)
        else:
            print 'after validate '
        json_data = json.dumps(data)
        public_key4 = import_key(public_key4_pem)
        jData = encrypt(json_data, public_key4, 2048)
        tomcat_count = get_tomcat_count(tomcat_count)
        user_id = global_user_id
        output = send_sequest(content, url, authorization, user_id, tomcat_count, jKey, jData)
        return Response(output)


@api_view([readProperty ('METHOD_TYPE')])
def get_validate_SLM_price(request):
    if request.method == readProperty ('METHOD_TYPE'):
        url = ApiHomeDict.get(readProperty("VALIDATE_SLM_PRICE"))[0].url
        apiName = readProperty ("VALIDATE_SLM_PRICE")
        authorization = request.META.get('HTTP_AUTHORIZATION')
        authorization = authorization.split("-")
        public_key4_pem = b64_decode(authorization[1].replace("\n", ""))
        tomcat_count = b64_decode(authorization[2].replace("\n", ""))
        jKey = get_jkey(public_key4_pem)
        requestJSON = content = request.body
        jsonObject = checkJson (content)
        data = validation_and_manipulation (jsonObject, apiName, InputDict)
        print 'data ', data
        if 'stat' in data:
            return Response (data)
        else:
            print 'after validate '
            json_data = json.dumps(data)
            public_key4 = import_key(public_key4_pem)
            jData = encrypt(json_data, public_key4, 2048)
            tomcat_count = get_tomcat_count(tomcat_count)
            user_id = global_user_id
            output = send_sequest(content, url, authorization, user_id, tomcat_count, jKey, jData)
            return Response(output)


@api_view([readProperty ('METHOD_TYPE')])
def get_place_order(request):
    if request.method == readProperty ('METHOD_TYPE'):
        url = ApiHomeDict.get(readProperty("PLACE_ORDER"))[0].url
        apiName = readProperty ("PLACE_ORDER")
        authorization = request.META.get('HTTP_AUTHORIZATION')
        authorization = authorization.split("-")
        public_key4_pem = b64_decode(authorization[1].replace("\n", ""))
        tomcat_count = b64_decode(authorization[2].replace("\n", ""))
        jKey = get_jkey(public_key4_pem)
        requestJSON = content = request.body
        jsonObject = checkJson (content)
        data = validation_and_manipulation (jsonObject, apiName, InputDict)
        print 'data ', data
        if 'stat' in data:
            return Response (data)
        else:
            print 'after validate '
            json_data = json.dumps(data)
            public_key4 = import_key(public_key4_pem)
            jData = encrypt(json_data, public_key4, 2048)
            tomcat_count = get_tomcat_count(tomcat_count)
            user_id = global_user_id
            output = send_sequest(content, url, authorization, user_id, tomcat_count, jKey, jData)
            return Response(output)


@api_view([readProperty ('METHOD_TYPE')])
def get_order_book(request):
    if request.method == readProperty ('METHOD_TYPE'):
        url = ApiHomeDict.get(readProperty("ORDER_BOOK"))[0].url
        apiName = readProperty ("ORDER_BOOK")
        authorization = request.META.get('HTTP_AUTHORIZATION')
        authorization = authorization.split("-")
        public_key4_pem = b64_decode(authorization[1].replace("\n", ""))
        tomcat_count = b64_decode(authorization[2].replace("\n", ""))
        jKey = get_jkey(public_key4_pem)
        requestJSON = content = request.body
        jsonObject = checkJson (content)
        data = validation_and_manipulation (jsonObject, apiName, InputDict)
        print 'data ', data
        if 'stat' in data:
            return Response (data)
        else:
            print 'after validate '
            json_data = json.dumps(data)
            public_key4 = import_key(public_key4_pem)
            jData = encrypt(json_data, public_key4, 2048)
            tomcat_count = get_tomcat_count(tomcat_count)
            user_id = global_user_id
            output = send_sequest(content, url, authorization, user_id, tomcat_count, jKey, jData)
            return Response(output)


@api_view([readProperty ('METHOD_TYPE')])
def get_modify_order(request):
    if request.method == readProperty ('METHOD_TYPE'):
        url = ApiHomeDict.get(readProperty("MODIFY_ORDER"))[0].url
        apiName = readProperty ("MODIFY_ORDER")
        authorization = request.META.get('HTTP_AUTHORIZATION')
        authorization = authorization.split("-")
        public_key4_pem = b64_decode(authorization[1].replace("\n", ""))
        tomcat_count = b64_decode(authorization[2].replace("\n", ""))
        jKey = get_jkey(public_key4_pem)
        requestJSON = content = request.body
        jsonObject = checkJson (content)
        data = validation_and_manipulation (jsonObject, apiName, InputDict)
        print 'data ', data
        if 'stat' in data:
            return Response (data)
        else:
            print 'after validate '
            json_data = json.dumps(data)
            public_key4 = import_key(public_key4_pem)
            jData = encrypt(json_data, public_key4, 2048)
            tomcat_count = get_tomcat_count(tomcat_count)
            user_id = global_user_id
            output = send_sequest(content, url, authorization, user_id, tomcat_count, jKey, jData)
            return Response(output)


@api_view([readProperty('METHOD_TYPE')])
def get_cancel_order(request):
    if request.method == readProperty ('METHOD_TYPE'):
        url = ApiHomeDict.get(readProperty("CANCEL_ORDER"))[0].url
        apiName = readProperty ("CANCEL_ORDER")
        authorization = request.META.get('HTTP_AUTHORIZATION')
        authorization = authorization.split("-")
        public_key4_pem = b64_decode(authorization[1].replace("\n", ""))
        tomcat_count = b64_decode(authorization[2].replace("\n", ""))
        jKey = get_jkey(public_key4_pem)
        requestJSON = content = request.body
        jsonObject = checkJson (content)
        data = validation_and_manipulation (jsonObject, apiName, InputDict)
        print 'data ', data
        if 'stat' in data:
            return Response (data)
        else:
            print 'after validate '
            json_data = json.dumps(data)
            public_key4 = import_key(public_key4_pem)
            jData = encrypt(json_data, public_key4, 2048)
            tomcat_count = get_tomcat_count(tomcat_count)
            user_id = global_user_id
            output = send_sequest(content, url, authorization, user_id, tomcat_count, jKey, jData)
            return Response(output)


@api_view([readProperty ('METHOD_TYPE')])
def get_order_history(request):
    if request.method == readProperty ('METHOD_TYPE'):
        url = ApiHomeDict.get(readProperty("ORDER_HISTORY"))[0].url
        apiName = readProperty ("ORDER_HISTORY")
        authorization = request.META.get('HTTP_AUTHORIZATION')
        authorization = authorization.split("-")
        public_key4_pem = b64_decode(authorization[1].replace("\n", ""))
        tomcat_count = b64_decode(authorization[2].replace("\n", ""))
        jKey = get_jkey(public_key4_pem)
        requestJSON = content = request.body
        jsonObject = checkJson (content)
        data = validation_and_manipulation (jsonObject, apiName, InputDict)
        print 'data ', data
        if 'stat' in data:
            return Response (data)
        else:
            print 'after validate '
            json_data = json.dumps(data)
            public_key4 = import_key(public_key4_pem)
            jData = encrypt(json_data, public_key4, 2048)
            tomcat_count = get_tomcat_count(tomcat_count)
            user_id = global_user_id
            output = send_sequest(content, url, authorization, user_id, tomcat_count, jKey, jData)
            return Response(output)


@api_view([readProperty('METHOD_TYPE')])
def get_trade_book(request):
    if request.method == readProperty ('METHOD_TYPE'):
        url = ApiHomeDict.get(readProperty("TRADE_BOOK"))[0].url
        apiName = readProperty ("TRADE_BOOK")
        authorization = request.META.get('HTTP_AUTHORIZATION')
        authorization = authorization.split("-")
        public_key4_pem = b64_decode(authorization[1].replace("\n", ""))
        tomcat_count = b64_decode(authorization[2].replace("\n", ""))
        jKey = get_jkey(public_key4_pem)
        requestJSON = content = request.body
        jsonObject = checkJson (content)
        data = validation_and_manipulation (jsonObject, apiName, InputDict)
        print 'data ', data
        if 'stat' in data:
            return Response (data)
        else:
            print 'after validate '
            json_data = json.dumps(data)
            public_key4 = import_key(public_key4_pem)
            jData = encrypt(json_data, public_key4, 2048)
            tomcat_count = get_tomcat_count(tomcat_count)
            user_id = global_user_id
            output = send_sequest(content, url, authorization, user_id, tomcat_count, jKey, jData)
            return Response(output)


@api_view([readProperty ('METHOD_TYPE')])
def get_holding(request):
    if request.method == readProperty ('METHOD_TYPE'):
        url = ApiHomeDict.get(readProperty("HOLDING"))[0].url
        apiName = readProperty ("HOLDING")
        authorization = request.META.get('HTTP_AUTHORIZATION')
        authorization = authorization.split("-")
        public_key4_pem = b64_decode(authorization[1].replace("\n", ""))
        tomcat_count = b64_decode(authorization[2].replace("\n", ""))
        jKey = get_jkey(public_key4_pem)
        requestJSON = content = request.body
        jsonObject = checkJson (content)
        data = validation_and_manipulation (jsonObject, apiName, InputDict)
        print 'data ', data
        if 'stat' in data:
            return Response (data)
        else:
            print 'after validate '
            json_data = json.dumps(data)
            public_key4 = import_key(public_key4_pem)
            jData = encrypt(json_data, public_key4, 2048)
            tomcat_count = get_tomcat_count(tomcat_count)
            user_id = global_user_id
            output = send_sequest(content, url, authorization, user_id, tomcat_count, jKey, jData)
            return Response(output)


@api_view([readProperty ('METHOD_TYPE')])
def get_limits(request):
    if request.method == readProperty ('METHOD_TYPE'):
        url = ApiHomeDict.get(readProperty("LIMITS"))[0].url
        apiName = readProperty ("LIMITS")
        authorization = request.META.get('HTTP_AUTHORIZATION')
        authorization = authorization.split("-")
        public_key4_pem = b64_decode(authorization[1].replace("\n", ""))
        tomcat_count = b64_decode(authorization[2].replace("\n", ""))
        jKey = get_jkey(public_key4_pem)
        requestJSON = content = request.body
        jsonObject = checkJson (content)
        data = validation_and_manipulation (jsonObject, apiName, InputDict)
        print 'data ', data
        if 'stat' in data:
            return Response (data)
        else:
            print 'after validate '
            json_data = json.dumps(data)
            public_key4 = import_key(public_key4_pem)
            jData = encrypt(json_data, public_key4, 2048)
            tomcat_count = get_tomcat_count(tomcat_count)
            user_id = global_user_id
            output = send_sequest(content, url, authorization, user_id, tomcat_count, jKey, jData)
            return Response(output)


@api_view([readProperty('METHOD_TYPE')])
def get_user_profile(request):
    if request.method == readProperty ('METHOD_TYPE'):
        url = ApiHomeDict.get(readProperty("USER_PROFILE"))[0].url
        apiName = readProperty ("USER_PROFILE")
        authorization = request.META.get('HTTP_AUTHORIZATION')
        authorization = authorization.split("-")
        public_key4_pem = b64_decode(authorization[1].replace("\n", ""))
        tomcat_count = b64_decode(authorization[2].replace("\n", ""))
        jKey = get_jkey(public_key4_pem)
        requestJSON = content = request.body
        jsonObject = checkJson (content)
        data = validation_and_manipulation (jsonObject, apiName, InputDict)
        print 'data ', data
        if 'stat' in data:
            return Response (data)
        else:
            print 'after validate '
            json_data = json.dumps(data)
            public_key4 = import_key(public_key4_pem)
            jData = encrypt(json_data, public_key4, 2048)
            tomcat_count = get_tomcat_count(tomcat_count)
            user_id = global_user_id
            output = send_sequest(content, url, authorization, user_id, tomcat_count, jKey, jData)
            return Response(output)


@api_view([readProperty('METHOD_TYPE')])
def get_account_info(request):
    if request.method ==readProperty ('METHOD_TYPE'):
        url = ApiHomeDict.get(readProperty("ACCOUNT_INFO"))[0].url
        apiName = readProperty ("ACCOUNT_INFO")
        authorization = request.META.get('HTTP_AUTHORIZATION')
        authorization = authorization.split("-")
        public_key4_pem = b64_decode(authorization[1].replace("\n", ""))
        tomcat_count = b64_decode(authorization[2].replace("\n", ""))
        jKey = get_jkey(public_key4_pem)
        requestJSON = content = request.body
        jsonObject = checkJson (content)
        data = validation_and_manipulation (jsonObject, apiName, InputDict)
        print 'data ', data
        if 'stat' in data:
            return Response (data)
        else:
            print 'after validate '
            json_data = json.dumps(data)
            public_key4 = import_key(public_key4_pem)
            jData = encrypt(json_data, public_key4, 2048)
            tomcat_count = get_tomcat_count(tomcat_count)
            user_id = global_user_id
            output = send_sequest(content, url, authorization, user_id, tomcat_count, jKey, jData)
            return Response(output)


@api_view([readProperty ('METHOD_TYPE')])
def get_open_orders(request):
    if request.method == readProperty ('METHOD_TYPE'):
        url = ApiHomeDict.get(readProperty("OPEN_ORDERS"))[0].url
        apiName = readProperty ("OPEN_ORDERS")
        authorization = request.META.get('HTTP_AUTHORIZATION')
        authorization = authorization.split("-")
        public_key4_pem = b64_decode(authorization[1].replace("\n", ""))
        tomcat_count = b64_decode(authorization[2].replace("\n", ""))
        jKey = get_jkey(public_key4_pem)
        requestJSON = content = request.body
        jsonObject = checkJson (content)
        data = validation_and_manipulation (jsonObject, apiName, InputDict)
        print 'data ', data
        if 'stat' in data:
            return Response (data)
        else:
            print 'after validate '
            json_data = json.dumps(data)
            public_key4 = import_key(public_key4_pem)
            jData = encrypt(json_data, public_key4, 2048)
            tomcat_count = get_tomcat_count(tomcat_count)
            user_id = global_user_id
            output = send_sequest(content, url, authorization, user_id, tomcat_count, jKey, jData)
            return Response(output)


@api_view([readProperty('METHOD_TYPE')])
def get_bo_holdings(request):
    if request.method ==readProperty ('METHOD_TYPE'):
        url = ApiHomeDict.get(readProperty("GET_PRE_AUTHENTICATION_KEY"))[0].url
        apiName = readProperty ("GET_PRE_AUTHENTICATION_KEY")
        authorization = request.META.get('HTTP_AUTHORIZATION')
        authorization = authorization.split("-")
        public_key4_pem = b64_decode(authorization[1].replace("\n", ""))
        tomcat_count = b64_decode(authorization[2].replace("\n", ""))
        jKey = get_jkey(public_key4_pem)
        requestJSON = content = request.body
        jsonObject = checkJson (content)
        data = validation_and_manipulation (jsonObject, apiName, InputDict)
        print 'data ', data
        if 'stat' in data:
            return Response (data)
        else:
            print 'after validate '
            json_data = json.dumps(data)
            public_key4 = import_key(public_key4_pem)
            jData = encrypt(json_data, public_key4, 2048)
            tomcat_count = get_tomcat_count(tomcat_count)
            user_id = global_user_id
            output = send_sequest(content, url, authorization, user_id, tomcat_count, jKey, jData)
            return Response(output)


@api_view([readProperty ('METHOD_TYPE')])
def get_bo_Ul_Trades(request):
    if request.method == readProperty ('METHOD_TYPE'):
        url = ApiHomeDict.get(readProperty("GET_PRE_AUTHENTICATION_KEY"))[0].url
        apiName = readProperty ("GET_PRE_AUTHENTICATION_KEY")
        authorization = request.META.get('HTTP_AUTHORIZATION')
        authorization = authorization.split("-")
        public_key4_pem = b64_decode(authorization[1].replace("\n", ""))
        tomcat_count = b64_decode(authorization[2].replace("\n", ""))
        jKey = get_jkey(public_key4_pem)
        requestJSON = content = request.body
        jsonObject = checkJson (content)
        data = validation_and_manipulation (jsonObject, apiName, InputDict)
        print 'data ', data
        if 'stat' in data:
            return Response (data)
        else:
            print 'after validate '
            json_data = json.dumps(data)
            public_key4 = import_key(public_key4_pem)
            jData = encrypt(json_data, public_key4, 2048)
            tomcat_count = get_tomcat_count(tomcat_count)
            user_id = global_user_id
            output = send_sequest(content, url, authorization, user_id, tomcat_count, jKey, jData)
            return Response(output)


@api_view([readProperty ('METHOD_TYPE')])
def get_logout(request):
    if request.method == readProperty ('METHOD_TYPE'):
        url = ApiHomeDict.get(readProperty("LOG_OUT"))[0].url
        apiName=readProperty("LOG_OUT")
        authorization = request.META.get('HTTP_AUTHORIZATION')
        authorization = authorization.split("-")
        public_key4_pem = b64_decode(authorization[1].replace("\n", ""))
        tomcat_count = b64_decode(authorization[2].replace("\n", ""))
        jKey = get_jkey(public_key4_pem)
        requestJSON = content = request.body
        jsonObject = checkJson (content)
        data = validation_and_manipulation (jsonObject, apiName, InputDict)
        print 'data ', data
        if 'stat' in data:
            return Response (data)
        else:
            print 'after validate '
            json_data = json.dumps(data)
            public_key4 = import_key(public_key4_pem)
            jData = encrypt(json_data, public_key4, 2048)
            tomcat_count = get_tomcat_count(tomcat_count)
            user_id = global_user_id
            output = send_sequest(content, url, authorization, user_id, tomcat_count, jKey, jData)
            return Response(output)





def validation_and_manipulation(jsonObject,apiName,InputDict):

    data={}
    data = validation_CheckInput (jsonObject, apiName, ApiHomeDict)
    if not data:
        data = validation_Parameter (jsonObject, apiName, InputDict)
    if not data:
        jsonObject = manipulation_Default (jsonObject, apiName, InputDict)
        data = validation_All (jsonObject, apiName, InputDict)
    if not data:
        jsonObject = manipulation_Transformation(jsonObject, apiName, InputDict)
        data=jsonObject
        print 'Actual Data'

    return data


def manipulation_Transformation(jsonObject, apiName, dict):
    if jsonObject:
        for param, value in jsonObject.items():
            transformation= dict.get(apiName).get(param)[0].transformation
            value = transformationValidation (transformation, value)
            jsonObject[param] = value
    return jsonObject


def manipulation_Default(jsonObject, apiName, dict):
    if jsonObject:
        for param, value in jsonObject.items():

            default= dict.get(apiName).get(param)[0].default
            value = defaultValidation (default, value)
            jsonObject[param]=value

    return jsonObject


def transformationValidation(transformation,Paramvalue):

    if isBlank(transformation):
        pass
    else:
        if isNotBlank(Paramvalue):
            transformation=ListDict.get(transformation).get(Paramvalue)[0].targetValue
            Paramvalue=transformation
        print 'transformation ', Paramvalue
    return Paramvalue

def defaultValidation(default,Paramvalue):

    if isBlank(default):
        pass
    else:
        Paramvalue=default

    return Paramvalue


def validation_CheckInput(jsonObject,apiName,Dict):
    data = {}
    Param = CheckInputBody (jsonObject, apiName, Dict)
    checkParam = Param[0]
    print checkParam
    errorParam = Param[1]
    print errorParam
    stat = Param[2]
    print stat
    if (checkParam == False):
        data = sendErrorRequesterror (errorParam, stat)
    return  data


def validation_Parameter(jsonObject,apiName,InputDict):
    data = {}
    if jsonObject:
        Param = CheckAllParameter (jsonObject, apiName, InputDict)
        checkParam = Param[0]
        print checkParam
        errorParam = Param[1]
        print errorParam
        stat = Param[2]
        print stat
        if (checkParam == False):
            data = sendErrorRequesterror (errorParam, stat)
    return  data


def validation_All(jsonObject,apiName,InputDict):
    data = {}
    if jsonObject:
        dataType = checkAll (jsonObject, apiName, InputDict)
        checkType = dataType[0]
        errorDataType = dataType[1]
        stat = dataType[2]
        if (checkType == False):
            data = sendErrorRequesterror (errorDataType, stat)
    return  data

def sendErrorRequesterror(errorList,stat):
    i=len(errorList)
    print i
    response_data = {}
    for v in errorList:

        response_data.setdefault(readProperty('ERROR_MSG'), [])
        response_data[readProperty('ERROR_MSG')].append(v)
        response_data[readProperty('STATUS')] = stat

    print 'response_data',response_data
    return response_data

def checkAll(content,ApiName,dict):
    check=True
    stat = ''
    errorMsg=''
    errorList=[]
    errorListAll=[]

    for param, value in content.items():
        dataType= dict.get(ApiName).get(param)[0].dataType
        validValues= dict.get(ApiName).get(param)[0].validValues
        optional= dict.get(ApiName).get(param)[0].optional

        errorList=dataTypeValidation(dataType,value,param)
        errorListAll.extend (errorList)
        errorList = ValidValuesValidation (validValues, value, param)
        errorListAll.extend (errorList)
        errorList = optionalValidation (optional, value, param)
        errorListAll.extend(errorList)

    if errorListAll:
        check = False
        stat  =readProperty('100')
    print errorListAll
    return check,errorListAll,stat



def ValidValuesValidation(validValues,Paramvalue,param):
    errorList = []
    errorMsg=''
    if isBlank(validValues):
        pass
    else:
        if isNotBlank(Paramvalue) and Paramvalue in validValues:
            pass
        else:
            errorMsg=param+" "+readProperty('104')+" "+validValues
            print errorMsg

    if errorMsg:
        errorList.append (errorMsg)
    return errorList


def optionalValidation(optional, Paramvalue, param):
    errorList = []
    errorMsg = ''
    if isBlank(optional):
        pass
    elif(optional == readProperty('YES')):
        if isBlank(Paramvalue):
             errorMsg = param + " " + readProperty ('105')
             print errorMsg

    if errorMsg:
        errorList.append (errorMsg)
    return errorList

def dataTypeValidation(dataType,Paramvalue,param):
    errorList = []
    errorMsg=''
    if (dataType == readProperty('STRING')):
        pass
    elif (dataType == readProperty('CHARACTER')):
        Valuelen = len(Paramvalue)
        if (Valuelen == 1):
            pass
        else:
            errorMsg=param+" "+readProperty('102')+" "+dataType
            print errorMsg
    elif(dataType == readProperty('NUMBER')):
        if(Paramvalue.isdigit()):
            pass
        else:
            errorMsg = param+" "+readProperty('102') + " " + dataType
            print errorMsg
    elif (dataType == readProperty('DECIMAL')):
        '''if (value.isdecimal()):
            pass
        else:
            errorMsg = param + " " + readProperty ('102') + " " + dataType
            print errorMsg'''
        splitNum=Paramvalue.split('.', 1)
        print splitNum[1].isdigit () and splitNum[0].isdigit ()
        if(splitNum[1].isdigit() and splitNum[0].isdigit ()):
            if (isinstance (json.loads (Paramvalue), (float))):
                pass
            else:
                errorMsg = param + " " + readProperty('102') + " " + dataType
                print 'hi1',errorMsg
        else:
            errorMsg = param + " " + readProperty('102') + " " + dataType
            print 'hi2',errorMsg

    elif (dataType == readProperty('LIST')):
        print type (Paramvalue)
        print type(Paramvalue) is list
        if type(Paramvalue) is list:
            pass
        else:
            errorMsg = param + " " +readProperty('102') + " " + dataType
            print errorMsg

    elif (dataType == readProperty('DATE_TIME')):
        print type (Paramvalue)
        timestamp = time.strftime ('%m/%d/%Y/%w/%H:%M:%S')
        Date=validateDate (Paramvalue)
        print Date
        print timestamp
        if Date:
            pass
        else:
            errorMsg = param + " " +readProperty('103') + " " + dataType
            print errorMsg

    # SSBOETOD need write
    if errorMsg:
        errorList.append (errorMsg)
    return errorList

def validateDate(date_text):

    try:
        time.strptime(date_text, '%m/%d/%Y/%w/%H:%M:%S')
        Date = True
    except ValueError:
        Date = False
    return Date

def CheckAllParameter(content,ApiName,dict):
    check=True
    #print dict.get(ApiName).get('jData')[0].description
    errorList=[]
    expectList=[]
    expectMsg=''
    stat = ''
    for k, v in dict.items():
        if k == ApiName:
            for k1, v1 in v.items():
                for v2 in v1:
                    b = v2.parameter
                    expectList.append(b)
    expectLen=len (expectList)
    contentLen=len (content)
    for param, v in content.items():

        if (param in expectList):
            pass
        else:
            errorList.append(readProperty('101') + " " + param)
            check = False
    if(expectLen!=contentLen):
        expectMsg="Expected "+str(expectLen)+" parameter available "+str(contentLen)+" parameter"
        errorList.append(expectMsg)
        check = False
    if errorList:
        stat = readProperty('100')
    print errorList
    print 'stat ',stat
    return check,errorList,stat

def CheckInputBody(content,ApiName,dict):
    check=True
    print dict.get(ApiName)[0].inputApi
    errorList=[]
    expectMsg=''
    stat = ''
    checkBody=dict.get (ApiName)[0].inputApi
    if checkBody==readProperty('CAPITAL_YES'):
        if content:
            pass
        else:
            print 'No'
            errorList.append(readProperty('106'))
            check = False
    else:
        if content:
            print 'No'
            errorList.append (readProperty ('107'))
            check = False
        else:
            pass

    if errorList:
        stat = readProperty('100')
    print errorList
    print 'stat ',stat
    return check,errorList,stat






def password_hash(password):
    for num in range(0, 999):
        password = hashlib.sha256(password).digest()
    password_hash = hashlib.sha256(password).hexdigest()
    return password_hash


def send_sequest(body_content, url, authorization, user_id, tomcat_count, jKey, jData):
    if isNotBlank(body_content):
        jsession_id = get_jsessionid(user_id)
        tomcat_count = get_tomcat_count(tomcat_count)
        if isNotBlank(jsession_id):
            url = url + "?jsessionid=" + jsession_id.strip()
        if isNotBlank(tomcat_count):
            url = url + "." + tomcat_count.strip()
        print "url="+url
        values = {'jKey': jKey,
                  'jData': jData}
        data = urllib.urlencode(values)
        req = urllib2.Request(url, data)
        response = urllib2.urlopen(req)
        the_page = response.read()
        d = json.loads(the_page)
        return d
    else:
        resp = requests.post(url)
        return resp.text


def get_cipher(key):
    cipher = PKCS1_v1_5.new(key)
    return cipher


def encrypt_block(key, data, start, end):
    data = data[start:end]
    cipher = get_cipher(key)
    encrypted_data = cipher.encrypt(data)
    encoded_data = b64_encode(encrypted_data)
    replace_data = replace_text(encoded_data, "\n", "")
    return replace_data


def encrypt(data, key, key_size):
    buffer = ""
    number_of_bytes = ((key_size / BYTE_BOUNDARY) - 11)
    start = 0
    end = number_of_bytes
    if (number_of_bytes > len(data)):
        end = len(data)
    buffer = buffer + encrypt_block(key, data, start, end)
    buffer = append_data(buffer, "\n")
    start = end
    end += number_of_bytes
    if (end > len(data)):
        end = len(data)

    while (end < len(data)):
        buffer = buffer + encrypt_block(key, data, start, end)
        buffer = append_data(buffer, "\n")
        start = end
        end += number_of_bytes
        if (end > len(data)):
            end = len(data)
    if (end - start > 0):
        buffer = buffer + encrypt_block(key, data, start, end)
        buffer = append_data(buffer, "\n")
    buffer = b64_encode(buffer)
    buffer = replace_text(buffer, "\n", "")
    return buffer


def replace_text(orginal_data, old_text, new_text):
    orginal_data = orginal_data.replace(old_text, new_text)
    return orginal_data


def append_data(original_text, append_text):
    original_text = original_text + append_text
    return original_text


def decrypt(data, private_key):
    data = b64_decode(data)
    data = unicode(data, "utf-8")
    data = data.strip().split("\n")
    final_data = ""
    for temp_data in data:
        temp_data = b64_decode(temp_data)
        cipher = get_cipher(private_key)
        temp_data = cipher.decrypt(temp_data, 'utf-8')
        final_data = append_data(final_data, temp_data)
    return final_data


def b64_decode(data):
    decoded_data = base64.b64decode(data)
    return decoded_data


def b64_encode(data):
    encoded_data = data.encode("base64")
    return encoded_data


def generate_key_pair():
    random_generator = Random.new().read
    key = RSA.generate(2048, random_generator)
    return key


def get_public_key_pem(key):
    publicKey2_PEM = key.publickey().exportKey("PEM")
    return publicKey2_PEM


def get_private_key_pem(key):
    privateKey2_PEM = key.exportKey()
    return privateKey2_PEM


def import_key(key_pem):
    key = RSA.importKey(key_pem)
    # cipher = PKCS1_v1_5.new(key)
    return key


def get_jkey(decoded_public_key):
    hash_object = hashlib.sha256(decoded_public_key)
    jKey = hash_object.hexdigest()
    return jKey


def get_jsessionid(user_id):
    jSessionId = b64_encode(user_id)
    return jSessionId


def get_tomcat_count(tomcat_count):
    # tomcat_count=''
    return tomcat_count


def decrtpt_data():
    encrypted_data = ''
    return encrypted_data;


def data_type(data, datatype):
    return ''


def valid_values(data, valid_values):
    return ''


def optional(data, is_optional):
    return ''


def default(data, is_default):
    return ''


def transformation(data, transform_value):
    return ''


def isBlank(myString):
    if myString and myString.strip():
        # myString is not None AND myString is not empty or blank
        return False
    # myString is None OR myString is empty or blank
    return True


def isNotBlank(myString):
    if myString and myString.strip():
        # myString is not None AND myString is not empty or blank
        return True
    # myString is None OR myString is empty or blank
    return False

def checkJson(text):
    try:
        return json.loads(text)
    except ValueError as e:
        print('invalid json: %s' % e)
        return text # or: raise

def PasswordHash(jsonObject):
    data={}
    for key in jsonObject:
        value = jsonObject[key]
        if key == readProperty ('PASSWORD'):
            value = password_hash (value)
        data[key] = value
    return data