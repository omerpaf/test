
from django import template
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, HttpResponseRedirect
from django.template import loader
from django.urls import reverse
from functools import reduce

from django.core.files.storage import FileSystemStorage
from scipy import stats

from .models import CDR, Cases, CDRList, BTSList, BTS
from .forms import CasesForm

import csv
import pandas as pd
import numpy as np

from django.shortcuts import render

from django.http import JsonResponse
from django import forms

from datetime import datetime
from django.db.models import Count

import re
from .utils import BulkCreateManager, download_csv

from subprocess import Popen

count = 0;

def uploadcsv(request):
    print('Data analysis')
    
    if not 'c_id' in request.POST:
        if request.method == 'POST' and request.FILES['myfile'] and request.POST['case_id']:
            # try:
            myfile = request.FILES['myfile']
            filename = myfile.name
            n = myfile.name
            fileext = ".csv"
            print(filename)
            if filename.endswith('.csv'):
                fileext = "csv"
                print('File is a csv')
            elif filename.endswith('.xlsx'):
                fileext = "exel"
                print('File is a exel')
            elif filename.endswith('.txt'):
                fileext = "text"
                print('File is a text')
            else:
                print('File is invalid')

            case_id = request.POST['case_id']
            print('\nWhat is `myfile`?')
            print(type(myfile))

            print('\nDirectly accessing `myfile` gives nothing :(')
            print(type(str(myfile.read())))
            print(str(myfile.read()))

            fs = FileSystemStorage()
            filename = fs.save("csvfiles/"+myfile.name, myfile)
            print('\nHowever, when using FileSystemStorage...')
            print('\nReading filename: %s' % filename)
            print(type(fs.open(filename)))
            print(fs.open(filename))

            print('\nOpen and preview using pandas:')
            df = pd.DataFrame(columns=['A']);
            if filename.endswith('.csv'):
                df = pd.read_csv(fs.open(filename), error_bad_lines=False,encoding="utf-8",index_col=False)
            if filename.endswith('.xlsx') or filename.endswith('.xlsv') or filename.endswith('.xls'):
                df = pd.read_excel(fs.open(filename))
            if filename.endswith('.txt'):
                df = pd.read_csv(fs.open(filename), delimiter = "\t")
            print(df)

            #getting case id
            cc = Cases.objects.get(id=case_id)
            print(cc.id)

            #check the operator by first column
            op = "jazz"
            colname = df.columns[0]



            #jazz 1
            if(colname == "CallType"):
                jazz1(df,case_id,n)
            #jazz 2
            if(colname == "Sr #"):
                jazz2(df,case_id,n)
            #zong
            if(colname == "CALL_TYPE"):
                zong1(df,case_id,n)
            #ufone
            if(colname == "IMSI"):
                ufone1(df,case_id,n)

            #ufone
            if(colname == "IMEI"):
                ufone2(df,case_id,n)

            #warid
            if(colname == "SUBNO"):
                warid(df,case_id,n)

            #telenor
            if(colname == "MSISDN"):
                if 'call_org_num' in df.columns:
                    telenor2(df,case_id,n)
                else:
                    telenor(df,case_id,n)

            #return render(request, 'home/uploadcsv.html',{'result_present': True,'df': df.to_html()})
            context ={}
            #return render(request, "home/cdrlist.html", context)
            # add the dictionary during initialization
            #context["dataset"] = CDR.objects.all()
            return JsonResponse({'responseText':'success',"caseid":cc.id})
            # except:
            # context ={}
     
            # add the dictionary during initialization
            #context["dataset"] = CDR.objects.all()
            # return JsonResponse({'responseText':'error',"caseid":cc.id,"error":"Error processing data."})
        #return render(request, "home/cdrlist.html", context)
    else:
        context ={}
        context["dataset"] = request.POST['c_id']

        return render(request, 'home/uploadcsv.html', context)
    context ={}
 
    # add the dictionary during initialization
    context["dataset"] = request.GET['id']
    
    return render(request, 'home/uploadcsv.html', context)
    #return JsonResponse({'data':'Error!'})

#multiple cdr file upload function
def up(request):
    print('Data analysis multi')
    
    if not 'c_id' in request.POST:
        if request.method == 'POST' and request.FILES['myfiles'] and request.POST['case_id']:
            type(request.FILES['myfiles'])
            for count, x in enumerate(request.FILES.getlist("myfiles")):
                myfile = x
                print("heloooooooooooo"+str(count))
                filename = myfile.name
                n = myfile.name
                fileext = ""
                print(filename)
                if filename.endswith('.csv'):
                    fileext = "csv"
                    print('File is a csv')
                elif filename.endswith('.xlsx') or filename.endswith('.xlsv') or filename.endswith('.xls'):
                    fileext = "exel"
                    print('File is a exel')
                elif filename.endswith('.txt'):
                    fileext = "text"
                    print('File is a text')
                else:
                    print('File is invalid')

                case_id = request.POST['case_id']
                print('\nWhat is `myfile`?')
                print(type(myfile))

                print('\nDirectly accessing `myfile` gives nothing :(')
                print(type(str(myfile.read())))
                print(str(myfile.read()))

                fs = FileSystemStorage()
                filename = fs.save("csvfiles/"+myfile.name, myfile)
                print('\nHowever, when using FileSystemStorage...')
                print('\nReading filename: %s' % filename)
                print(type(fs.open(filename)))
                print(fs.open(filename))

                print('\nOpen and preview using pandas:')
                df = pd.DataFrame(columns=['A']);
                if filename.endswith('.csv'):
                    df = pd.read_csv(fs.open(filename),error_bad_lines=False,encoding="utf-8",index_col=False)
                if filename.endswith('.xlsx') or filename.endswith('.xlsv') or filename.endswith('.xls'):
                    df = pd.read_excel(fs.open(filename))
                if filename.endswith('.txt'):
                    df = pd.read_csv(fs.open(filename), delimiter = "\t")
                print(df)

                #getting case id
                cc = Cases.objects.get(id=case_id)
                print(cc.id)

                #check the operator by first column
                op = "jazz"
                colname = df.columns[0]



                #jazz 1
                if(colname == "CallType"):
                    jazz1(df,case_id,n)
                #jazz 2
                if(colname == "Sr #"):
                    jazz2(df,case_id,n)
                #zong
                if(colname == "CALL_TYPE"):
                    zong1(df,case_id,n)
                #ufone
                if(colname == "IMSI"):
                    ufone1(df,case_id,n)

                #ufone
                if(colname == "IMEI"):
                    ufone2(df,case_id,n)
                #warid
                if(colname == "SUBNO"):
                    warid(df,case_id,n)

                #telenor
                if(colname == "MSISDN"):
                    if 'call_org_num' in df.columns:
                        telenor2(df,case_id,n)
                    else:
                        telenor(df,case_id,n)

                #return render(request, 'home/uploadcsv.html',{'result_present': True,'df': df.to_html()})
            context ={}
            context["dataset"] = CDRList.objects.filter(caseid=cc.id)
            
            return render(request, "home/cdrreflist.html", context)
         
                # add the dictionary during initialization
                #context["dataset"] = CDR.objects.all()
           # return JsonResponse({'responseText':'success',"caseid":cc.id})
        #return render(request, "home/cdrlist.html", context)
    else:
        context ={}
        context["dataset"] = request.POST['c_id']
        return render(request, 'home/uploadcsv.html', context)
    context ={}
 
    # add the dictionary during initialization
    context["dataset"] = request.GET['id']
    
    return render(request, 'home/uploadcsv.html', context)

#multiple cdr file upload function
def multibts(request):
    print('bts multi')
    
    if not 'c_id' in request.POST:
        if request.method == 'POST' and request.FILES['mybtsfiles'] and request.POST['case_id']:
            type(request.FILES['mybtsfiles'])
            for count, x in enumerate(request.FILES.getlist("mybtsfiles")):
                myfile = x
                print("heloooooooooooo bts"+str(count))
                filename = myfile.name
                n = myfile.name
                fileext = ""
                print(filename)
                if filename.endswith('.csv'):
                    fileext = "csv"
                    print('File is a csv')
                elif filename.endswith('.xlsx') or filename.endswith('.xlsv') or filename.endswith('.xls'):
                    fileext = "exel"
                    print('File is a exel')
                elif filename.endswith('.txt'):
                    fileext = "text"
                    print('File is a text')
                else:
                    print('File is invalid')

                case_id = request.POST['case_id']
                print('\nWhat is `myfile`?')
                print(type(myfile))

                print('\nDirectly accessing `myfile` gives nothing :(')
                print(type(str(myfile.read())))
                print(str(myfile.read()))

                fs = FileSystemStorage()
                filename = fs.save("csvfiles/"+myfile.name, myfile)
                print('\nHowever, when using FileSystemStorage...')
                print('\nReading filename: %s' % filename)
                print(type(fs.open(filename)))
                print(fs.open(filename))

                print('\nOpen and preview using pandas:')
                df = pd.DataFrame(columns=['A']);
                if filename.endswith('.csv'):
                    df = pd.read_csv(fs.open(filename), error_bad_lines=False,encoding="utf-8",index_col=False)
                if filename.endswith('.xlsx') or filename.endswith('.xlsv') or filename.endswith('.xls'):
                    df = pd.read_excel(fs.open(filename))
                if filename.endswith('.txt'):
                    df = pd.read_csv(fs.open(filename), delimiter = "\t")
                print(df)

                #getting case id
                cc = Cases.objects.get(id=case_id)
                print(cc.id)

                #check the operator by first column
                op = "jazz"
                colname = df.columns[0]



                if(colname == "Sr #"):
                    btsjazz1(df,case_id,n)
                #zong
                if(colname == "DLD_NO"):
                    btszong1(df,case_id,n)

                #zong
                if(colname == "CALL_TYPE"):
                    btszong2(df,case_id,n)
                #ufone
                if(colname == "CALL_START_DT"):
                    btsufone1(df,case_id,n)

                #ufone
                if(colname == "IMEI"):
                    btsufone2(df,case_id,n)

                 #telenor
                if(colname == "MSISDN"):
                    if 'call_org_num' in df.columns:
                        btstelenor2(df,case_id,n)
                    else:
                        btstelenor1(df,case_id,n)

                #telenor 3
                if(colname == "CALL_DATE"):
                    btstelenor3(df,case_id,n)

                #return render(request, 'home/uploadcsv.html',{'result_present': True,'df': df.to_html()})
            context ={}
            context["dataset"] = BTSList.objects.filter(caseid=cc.id)
            
            return render(request, "home/btsreflist.html", context)
         
                # add the dictionary during initialization
                #context["dataset"] = CDR.objects.all()
           # return JsonResponse({'responseText':'success',"caseid":cc.id})
        #return render(request, "home/cdrlist.html", context)
    else:
        context ={}
        context["dataset"] = request.POST['c_id']
        return render(request, 'home/adbts.html', context)
    context ={}
 
    # add the dictionary during initialization
    context["dataset"] = request.GET['id']
    
    return render(request, 'home/adbts.html', context)

def commoncase(request):
    now = datetime.now()
    dt_string = now.strftime("%d-%m-%Y%H-%M-%S")
    print(request.POST)
    cid = request.POST['ct_id1']
    cid2 = request.POST['ct_id2']
    print("heloo"+cid)
    print("hi"+cid2)
    r = request.POST['relation']
    print(r)

    if(r=="aa"):

    # for first case id
        #for cdr
        cdr = CDR.objects.filter(caseid=cid)
        dfcdr = pd.DataFrame.from_records(cdr.values())
        if(not dfcdr.empty):
            dfcdr = dfcdr.replace('', np.nan)

        #for bts
        bts = BTS.objects.filter(caseid=cid)
        dfbts = pd.DataFrame.from_records(bts.values())
        if(not dfbts.empty):
            dfbts = dfbts.replace('', np.nan)

        grand_df_1 = dfcdr.append(dfbts)

    # for second case id
        #for cdr
        cdr2 = CDR.objects.filter(caseid=cid2)
        dfcdr2 = pd.DataFrame.from_records(cdr2.values())
        if(not dfcdr2.empty):
            dfcdr2 = dfcdr2.replace('', np.nan)

        #for bts
        bts2 = BTS.objects.filter(caseid=cid2)
        dfbts2 = pd.DataFrame.from_records(bts2.values())
        if(not dfbts2.empty):
            dfbts2 = dfbts2.replace('', np.nan)

        grand_df_2 = dfcdr2.append(dfbts2)

        print(grand_df_1)
        
        print("jcghvjh")

        print(grand_df_2)

        x = list(reduce(set.intersection, map(set, [grand_df_1.aparty, grand_df_2.aparty])))

        d3 = pd.DataFrame(x,columns=["common numbers"])

        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename=ApartyToAparty.csv'  # alter as needed
        d3.to_csv(path_or_buf=response)  # with other applicable parameters
        return response

    if(r=="ab"):

    # for first case id
        #for cdr
        cdr = CDR.objects.filter(caseid=cid)
        dfcdr = pd.DataFrame.from_records(cdr.values())
        if(not dfcdr.empty):
            dfcdr = dfcdr.replace('', np.nan)

        #for bts
        bts = BTS.objects.filter(caseid=cid)
        dfbts = pd.DataFrame.from_records(bts.values())
        if(not dfbts.empty):
            dfbts = dfbts.replace('', np.nan)

        grand_df_1 = dfcdr.append(dfbts)

    # for second case id
        #for cdr
        cdr2 = CDR.objects.filter(caseid=cid2)
        dfcdr2 = pd.DataFrame.from_records(cdr2.values())
        if(not dfcdr2.empty):
            dfcdr2 = dfcdr2.replace('', np.nan)

        #for bts
        bts2 = BTS.objects.filter(caseid=cid2)
        dfbts2 = pd.DataFrame.from_records(bts2.values())
        if(not dfbts2.empty):
            dfbts2 = dfbts2.replace('', np.nan)

        grand_df_2 = dfcdr2.append(dfbts2)

        print(grand_df_1)
        
        print("jcghvjh")

        print(grand_df_2)

        x = list(reduce(set.intersection, map(set, [grand_df_1.aparty, grand_df_2.bparty])))

        d3 = pd.DataFrame(x,columns=["aparty"])

        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename=ApartyToBparty.csv'  # alter as needed
        d3.to_csv(path_or_buf=response)  # with other applicable parameters
        return response

    if(r=="bb"):

    # for first case id
        #for cdr
        cdr = CDR.objects.filter(caseid=cid)
        dfcdr = pd.DataFrame.from_records(cdr.values())
        if(not dfcdr.empty):
            dfcdr = dfcdr.replace('', np.nan)

        #for bts
        bts = BTS.objects.filter(caseid=cid)
        dfbts = pd.DataFrame.from_records(bts.values())
        if(not dfbts.empty):
            dfbts = dfbts.replace('', np.nan)

        grand_df_1 = dfcdr.append(dfbts)

    # for second case id
        #for cdr
        cdr2 = CDR.objects.filter(caseid=cid2)
        dfcdr2 = pd.DataFrame.from_records(cdr2.values())
        if(not dfcdr2.empty):
            dfcdr2 = dfcdr2.replace('', np.nan)

        #for bts
        bts2 = BTS.objects.filter(caseid=cid2)
        dfbts2 = pd.DataFrame.from_records(bts2.values())
        if(not dfbts2.empty):
            dfbts2 = dfbts2.replace('', np.nan)

        grand_df_2 = dfcdr2.append(dfbts2)

        print(grand_df_1)
        
        print("jcghvjh")

        print(grand_df_2)

        x = list(reduce(set.intersection, map(set, [grand_df_1.bparty, grand_df_2.bparty])))

        d3 = pd.DataFrame(x,columns=["aparty"])

        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename=BpartyToBparty.csv'  # alter as needed
        d3.to_csv(path_or_buf=response)  # with other applicable parameters
        return response


        # download_csv(request, d3)

    context ={}
    if request.user.groups.filter(name = "admins").exists():
        context["dataset"] = Cases.objects.all()
    else:
        context["dataset"] = Cases.objects.all()
        #context["dataset"] = Cases.objects.filter(user=request.user)
         
    return render(request, "home/commoncaselist.html", context)


    # Create the HttpResponse object with the appropriate CSV header.
    # data = download_csv(request, Cases.objects.filter(id=cid))
    # data = download_csv(request, CDR.objects.filter(caseid=cid))





def transformcase(request):
    now = datetime.now()
    dt_string = now.strftime("%d-%m-%Y%H-%M-%S")
    print(request.POST)
    cid = request.POST['ca_id']
    print(cid)

#for cases
    case = Cases.objects.filter(id=cid)
    df = pd.DataFrame.from_records(case.values())

    # df = pd.DataFrame(case,columns={'id','casetype',"fir","ps","telco","voip","complaintcaste","modusoperandus","casetitle"
    #     ,"casedate","region","internationalno","coplaintname","profession","incidentdate","firreference","us","localno","country","complaintno","groupclaim"
    #     ,"incidenttime","createdat","user","incident_ps_jurisdiction","demand_amount","victim_reference","victim","io","remarks"})

    df = df[[ 'id','casetype', 'casetitle', 'fir','firreference', 'casedate','us',"ps","region","localno","telco","internationalno","country","voip",
    "coplaintname","complaintno","complaintcaste","profession","groupclaim","modusoperandus","incidentdate","incidenttime","incident_place",
    "incident_ps_jurisdiction","demand_amount","victim_reference","victim","io","remarks"]]
    

    df['casedate'] = pd.to_datetime(df['casedate'])
   
    df['incidentdate'] = pd.to_datetime(df['incidentdate'])
  
    print(df)

    df.rename(columns={'id':"cases_id",'casetype':"case_type", 'casetitle':"case_title", 'fir':"reference_type_fir",'firreference':"reference_fir", 'casedate':"c_dt",
        "localno":"local_demand_nbr","telco":"company","internationalno":"international_nbr",
    "coplaintname":"complainant_case","complaintno":"complainant_no","complaintcaste":"complainant_caste","profession":"profession_comp",
    "groupclaim":"group_claim","modusoperandus":"modus_operandi","incidentdate":"incident_dt","incidenttime":"incident_time",}, inplace=True)
    #cases_id   case_type   case_title  reference_type_fir  reference_fir   c_dt    us  ps  region  local_demand_nbr    company international_nbr   country voip
    #    complainant_case    complainant_no  complainant_caste   profession_comp group_claim modus_operandi  incident_dt incident_time   incident_place 
    # incident_ps_jurisdiction    demand_amount   victim_reference    victim  io  remarks
    nnn = "C:/cdr/cases-"+cid+dt_string+".tsv"
    df.to_csv(nnn,sep="\t",index=False, header=False)


#for cdr
    cdr = CDR.objects.filter(caseid=cid)
    dfcdr = pd.DataFrame.from_records(cdr.values())
    if(not dfcdr.empty):
        dfcdr = dfcdr.replace('', np.nan)
        # df = pd.DataFrame(case,columns={'id','casetype',"fir","ps","telco","voip","complaintcaste","modusoperandus","casetitle"
        #     ,"casedate","region","internationalno","coplaintname","profession","incidentdate","firreference","us","localno","country","complaintno","groupclaim"
        #     ,"incidenttime","createdat","user","incident_ps_jurisdiction","demand_amount","victim_reference","victim","io","remarks"})
        #aparty,bparty,"telenor",ts,duration,cellid,Imei,Imsi,calltype,direction,filextt,sitelocation,cc.id, cc.createdat,source,destination
        dfcdr["cid"] = case[0].id
        dfcdr["casedate"] = case[0].createdat
        dfcdr["filextt"] = "CDR"
        dfcdr["description"] = pd.NaT
        dfcdr["lat_lng"] = pd.NaT
        
        
        dfcdr = dfcdr[[ "id","aparty","bparty","operator","ts","duration","cellid","imei","imsi","calltype","direction","filextt","SiteAddress","cid","description", "casedate","lat_lng","source","destination"]]
     
        if(type(dfcdr["source"]) ==str):
            dfcdr["lat_lng"] = dfcdr["source"]+";"+dfcdr["destination"]
        else:
            dfcdr["lat_lng"] = dfcdr["source"].astype(str)+";"+dfcdr["destination"].astype(str)

        dfcdr["source"] = dfcdr["lat_lng"]
        dfcdr['destination'] = dfcdr['source'].shift(-1)
       

        dfcdr.rename(columns={"cellid":"lac_cellid","calltype":"call_type","filextt":"filetype","SiteAddress":"site_address","cid":"CDR_id",
            "casedate":"cdr_dt"}, inplace=True)

    #for bts
    bts = BTS.objects.filter(caseid=cid)
    dfbts = pd.DataFrame.from_records(bts.values())
    if(not dfbts.empty):
        dfbts = dfbts.replace('', np.nan)
        # df = pd.DataFrame(case,columns={'id','casetype',"fir","ps","telco","voip","complaintcaste","modusoperandus","casetitle"
        #     ,"casedate","region","internationalno","coplaintname","profession","incidentdate","firreference","us","localno","country","complaintno","groupclaim"
        #     ,"incidenttime","createdat","user","incident_ps_jurisdiction","demand_amount","victim_reference","victim","io","remarks"})
        #aparty,bparty,"telenor",ts,duration,cellid,Imei,Imsi,calltype,direction,filextt,sitelocation,cc.id, cc.createdat,source,destination
        dfbts["cid"] = case[0].id
        dfbts["casedate"] = case[0].createdat
        dfbts["filextt"] = "BTS"
        dfbts["description"] = pd.NaT
        dfbts["lat_lng"] = pd.NaT
        

        dfbts = dfbts[[ "id","aparty","bparty","operator","ts","duration","cellid","imei","imsi","calltype","direction","filextt","SiteAddress","cid","description", "casedate","lat_lng","source","destination"]]
        

        if(type(dfbts["source"]) ==str):
            dfbts["lat_lng"] = dfbts["source"]+";"+dfbts["destination"]
        else:
            dfbts["lat_lng"] = dfbts["source"].astype(str)+";"+dfbts["destination"].astype(str)

        dfbts["source"] = dfbts["lat_lng"]
        dfbts['destination'] = dfbts['source'].shift(-1)

        dfbts.rename(columns={"cellid":"lac_cellid","calltype":"call_type","filextt":"filetype","SiteAddress":"site_address","cid":"CDR_id",
            "casedate":"cdr_dt"}, inplace=True)


    grand_df = dfcdr.append(dfbts)

    #id aparty  bparty  operator    ts  duration    lac_cellid  imei    imsi    call_type   direction   filetype    site_address    CDR_id  description cdr_dt  lat_lng source  destination

    # df.rename(columns={'id':"cases_id",'casetype':"case_type", 'casetitle':"case_title", 'fir':"reference_type_fir",'firreference':"reference_fir", 'casedate':"c_dt",
    #     "localno":"local_demand_nbr","telco":"company","internationalno":"international_nbr",
    # "coplaintname":"complainant_case","complaintno":"complainant_no","complaintcaste":"complainant_caste","profession":"profession_comp",
    # "groupclaim":"group_claim","modusoperandus":"modus_operandi","incidentdate":"incident_dt","incidenttime":"incident_time",}, inplace=True)
    #cases_id   case_type   case_title  reference_type_fir  reference_fir   c_dt    us  ps  region  local_demand_nbr    company international_nbr   country voip
    #    complainant_case    complainant_no  complainant_caste   profession_comp group_claim modus_operandi  incident_dt incident_time   incident_place 
    # incident_ps_jurisdiction    demand_amount   victim_reference    victim  io  remarks
    nnn = "C:/cdr/cdr-"+cid+dt_string+".tsv"
    #grand_df.to_csv(nnn,sep="\t",index=False, header=False)

    grand_df.to_csv(nnn,sep="\t",index=False, header=False)

    p = Popen("C:/cdr/main.bat", shell=True)
    stdout, stderr = p.communicate()

    print(p.returncode)


    context ={}
    if request.user.groups.filter(name = "admins").exists():
        context["dataset"] = Cases.objects.all()
    else:
        context["dataset"] = Cases.objects.all()
        #context["dataset"] = Cases.objects.filter(user=request.user)
         
    return render(request, "home/caselist.html", context)


    # Create the HttpResponse object with the appropriate CSV header.
    # data = download_csv(request, Cases.objects.filter(id=cid))
    # data = download_csv(request, CDR.objects.filter(caseid=cid))


    

def adbts(request):
    print('add bts function')
    if not 'c_id' in request.POST:
        if request.method == 'POST' and request.FILES['mybtsfile'] and request.POST['case_id']:
            myfile = request.FILES['mybtsfile']
            filename = myfile.name
            n = myfile.name
            fileext = ".csv"
            print(filename)
            if filename.endswith('.csv'):
                fileext = "csv"
                print('File is a csv')
            elif filename.endswith('.xlsx') or filename.endswith('.xlsv') or filename.endswith('.xls') :
                fileext = "exel"
                print('File is a exel')
            elif filename.endswith('.txt'):
                fileext = "text"
                print('File is a text')
            else:
                print('File is invalid')


            case_id = request.POST['case_id']
            print('\nWhat is `myfile`?')
            print(type(myfile))

            print('\nDirectly accessing `myfile` gives nothing :(')
            print(type(str(myfile.read())))
            print(str(myfile.read()))

            fs = FileSystemStorage()
            filename = fs.save("csvfiles/"+myfile.name, myfile)
            print('\nHowever, when using FileSystemStorage...')
            print('\nReading filename: %s' % filename)
            print(type(fs.open(filename)))
            print(fs.open(filename))

            print('\nOpen and preview using pandas:')
            df = pd.NaT;
            if filename.endswith('.csv'):
                df = pd.read_csv(fs.open(filename), error_bad_lines=False,encoding="utf-8",index_col=False)
            if filename.endswith('.xlsx') or filename.endswith('.xls'):
                df = pd.read_excel(fs.open(filename))
            if filename.endswith('.txt'):
                df = pd.read_csv(fs.open(filename), delimiter = "\t")
            print(df)

            #getting case id
            cc = Cases.objects.get(id=case_id)
            print(cc.id)

            #check the operator by first column
            op = "jazz"
            colname = df.columns[0]



            # #jazz 1
            # if(colname == "CallType"):
            #     btsjazz1(df,case_id)
            # #jazz 2
            if(colname == "Sr #"):
                btsjazz1(df,case_id,n)
            #zong
            if(colname == "DLD_NO"):
                btszong1(df,case_id,n)
            #zong
            if(colname == "CALL_TYPE"):
                btszong2(df,case_id,n)
            #ufone
            if(colname == "CALL_START_DT"):
                btsufone1(df,case_id,n)

            #ufone
            if(colname == "IMEI"):
                btsufone2(df,case_id,n)

            # #warid
            # if(colname == "SUBNO"):
            #     warid(df,case_id)

            #telenor
            if(colname == "MSISDN"):
                if 'call_org_num' in df.columns:
                    btstelenor2(df,case_id,n) 
                else:
                    btstelenor1(df,case_id,n)

            #telenor 3
            if(colname == "CALL_DATE"):
                btstelenor3(df,case_id,n)



            #return render(request, 'home/uploadcsv.html',{'result_present': True,'df': df.to_html()})
            context ={}
            context["dataset"] = BTSList.objects.filter(caseid=cc.id)
            
            #return render(request, "home/btsreflist.html", context)
            return JsonResponse({'responseText':'success',"caseid":cc.id})
        #return render(request, "home/cdrlist.html", context)
    else:
        context ={}
        context["dataset"] = request.POST['c_id']
        return render(request, 'home/addbts.html', context)
    context ={}
 
    # add the dictionary during initialization
    context["dataset"] = request.GET['id']
    
    return render(request, 'home/addbts.html', context)
    #return JsonResponse({'data':'Error!'})
    
def bulkcaseupload(request):
    #delete
    print("bulk case upload")

    if request.method == 'POST' and request.FILES['bulkcasefile'] :
        myfile = request.FILES['bulkcasefile']
        filename = myfile.name
        n = myfile.name
        fileext = ".csv"
        print(filename)
        if filename.endswith('.csv'):
            fileext = "csv"
            print('File is a csv')
        elif filename.endswith('.xlsx') or filename.endswith('.xlsv') or filename.endswith('.xls') :
            fileext = "exel"
            print('File is a exel')
        elif filename.endswith('.txt'):
            fileext = "text"
            print('File is a text')
        else:
            print('File is invalid')


        case_id = request.POST['case_id']
        print('\nWhat is `myfile`?')
        print(type(myfile))

        print('\nDirectly accessing `myfile` gives nothing :(')
        print(type(str(myfile.read())))
        print(str(myfile.read()))

        fs = FileSystemStorage()
        filename = fs.save("casefiles/"+myfile.name, myfile)
        print('\nHowever, when using FileSystemStorage...')
        print('\nReading filename: %s' % filename)
        print(type(fs.open(filename)))
        print(fs.open(filename))

        print('\nOpen and preview using pandas:')
        df = pd.NaT;
        if filename.endswith('.csv'):
            df = pd.read_csv(fs.open(filename), error_bad_lines=False,encoding="utf-8",index_col=False)
        if filename.endswith('.xlsx') or filename.endswith('.xls'):
            df = pd.read_excel(fs.open(filename))
        if filename.endswith('.txt'):
            df = pd.read_csv(fs.open(filename), delimiter = "\t")
        print(df)



        bulk_mgr = BulkCreateManager(chunk_size=10)

        for index, row in df.iterrows():
            print(row['casetype'])
            casetype = row['casetype']
            casetitle = row['casetitle']
            fir = row['fir']
            firreference = row['firreference']
            casedate = row['casedate']
            us = row['us']
            ps = row['ps']
            region = row['region']
            localno = row['localno']
            telco  = row['telco'] 
            internationalno = row['internationalno']
            country= row['country']
            voip  = row['voip']
            coplaintname = row['coplaintname']
            complaintno = row['complaintno']
            complaintcaste = row['complaintcaste']
            profession = row['profession']
            groupclaim = row['groupclaim']
            modusoperandus = row['modusoperandus']
            incidentdate = row['incidentdate']
            incidenttime = row['incidenttime']
            incident_place = row['incident_place']
            incident_ps_jurisdiction = row['incident_ps_jurisdiction']
            demand_amount = row['demand_amount']
            victim_reference  = row['victim_reference']
            victim= row['victim']
            io= row['io']
            remarks= row['remarks']

            bulk_mgr.add(Cases(casetype=casetype,casetitle=casetitle,fir=fir,firreference=firreference,casedate=casedate,us=us,ps=ps,region=region,localno=localno,telco=telco,internationalno=internationalno,country=country,voip=voip,coplaintname=coplaintname,complaintno=complaintno,complaintcaste=complaintcaste,profession=profession,groupclaim=groupclaim,modusoperandus=modusoperandus,incidentdate=incidentdate,incidenttime=incidenttime,incident_place=incident_place,incident_ps_jurisdiction=incident_ps_jurisdiction,demand_amount=demand_amount,victim_reference=victim_reference,victim=victim,io=io,remarks=remarks,user=request.user))
        bulk_mgr.done()

    context ={}

    if request.user.groups.filter(name = "admins").exists():
        context["dataset"] = Cases.objects.all()
    else:
        context["dataset"] = Cases.objects.all()
        #context["dataset"] = Cases.objects.filter(user=request.user)

    return render(request, "home/caselist.html", context)

def deletecase(request):
    ca_id = request.POST['ca_id'];
    #delete
    Cases.objects.filter(id=ca_id).delete()
    CDR.objects.filter(caseid=ca_id).delete()
    BTS.objects.filter(caseid=ca_id).delete()

    context ={}

    if request.user.groups.filter(name = "admins").exists():
        context["dataset"] = Cases.objects.all()
    else:
        context["dataset"] = Cases.objects.all()
        #context["dataset"] = Cases.objects.filter(user=request.user)

    return render(request, "home/caselist.html", context)


def checkprogress(request):
    #ChatConsumer.chat_message();
 
    return JsonResponse({'responseText':count})

def removefirst(x):
    return x[3:]

def r_xor_p(x, y, r_xor_p='r'):
    ''' Pearson's r or its p
    Depending of what you would like to get.
    '''
    r, p = stats.pearsonr(x, y)

    if r_xor_p == 'r':
        return r
    else:
        return p

def cdrlist(request):
    # dictionary for initial data with
    # field names as keys
    context ={}
    if not 'ca_id' in request.POST:
        print("ca_id not found")
    else:
        ca_id = request.POST['ca_id'];
        cdrlistid = request.POST['cdrlistid'];
        print(ca_id)
        context["ca_id"] = ca_id
        context["cdrlistid"] = cdrlistid
        context["dataset"] = CDR.objects.filter(caseid=ca_id , cdrlist=cdrlistid)[:100]

    
 
    # add the dictionary during initialization
    
    #context["dataset"] = CDR.objects.all(caseid == ca_id)
         
    return render(request, "home/cdrlist.html", context)

def cdrlistall(request):
    # dictionary for initial data with
    # field names as keys
    context ={}
    if not 'ca_id' in request.POST:
        print("ca_id not found")
    else:
        ca_id = request.POST['ca_id'];
        cdrlistid = request.POST['cdrlistid'];
        print(ca_id)
        context["dataset"] = CDR.objects.filter(caseid=ca_id , cdrlist=cdrlistid)

    
 
    # add the dictionary during initialization
    
    #context["dataset"] = CDR.objects.all(caseid == ca_id)
         
    return render(request, "home/cdrlist.html", context)

def btslist(request):
    # dictionary for initial data with
    # field names as keys
    context ={}
    if not 'ca_id' in request.POST:
        print("ca_id not found")
    else:
        ca_id = request.POST['ca_id'];
        cdrlistid = request.POST['cdrlistid'];
        print(ca_id)
        context["dataset"] = BTS.objects.filter(caseid=ca_id , cdrlist=cdrlistid)[:100]

    
 
    # add the dictionary during initialization
    
    #context["dataset"] = CDR.objects.all(caseid == ca_id)
         
    return render(request, "home/btslist.html", context)

def btslistall(request):
    # dictionary for initial data with
    # field names as keys
    context ={}
    if not 'ca_id' in request.POST:
        print("ca_id not found")
    else:
        ca_id = request.POST['ca_id'];
        cdrlistid = request.POST['cdrlistid'];
        print(ca_id)
        context["dataset"] = BTS.objects.filter(caseid=ca_id , cdrlist=cdrlistid)

    
 
    # add the dictionary during initialization
    
    #context["dataset"] = CDR.objects.all(caseid == ca_id)
         
    return render(request, "home/btslist.html", context)

def dataformat(request):
    # dictionary for initial data with
    # field names as keys
    context ={}
    

    
 
    # add the dictionary during initialization
    
    #context["dataset"] = CDR.objects.all(caseid == ca_id)
         
    return render(request, "home/dataformat.html", context)

def cdrreflist(request):
    # dictionary for initial data with
    # field names as keys
    context ={}
    if not 'ca_id' in request.POST:
        print("ca_id not found")
    else:
        ca_id = request.POST['ca_id'];

        print(ca_id)
        context["dataset"] = CDRList.objects.filter(caseid=ca_id)

    
 
    # add the dictionary during initialization
    
    #context["dataset"] = CDR.objects.all(caseid == ca_id)
         
    return render(request, "home/cdrreflist.html", context)



def btsreflist(request):
    # dictionary for initial data with
    # field names as keys
    context ={}
    if not 'ca_id' in request.POST:
        print("ca_id not found")
    else:
        ca_id = request.POST['ca_id'];

        print(ca_id)
        context["dataset"] = BTSList.objects.filter(caseid=ca_id)

    
 
    # add the dictionary during initialization
    
    #context["dataset"] = CDR.objects.all(caseid == ca_id)
         
    return render(request, "home/btsreflist.html", context)




def commoncaselist(request):
    # dictionary for initial data with
    # field names as keys
    print("commoncaselistkkkk")

    context ={}
    if request.user.groups.filter(name = "admins").exists():
        context["dataset"] = Cases.objects.all()
    else:
        context["dataset"] = Cases.objects.all()
        #context["dataset"] = Cases.objects.filter(user=request.user)
         
    return render(request, "home/commoncaselist.html", context)




def caselist(request):
    # dictionary for initial data with
    # field names as keys
    context ={}
    if request.user.groups.filter(name = "admins").exists():
        context["dataset"] = Cases.objects.all()
    else:
        context["dataset"] = Cases.objects.all()
        #context["dataset"] = Cases.objects.filter(user=request.user)
         
    return render(request, "home/caselist.html", context)



def searchcaselist(request):
    # dictionary for initial data with
    # field names as keys
    case_title = request.GET['search']
    context ={}
    if request.user.groups.filter(name = "admins").exists():
        context["dataset"] = Cases.objects.all().filter(casetitle__icontains=case_title)
    else:
        context["dataset"] = Cases.objects.all().filter(casetitle__icontains=case_title)
        #context["dataset"] = Cases.objects.filter(user=request.user).filter(casetitle__icontains=case_title)
         
    return render(request, "home/caselist.html", context)


def addcase(request):
    if request.method == 'POST':
        form = CasesForm(request.POST)
        if form.is_valid():
            instance = form.save(commit=False)
            instance.user = request.user
            instance.save()

            context ={}
            if request.user.groups.filter(name = "admins").exists():
                context["dataset"] = Cases.objects.all()
            else:
                context["dataset"] = Cases.objects.all()
                #context["dataset"] = Cases.objects.filter(user=request.user)
                 
            return render(request, "home/caselist.html", context)
        else:
            return render(request, "home/addcase.html")
         
    return render(request, "home/addcase.html")


@login_required(login_url="/login/")
def index(request):
    context = {'segment': 'index'}
    
    #context["dataset"] = Cases.objects.all();
    if request.user.groups.filter(name = "admins").exists():
        context["cases"] = Cases.objects.count();
        context["dataset"] = Cases.objects.all()[:6]
        # context["cdr"] = CDR.objects.count();
        # context["bts"] = BTS.objects.count();
        cdrss = CDR.objects.all().values('aparty').annotate(total=Count('aparty')).order_by('aparty')
        context["cdr"] = len(cdrss);
        btsss = BTS.objects.all().values('cellid').annotate(total=Count('cellid')).order_by('cellid')
        context["bts"] = len(btsss);

    else:
        context["cases"] = Cases.objects.count();
        context["dataset"] = Cases.objects.all()[:6]
        cdrss = CDR.objects.all().values('aparty').annotate(total=Count('aparty')).order_by('aparty')
        context["cdr"] = len(cdrss);
        btsss = BTS.objects.all().values('cellid').annotate(total=Count('cellid')).order_by('cellid')
        context["bts"] = len(btsss);
        # context["cases"] = Cases.objects.filter(user=request.user).count();
        # cas = Cases.objects.filter(user=request.user)


        # context["dataset"] = Cases.objects.filter(user=request.user)[:6]
        # context["cdr"] = CDR.objects.count();
        # context["bts"] = BTS.objects.count();
    #html_template = loader.get_template('home/dashboard.html')
    html_template = loader.get_template('home/dashboard.html')
    return HttpResponse(html_template.render(context, request))

@login_required(login_url="/login/")
def dashboard(request):
    context = {'segment': 'index'}
    if request.user.groups.filter(name = "admins").exists():
        context["cases"] = Cases.objects.count();
        context["dataset"] = Cases.objects.all()[:6]
        cdrss = CDR.objects.all().values('aparty').annotate(total=Count('aparty')).order_by('aparty')
        context["cdr"] = len(cdrss);
        btsss = BTS.objects.all().values('cellid').annotate(total=Count('cellid')).order_by('cellid')
        context["bts"] = len(btsss);

    else:
        context["cases"] = Cases.objects.count();
        context["dataset"] = Cases.objects.all()[:6]
        cdrss = CDR.objects.all().values('aparty').annotate(total=Count('aparty')).order_by('aparty')
        context["cdr"] = len(cdrss);
        btsss = BTS.objects.all().values('cellid').annotate(total=Count('cellid')).order_by('cellid')
        context["bts"] = len(btsss);
        # context["cases"] = Cases.objects.filter(user=request.user).count();
        # context["dataset"] = Cases.objects.filter(user=request.user)[:6]
        # context["cdr"] = CDR.objects.count();
        # context["bts"] = BTS.objects.count();
    html_template = loader.get_template('home/dashboard.html')
    return HttpResponse(html_template.render(context, request))

#@login_required(login_url="/login/")
def pages(request):
    context = {}
    # All resource paths end in .html.
    # Pick out the html file name from the url. And load that template.
    try:

        load_template = request.path.split('/')[-1]

        if load_template == 'admin':
            return HttpResponseRedirect(reverse('admin:index'))
        context['segment'] = load_template

        html_template = loader.get_template('home/' + load_template)
        return HttpResponse(html_template.render(context, request))

    except template.TemplateDoesNotExist:

        html_template = loader.get_template('home/page-404.html')
        return HttpResponse(html_template.render(context, request))

    except:
        html_template = loader.get_template('home/page-500.html')
        return HttpResponse(html_template.render(context, request))

#first jazz format
def jazz1(df,case_id,filename):

    #getting case id
    cc = Cases.objects.get(id=case_id)
    print(cc.id)

    # add a new column
    df['type'] = np.where(df['Duration']!= 0, "call", "sms")
    df = df[[ "Aparty", "BParty","Datetime","Duration","cellid","Imei","Imsi","type","CallType","SiteLocation"]]

    df.rename(columns={'Datetime': 'ts',"CallType":"Direction","type":"CallType","SiteLocation":"SiteAddress"}, inplace=True)

    #creating a cdr list record
    reference = df.loc[1, 'Aparty']
    ref = str(reference)

    if(ref.startswith("9230")):
        operator = "jazz"
        
    if(ref.startswith("009230")):
        operator = "jazz"
        
    if(ref.startswith("+9230")):
        operator = "jazz"
        
    if(ref.startswith("09230")):
        operator = "jazz"


    if(ref.startswith("9231")):
        operator = "zong"
        
    if(ref.startswith("009231")):
        operator = "zong"
        
    if(ref.startswith("+9231")):
        operator = "zong"
        
    if(ref.startswith("09231")):
        operator = "zong"
        
    
    cd = CDRList(reference=reference, operator=operator, caseid=cc )
    cdrlistid = cd.save()


    df['Aparty'] = df['Aparty'].astype(str)
    df['BParty'] = df['BParty'].astype(str)
    bulk_mgr = BulkCreateManager(chunk_size=500)

    for index, row in df.iterrows():


#transform aparty
        aparty = df.loc[index, 'Aparty']

        
        #check if it starts with 92
        if(aparty.startswith("92")):
            aparty=aparty[2:]
        if(aparty.startswith("0")):
            aparty=aparty[1:]
        if(aparty.startswith("0092")):
            aparty=aparty[4:]
        if(aparty.startswith("+92")):
            aparty=aparty[3:]
        if(aparty.startswith("092")):
            aparty=aparty[3:]
        if(aparty.endswith(".0")):
            aparty=aparty[:-2]

            

    #transform bparty
        bparty = df.loc[index, 'BParty']
        
        #check if it starts with 92
        if(bparty.startswith("92")):
            bparty=bparty[2:]
        if(bparty.startswith("0")):
            bparty=bparty[1:]
        if(bparty.startswith("0092")):
            bparty=bparty[4:]
        if(bparty.startswith("+92")):
            bparty=bparty[3:]
        if(bparty.startswith("092")):
            bparty=bparty[3:]
        if(bparty.endswith(".0")):
            bparty=bparty[:-2]

#transform time
        ts = df.loc[index, 'ts']
        ts = pd.to_datetime(ts)
        ts = str(ts)
        # date_time_obj = datetime.strptime(ts, '%m/%d/%y %H:%M')
        # ts = date_time_obj.strftime("%Y-%m-%dT%H:%M:%S")

        duration = df.loc[index, 'Duration']

#transform cell id
        cellid = df.loc[index, 'cellid']
        cellid = str(int(cellid, 16))

#transform imei
        Imei = df.loc[index, 'Imei']
        Imei = Imei.astype(str)
        if(Imei.endswith(".0")):
            Imei=Imei[:-2]

#transform imsi
        Imsi = df.loc[index, 'Imsi']
        Imsi = Imsi.astype(str)
        if(Imsi.endswith(".0")):
            Imsi=Imsi[:-2]

#already transformed
        calltype = df.loc[index, 'CallType']

        direction = df.loc[index, 'Direction']
        dtemp = direction.split()
        direction = dtemp[0].lower()

        sitelocation = df.loc[index, 'SiteAddress']
        p = re.compile(r'\d+\.\d+')  # Compile a pattern to capture float values
        floats = [float(i) for i in p.findall(sitelocation)]  # Convert strings to float
        source = "Nan"
        destination = "Nan"
        if(len(floats) >0):
            source = str(floats[0])
            destination = str(floats[1])
        oper = "jazz"
        #p = CDR(aparty=aparty, bparty=bparty, ts=ts, duration=duration, cellid=cellid, imei=Imei, imsi=Imsi, calltype=calltype, direction=direction, SiteAddress=sitelocation, caseid=cc , cdrlist=cd,source = source, destination=destination)
        #p.save()
        count = index+1;
        bulk_mgr.add(CDR(aparty=aparty, bparty=bparty, ts=ts, duration=duration, cellid=cellid, imei=Imei, imsi=Imsi, calltype=calltype, direction=direction, SiteAddress=sitelocation, caseid=cc , cdrlist=cd,source = source, destination=destination, operator = oper))
    bulk_mgr.done()


#second jazz format
def jazz2(df,case_id,filename):
    #getting case id
    cc = Cases.objects.get(id=case_id)
    print(cc.id)

    df['type'] = np.where(df['Duration']!= 0, "call", "sms")
    df = df[[ "Call Type", "A-Party","B-Party","Date & Time","Duration","Cell ID","IMEI","IMSI","type","Site"]]

    df.rename(columns={'Date & Time': 'ts',"Call Type":"Direction","type":"CallType","Site":"SiteAddress",
        "A-Party":"Aparty","B-Party":"BParty", "Cell ID":"cellid", "IMEI":"Imei","IMSI":"Imsi"}, inplace=True)
   
    print(df)
    #creating a cdr list record
    reference = df.loc[1, 'Aparty']
    ref = str(reference)
        
    
    cd = CDRList(reference=reference, operator="jazz", caseid=cc )
    cdrlistid = cd.save()

    df['Aparty'] = df['Aparty'].astype(str)
    df['BParty'] = df['BParty'].astype(str)
    bulk_mgr = BulkCreateManager(chunk_size=500)
    for index, row in df.iterrows():

        aparty = df.loc[index, 'Aparty']
        
        #check if it starts with 92
        if(aparty.startswith("92")):
            aparty=aparty[2:]
        if(aparty.startswith("0")):
            aparty=aparty[1:]
        if(aparty.startswith("0092")):
            aparty=aparty[4:]
        if(aparty.startswith("+92")):
            aparty=aparty[3:]
        if(aparty.startswith("092")):
            aparty=aparty[3:]
        if(aparty.endswith(".0")):
            aparty=aparty[:-2]


        bparty = df.loc[index, 'BParty']
        
        #check if it starts with 92
        if(bparty.startswith("92")):
            bparty=bparty[2:]
        if(bparty.startswith("0")):
            bparty=bparty[1:]
        if(bparty.startswith("0092")):
            bparty=bparty[4:]
        if(bparty.startswith("+92")):
            bparty=bparty[3:]
        if(bparty.startswith("092")):
            bparty=bparty[3:]
        if(bparty.endswith(".0")):
            bparty=bparty[:-2]


        ts = df.loc[index, 'ts']
        ts = pd.to_datetime(ts)
        ts = str(ts)


        duration = df.loc[index, 'Duration']
        cellid = df.loc[index, 'cellid']
        cellid = str(int(cellid, 16))
        Imei = df.loc[index, 'Imei']
        Imei = Imei.astype(str)
        if(Imei.endswith(".0")):
            Imei=Imei[:-2]
        Imsi = df.loc[index, 'Imsi']
        Imsi = Imsi.astype(str)
        if(Imsi.endswith(".0")):
            Imsi=Imsi[:-2]

        calltype = df.loc[index, 'CallType']
        direction = df.loc[index, 'Direction']
        dtemp = direction.split()
        direction = dtemp[0].lower()

        sitelocation = df.loc[index, 'SiteAddress']
        p = re.compile(r'\d+\.\d+')  # Compile a pattern to capture float values
        floats = [float(i) for i in p.findall(sitelocation)]  # Convert strings to float
        source = "Nan"
        destination = "Nan"

        
        print(len(floats))
        if(len(floats) >1):
            source = str(floats[0])
            destination = str(floats[1])
        oper = "jazz"
       
       
        #p = CDR(aparty=aparty, bparty=bparty, ts=ts, duration=duration, cellid=cellid, imei=Imei, imsi=Imsi, calltype=calltype, direction=direction, SiteAddress=sitelocation, caseid=cc , cdrlist=cd ,source = source, destination=destination)
        #p.save()
        count = index+1;
        bulk_mgr.add(CDR(aparty=aparty, bparty=bparty, ts=ts, duration=duration, cellid=cellid, imei=Imei, imsi=Imsi, calltype=calltype, direction=direction, SiteAddress=sitelocation, caseid=cc , cdrlist=cd,source = source, destination=destination, operator = oper))
    bulk_mgr.done()

#first zong format
def btszong2(df,case_id,filename):
    # # df = df[[ "Aparty", "BParty","Datetime","Duration","cellid","Imei","Imsi","type","CallType","SiteLocation"]]
    #getting case id
    cc = Cases.objects.get(id=case_id)
    print(cc.id)
    df['Duration'] = df['MINS'] * 60 + df['SECS']
    df['Duration'] = df['Duration'].astype(str)


    df['CELL_ID'] = df['LAC_ID'].astype(str) + df['CELL_ID'].astype(str)

    df['LAT'] = df['LAT'].astype(str)
    df['LNG'] = df['LNG'].astype(str)
    df['type'] = np.where(df['Duration']!= "0", "call", "sms")
    df['SiteLocation'] = df["SITE_ADDRESS"].astype(str)
    df["Imsi"] = pd.NaT

#note LAC_ID remaining
    df = df[[ "CALL_TYPE", "MSISDN_ID","BNUMBER","STRT_TM","Duration","LAC_ID","CELL_ID","IMEI","type","SiteLocation","Imsi","LAT","LNG"]]

    df.rename(columns={'CALL_TYPE': 'Direction',"MSISDN_ID":"Aparty","type":"CallType","BNUMBER":"BParty",
        "STRT_TM":"ts","CELL_ID":"cellid", "IMEI":"Imei", "SiteLocation":"SiteAddress","LAT":"source","LNG":"destination"}, inplace=True)
   
    print(df)
    #creating a cdr list record
    reference = df.loc[1, 'Aparty']
    ref = str(reference)

    
    cd = BTSList(reference=reference, operator="zong", caseid=cc )
    cdrlistid = cd.save()

    df['Aparty'] = df['Aparty'].astype(str)
    df['BParty'] = df['BParty'].astype(str)
    bulk_mgr = BulkCreateManager(chunk_size=500)
    for index, row in df.iterrows():

        aparty = df.loc[index, 'Aparty']
      
        #check if it starts with 92
        if(aparty.startswith("92")):
            aparty=aparty[2:]
        if(aparty.startswith("0092")):
            aparty=aparty[4:]
        if(aparty.startswith("+92")):
            aparty=aparty[3:]
        if(aparty.startswith("092")):
            aparty=aparty[3:]
        if(aparty.endswith(".0")):
            aparty=aparty[:-2]


        bparty = df.loc[index, 'BParty']
        
        #check if it starts with 92
        if(bparty.startswith("92")):
            bparty=bparty[2:]
        if(bparty.startswith("0092")):
            bparty=bparty[4:]
        if(bparty.startswith("+92")):
            bparty=bparty[3:]
        if(bparty.startswith("092")):
            bparty=bparty[3:]
        if(bparty.endswith(".0")):
            bparty=bparty[:-2]

        ts = df.loc[index, 'ts']
        ts = pd.to_datetime(ts)
        ts = str(ts)

        duration = df.loc[index, 'Duration']
        cellid = df.loc[index, 'cellid']

        Imei = df.loc[index, 'Imei']
        Imei = Imei.astype(str)
        if(Imei.endswith(".0")):
            Imei=Imei[:-2]
        Imsi = df.loc[index, 'Imsi']
        

        calltype = df.loc[index, 'CallType']
        direction = df.loc[index, 'Direction']
        dtemp = direction.split()
        direction = dtemp[2].lower()
        sitelocation = df.loc[index, 'SiteAddress']
        
        source = df.loc[index, 'source']
        destination = df.loc[index, 'destination']
        oper = "zong"
        
       
        #p = CDR(aparty=aparty, bparty=bparty, ts=ts, duration=duration, cellid=cellid, imei=Imei, imsi=Imsi, calltype=calltype, direction=direction, SiteAddress=sitelocation, caseid=cc , cdrlist=cd,source = source, destination=destination)
        #p.save()
        count = index+1;
        bulk_mgr.add(BTS(aparty=aparty, bparty=bparty, ts=ts, duration=duration, cellid=cellid, imei=Imei, imsi=Imsi, calltype=calltype, direction=direction, SiteAddress=sitelocation, caseid=cc , cdrlist=cd,source = source, destination=destination,operator=oper))
    bulk_mgr.done()


#first zong format
def zong1(df,case_id,filename):
    # # df = df[[ "Aparty", "BParty","Datetime","Duration","cellid","Imei","Imsi","type","CallType","SiteLocation"]]
    #getting case id
    cc = Cases.objects.get(id=case_id)
    print(cc.id)
    df['Duration'] = df['MINS'] * 60 + df['SECS']
    df['Duration'] = df['Duration'].astype(str)


    df['CELL_ID'] = df['LAC_ID'].astype(str) + df['CELL_ID'].astype(str)

    df['LAT'] = df['LAT'].astype(str)
    df['LNG'] = df['LNG'].astype(str)
    df['type'] = np.where(df['Duration']!= "0", "call", "sms")
    df['SiteLocation'] = df["SITE_ADDRESS"].astype(str)
    df["Imsi"] = pd.NaT

#note LAC_ID remaining
    df = df[[ "CALL_TYPE", "MSISDN_ID","BNUMBER","STRT_TM","Duration","LAC_ID","CELL_ID","IMEI","type","SiteLocation","Imsi","LAT","LNG"]]

    df.rename(columns={'CALL_TYPE': 'Direction',"MSISDN_ID":"Aparty","type":"CallType","BNUMBER":"BParty",
        "STRT_TM":"ts","CELL_ID":"cellid", "IMEI":"Imei", "SiteLocation":"SiteAddress","LAT":"source","LNG":"destination"}, inplace=True)
   
    print(df)
    #creating a cdr list record
    reference = df.loc[1, 'Aparty']
    ref = str(reference)

    
    cd = CDRList(reference=reference, operator="zong", caseid=cc )
    cdrlistid = cd.save()

    df['Aparty'] = df['Aparty'].astype(str)
    df['BParty'] = df['BParty'].astype(str)
    bulk_mgr = BulkCreateManager(chunk_size=500)
    for index, row in df.iterrows():

        aparty = df.loc[index, 'Aparty']
      
        #check if it starts with 92
        if(aparty.startswith("92")):
            aparty=aparty[2:]
        if(aparty.startswith("0092")):
            aparty=aparty[4:]
        if(aparty.startswith("+92")):
            aparty=aparty[3:]
        if(aparty.startswith("092")):
            aparty=aparty[3:]
        if(aparty.endswith(".0")):
            aparty=aparty[:-2]


        bparty = df.loc[index, 'BParty']
        
        #check if it starts with 92
        if(bparty.startswith("92")):
            bparty=bparty[2:]
        if(bparty.startswith("0092")):
            bparty=bparty[4:]
        if(bparty.startswith("+92")):
            bparty=bparty[3:]
        if(bparty.startswith("092")):
            bparty=bparty[3:]
        if(bparty.endswith(".0")):
            bparty=bparty[:-2]

        ts = df.loc[index, 'ts']
        ts = pd.to_datetime(ts)
        ts = str(ts)

        duration = df.loc[index, 'Duration']
        cellid = df.loc[index, 'cellid']

        Imei = df.loc[index, 'Imei']
        Imei = Imei.astype(str)
        if(Imei.endswith(".0")):
            Imei=Imei[:-2]
        Imsi = df.loc[index, 'Imsi']
        

        calltype = df.loc[index, 'CallType']
        direction = df.loc[index, 'Direction']
        dtemp = direction.split()
        direction = dtemp[2].lower()
        sitelocation = df.loc[index, 'SiteAddress']
        
        source = df.loc[index, 'source']
        destination = df.loc[index, 'destination']
        oper = "zong"
        
       
        #p = CDR(aparty=aparty, bparty=bparty, ts=ts, duration=duration, cellid=cellid, imei=Imei, imsi=Imsi, calltype=calltype, direction=direction, SiteAddress=sitelocation, caseid=cc , cdrlist=cd,source = source, destination=destination)
        #p.save()
        count = index+1;
        bulk_mgr.add(CDR(aparty=aparty, bparty=bparty, ts=ts, duration=duration, cellid=cellid, imei=Imei, imsi=Imsi, calltype=calltype, direction=direction, SiteAddress=sitelocation, caseid=cc , cdrlist=cd,source = source, destination=destination,operator=oper))
    bulk_mgr.done()



#first ufone format
def ufone1(df,case_id,filename):
    #getting case id
    cc = Cases.objects.get(id=case_id)
    print(cc.id)

    df['type'] = np.where(df['Call Duration']!= 0, "call", "sms")
    df = df[[ "IMSI", "IMEI","A Number","B Number","Call Start Time","Call Duration","Call Type"," Service Type","Cell ID - A","Cell Sector"," Location - A","type"]]

    df.rename(columns={'Call Start Time': 'ts',"Call Type":"Direction","type":"CallType"," Location - A":"SiteAddress",
        "A Number":"Aparty","B Number":"BParty", "Cell ID - A":"cellid", "IMEI":"Imei","IMSI":"Imsi"," Service Type":"servicetype", "Cell Sector":"cellsector","Call Duration":"Duration"}, inplace=True)
   
# lacid = models.CharField(max_length=150)
#    servicetype = models.CharField(max_length=150)
 #   cellsector = models.CharField(max_length=150)


    print(df)
    #creating a cdr list record
    reference = df.loc[1, 'Aparty']
    ref = str(reference)
        
    
    cd = CDRList(reference=reference, operator="ufone", caseid=cc )
    cdrlistid = cd.save()
    # df['BParty'] = df['BParty'].astype(float)
    # df['Aparty'].map(lambda x: '{:.0f}'.format(x))
    # df['BParty'].map(lambda x: '{:.0f}'.format(x))
    df['BParty'] = pd.to_numeric(df['BParty'].str.replace(',', '.'), errors='coerce')
    df['Aparty'] = df['Aparty'].astype(str)
    df['BParty'] = df['BParty'].astype(str)
    df['Imei'] = df['Imei'].astype(str)
    bulk_mgr = BulkCreateManager(chunk_size=500)
    for index, row in df.iterrows():

        aparty = df.loc[index, 'Aparty']
        
        #check if it starts with 92
        if(aparty.startswith("92")):
            aparty=aparty[2:]
        if(aparty.startswith("0092")):
            aparty=aparty[4:]
        if(aparty.startswith("+92")):
            aparty=aparty[3:]
        if(aparty.startswith("092")):
            aparty=aparty[3:]
        if(aparty.endswith(".0")):
            aparty=aparty[:-2]


        bparty = df.loc[index, 'BParty']
        bparty = bparty.strip()
        bparty = str(bparty)

        print(type(bparty))


        print(bparty[2:])
        #check if it starts with 92
        if(bparty.startswith("92")):
            bparty=bparty[2:]
            print("omer")
        if(bparty.startswith("0092")):
            bparty=bparty[4:]
        if(bparty.startswith("+92")):
            bparty=bparty[3:]
        if(bparty.startswith("092")):
            bparty=bparty[3:]
        if(bparty.endswith(".0")):
            bparty=bparty[:-2]


        print(bparty)

        ts = df.loc[index, 'ts']
        ts = pd.to_datetime(ts)
        ts = str(ts)

        duration = df.loc[index, 'Duration']
        cellid = df.loc[index, 'cellid']
        Imei = df.loc[index, 'Imei']
        if(Imei.endswith(".0")):
            Imei=Imei[:-2]

        Imsi = df.loc[index, 'Imsi']
        calltype = df.loc[index, 'CallType']
        direction = df.loc[index, 'Direction']
        direction = direction.lower()

        sitelocation = df.loc[index, 'SiteAddress']

        servicetype = df.loc[index,'servicetype']
        cellsector = df.loc[index,"cellsector"]
        oper = "ufone"
       
        #p = CDR(aparty=aparty, bparty=bparty, ts=ts, duration=duration, cellid=cellid, imei=Imei, imsi=Imsi, calltype=calltype, direction=direction, SiteAddress=sitelocation, caseid=cc , cdrlist=cd,cellsector=cellsector,servicetype=servicetype)
        #p.save()
        count = index+1;
        bulk_mgr.add(CDR(aparty=aparty, bparty=bparty, ts=ts, duration=duration, cellid=cellid, imei=Imei, imsi=Imsi, calltype=calltype, direction=direction, SiteAddress=sitelocation, caseid=cc , cdrlist=cd,cellsector=cellsector,servicetype=servicetype,operator=oper))
    bulk_mgr.done()


#first ufone format
def ufone2(df,case_id,filename):
    #getting case id
    cc = Cases.objects.get(id=case_id)
    print(cc.id)

    df['type'] = np.where(df['duration']!= 0, "call", "sms")
    df = df[[ "IMSI", "IMEI","A Number","B Number","Start Time","Direction","duration","Type","Service Provider","Cell Id","Cell Sector","Location","type","Latitude","Longitude"]]

    df.rename(columns={'Start Time': 'ts',"type":"CallType","Location":"SiteAddress",
        "A Number":"Aparty","B Number":"BParty", "Cell Id":"cellid", "IMEI":"Imei","IMSI":"Imsi","Service Provider":"servicetype", "Cell Sector":"cellsector","duration":"Duration"}, inplace=True)
   
# lacid = models.CharField(max_length=150)
#    servicetype = models.CharField(max_length=150)
 #   cellsector = models.CharField(max_length=150)


    print(df)
    #creating a cdr list record
    reference = df.loc[1, 'Aparty']
    ref = str(reference)
        
    
    cd = CDRList(reference=reference, operator="ufone", caseid=cc )
    cdrlistid = cd.save()

    df['Aparty'] = df['Aparty'].astype(str)
    df['BParty'] = df['BParty'].astype(str)
    bulk_mgr = BulkCreateManager(chunk_size=500)
    for index, row in df.iterrows():

        aparty = df.loc[index, 'Aparty']
        
        #check if it starts with 92
        if(aparty.startswith("92")):
            aparty=aparty[2:]
        if(aparty.startswith("0092")):
            aparty=aparty[4:]
        if(aparty.startswith("+92")):
            aparty=aparty[3:]
        if(aparty.startswith("092")):
            aparty=aparty[3:]
        if(aparty.endswith(".0")):
            aparty=aparty[:-2]


        bparty = df.loc[index, 'BParty']

        
        #check if it starts with 92
        if(bparty.startswith("92")):
            bparty=bparty[2:]
        if(bparty.startswith("0092")):
            bparty=bparty[4:]
        if(bparty.startswith("+92")):
            bparty=bparty[3:]
        if(bparty.startswith("092")):
            bparty=bparty[3:]
        if(bparty.endswith(".0")):
            bparty=bparty[:-2]

        ts = df.loc[index, 'ts']
        ts = pd.to_datetime(ts)
        ts = str(ts)

        duration = df.loc[index, 'Duration']
        cellid = df.loc[index, 'cellid']
        Imei = df.loc[index, 'Imei']

        Imsi = df.loc[index, 'Imsi']
        calltype = df.loc[index, 'CallType']
        direction = df.loc[index, 'Direction']
        direction = direction.lower()

        sitelocation = df.loc[index, 'SiteAddress']

        servicetype = df.loc[index,'servicetype']
        cellsector = df.loc[index,"cellsector"]
        oper = "ufone"
        lat = df.loc[index,"Latitude"]
        lng = df.loc[index,"Longitude"]
       
        #p = CDR(aparty=aparty, bparty=bparty, ts=ts, duration=duration, cellid=cellid, imei=Imei, imsi=Imsi, calltype=calltype, direction=direction, SiteAddress=sitelocation, caseid=cc , cdrlist=cd,cellsector=cellsector,servicetype=servicetype)
        #p.save()
        count = index+1;
        bulk_mgr.add(CDR(aparty=aparty, bparty=bparty, ts=ts, duration=duration, cellid=cellid, imei=Imei, imsi=Imsi, calltype=calltype, direction=direction, SiteAddress=sitelocation, caseid=cc , cdrlist=cd,cellsector=cellsector,servicetype=servicetype,operator=oper,source=lat,destination=lng))
    bulk_mgr.done()



#first ufone format
def btsufone2(df,case_id,filename):
    #getting case id
    cc = Cases.objects.get(id=case_id)
    print(cc.id)

    df['type'] = np.where(df['duration']!= 0, "call", "sms")
    df = df[[ "IMSI", "IMEI","A Number","B Number","Start Time","Direction","duration","Type","Service Provider","Cell Id","Cell Sector","Location","type","Latitude","Longitude"]]

    df.rename(columns={'Start Time': 'ts',"type":"CallType","Location":"SiteAddress",
        "A Number":"Aparty","B Number":"BParty", "Cell Id":"cellid", "IMEI":"Imei","IMSI":"Imsi","Service Provider":"servicetype", "Cell Sector":"cellsector","duration":"Duration"}, inplace=True)
   
# lacid = models.CharField(max_length=150)
#    servicetype = models.CharField(max_length=150)
 #   cellsector = models.CharField(max_length=150)


    print(df)
    #creating a cdr list record
    reference = df.loc[1, 'Aparty']
    ref = str(reference)
        
    
    cd = BTSList(reference=reference, operator="ufone", caseid=cc )
    cdrlistid = cd.save()

    df['Aparty'] = df['Aparty'].astype(str)
    df['BParty'] = df['BParty'].astype(str)
    bulk_mgr = BulkCreateManager(chunk_size=500)
    for index, row in df.iterrows():

        aparty = df.loc[index, 'Aparty']
        
        #check if it starts with 92
        if(aparty.startswith("92")):
            aparty=aparty[2:]
        if(aparty.startswith("0092")):
            aparty=aparty[4:]
        if(aparty.startswith("+92")):
            aparty=aparty[3:]
        if(aparty.startswith("092")):
            aparty=aparty[3:]
        if(aparty.endswith(".0")):
            aparty=aparty[:-2]


        bparty = df.loc[index, 'BParty']

        
        #check if it starts with 92
        if(bparty.startswith("92")):
            bparty=bparty[2:]
        if(bparty.startswith("0092")):
            bparty=bparty[4:]
        if(bparty.startswith("+92")):
            bparty=bparty[3:]
        if(bparty.startswith("092")):
            bparty=bparty[3:]
        if(bparty.endswith(".0")):
            bparty=bparty[:-2]

        ts = df.loc[index, 'ts']
        ts = pd.to_datetime(ts)
        ts = str(ts)

        duration = df.loc[index, 'Duration']
        cellid = df.loc[index, 'cellid']
        Imei = df.loc[index, 'Imei']

        Imsi = df.loc[index, 'Imsi']
        calltype = df.loc[index, 'CallType']
        direction = df.loc[index, 'Direction']
        direction = direction.lower()

        sitelocation = df.loc[index, 'SiteAddress']

        servicetype = df.loc[index,'servicetype']
        cellsector = df.loc[index,"cellsector"]
        oper = "ufone"
        lat = df.loc[index,"Latitude"]
        lng = df.loc[index,"Longitude"]
       
        #p = CDR(aparty=aparty, bparty=bparty, ts=ts, duration=duration, cellid=cellid, imei=Imei, imsi=Imsi, calltype=calltype, direction=direction, SiteAddress=sitelocation, caseid=cc , cdrlist=cd,cellsector=cellsector,servicetype=servicetype)
        #p.save()
        count = index+1;
        bulk_mgr.add(BTS(aparty=aparty, bparty=bparty, ts=ts, duration=duration, cellid=cellid, imei=Imei, imsi=Imsi, calltype=calltype, direction=direction, SiteAddress=sitelocation, caseid=cc , cdrlist=cd,cellsector=cellsector,servicetype=servicetype,operator=oper,source=lat,destination=lng))
    bulk_mgr.done()




#second jazz format
def warid(df,case_id,filename):
    #getting case id
    cc = Cases.objects.get(id=case_id)
    print(cc.id)

    df['type'] = np.where(df['DURATION']!= 1, "call", "sms")
    df['Date & Time'] = df['A_TRANSDATE'].astype(str)
    df["Imsi"] = pd.NaT
    
    
    df = df[[ "SUBNO", "B_SUBNO","A_TRANSDATE","TRANSTIME","DURATION","CELL_ID","DESCRIPTION","IMEI_NUMBER","type","OPER","Date & Time","Imsi"]]

    df.rename(columns={'Date & Time': 'ts',"OPER":"Direction","type":"CallType","DESCRIPTION":"SiteAddress",
        "SUBNO":"Aparty","B_SUBNO":"BParty", "CELL_ID":"cellid", "IMEI_NUMBER":"Imei","DURATION":"Duration"}, inplace=True)
   
    print(df)
    #creating a cdr list record
    reference = df.loc[1, 'Aparty']
    ref = str(reference)
        
    
    cd = CDRList(reference=reference, operator="warid", caseid=cc )
    cdrlistid = cd.save()

    df['Aparty'] = df['Aparty'].astype(str)
    df['BParty'] = df['BParty'].astype(str)

    bulk_mgr = BulkCreateManager(chunk_size=500)
    for index, row in df.iterrows():

        aparty = df.loc[index, 'Aparty']
       
        #check if it starts with 92
        if(aparty.startswith("92")):
            aparty=aparty[2:]
        if(aparty.startswith("0092")):
            aparty=aparty[4:]
        if(aparty.startswith("+92")):
            aparty=aparty[3:]
        if(aparty.startswith("092")):
            aparty=aparty[3:]
        if(aparty.endswith(".0")):
            aparty=aparty[:-2]


        bparty = df.loc[index, 'BParty']
        
        #check if it starts with 92
        if(bparty.startswith("92")):
            bparty=bparty[2:]
        if(bparty.startswith("0092")):
            bparty=bparty[4:]
        if(bparty.startswith("+92")):
            bparty=bparty[3:]
        if(bparty.startswith("092")):
            bparty=bparty[3:]
        if(bparty.endswith(".0")):
            bparty=bparty[:-2]

        ts = df.loc[index, 'ts']
        ts = pd.to_datetime(ts)
        ts = str(ts)

        duration = df.loc[index, 'Duration']
        cellid = df.loc[index, 'cellid']
        cellid = str(cellid)
        if(cellid.endswith(".0")):
            cellid=cellid[:-2]

        Imei = df.loc[index, 'Imei']
        Imei = Imei.astype(str)
        if(Imei.endswith(".0")):
            Imei=Imei[:-2]
     
        Imsi = df.loc[index, 'Imsi']
        calltype = df.loc[index, 'CallType']
        direction = df.loc[index, 'Direction']
        dtemp = direction.split()
        direction = dtemp[0].lower()

        sitelocation = df.loc[index, 'SiteAddress']
       
        #p = CDR(aparty=aparty, bparty=bparty, ts=ts, duration=duration, cellid=cellid, imei=Imei, imsi=Imsi, calltype=calltype, direction=direction, SiteAddress=sitelocation, caseid=cc , cdrlist=cd)
        #p.save()
        count = index+1;
        bulk_mgr.add(CDR(aparty=aparty, bparty=bparty, ts=ts, duration=duration, cellid=cellid, imei=Imei, imsi=Imsi, calltype=calltype, direction=direction, SiteAddress=sitelocation, caseid=cc , cdrlist=cd, operator="warid"))
    bulk_mgr.done()



#second telenor format
def telenor(df,case_id,filename):
    #getting case id
    cc = Cases.objects.get(id=case_id)
    print(cc.id)

    # if("call_org_num" in df.columns):
    #     df.rename(columns={'call_org_num': 'CALL_ORIG_NUM',"lat":"LAT","longitude":"LONGITUDE","Lac_Id":"Cell_Lac_Id","Site_Id":"Cell_Site_Id"}, inplace=True)
    df['CALL_TYPE'] = np.where(df['CALL_TYPE']== "GSM", "call", "sms")
    df['B-Party'] = np.where(df['MSISDN'] == df['CALL_ORIG_NUM'],df['CALL_DIALED_NUM'], df['CALL_ORIG_NUM'])
    df = df[[ "MSISDN","B-Party", "CALL_ORIG_NUM","CALL_DIALED_NUM","IMSI","IMEI","CALL_START_DT_TM","CALL_END_DT_TM","INBOUND_OUTBOUND_IND","Call_Network_Volume","Cell_Lac_Id","Cell_Site_Id","ORIG_OPER_NAME","TERM_OPER_NAME","CALL_TYPE","Location"]]


    df.rename(columns={'MSISDN': 'Aparty',"B-Party":"BParty","CALL_TYPE":"CallType","Location":"SiteAddress","CALL_START_DT_TM":"ts",
        "A-Party":"Aparty","B-Party":"BParty", "Cell_Lac_Id":"cellid", "IMEI":"Imei","IMSI":"Imsi","INBOUND_OUTBOUND_IND":"Direction","Call_Network_Volume":"Duration","ORIG_OPER_NAME":"operator"}, inplace=True)
   
    print(df)
    #creating a cdr list record
    reference = df.loc[1, 'Aparty']
    ref = str(reference)
        
    
    cd = CDRList(reference=reference, operator="telenor", caseid=cc )
    cdrlistid = cd.save()

    df['Aparty'] = df['Aparty'].astype(str)
    df['BParty'] = df['BParty'].astype(str)

    bulk_mgr = BulkCreateManager(chunk_size=500)
    for index, row in df.iterrows():

        aparty = df.loc[index, 'Aparty']
        
        #check if it starts with 92
        if(aparty.startswith("92")):
            aparty=aparty[2:]
        if(aparty.startswith("0092")):
            aparty=aparty[4:]
        if(aparty.startswith("+92")):
            aparty=aparty[3:]
        if(aparty.startswith("092")):
            aparty=aparty[3:]
        if(aparty.endswith(".0")):
            aparty=aparty[:-2]


        bparty = df.loc[index, 'BParty']
        
        #check if it starts with 92
        if(bparty.startswith("92")):
            bparty=bparty[2:]
        if(bparty.startswith("0092")):
            bparty=bparty[4:]
        if(bparty.startswith("+92")):
            bparty=bparty[3:]
        if(bparty.startswith("092")):
            bparty=bparty[3:]
        if(bparty.endswith(".0")):
            bparty=bparty[:-2]

        ts = df.loc[index, 'ts']
        d = datetime.strptime(ts, "%Y-%m-%d%H:%M:%S")
        
        ts=str(d)
        # ts = pd.to_datetime(ts)
        # ts = str(ts)

        duration = df.loc[index, 'Duration']
        cellid = df.loc[index, 'cellid']
        Imei = df.loc[index, 'Imei']
        Imei = Imei.astype(str)
        if(Imei.endswith(".0")):
            Imei=Imei[:-2]
        Imsi = df.loc[index, 'Imsi']
        Imsi = Imsi.astype(str)
        if(Imsi.endswith(".0")):
            Imsi=Imsi[:-2]
        calltype = df.loc[index, 'CallType']
        direction = df.loc[index, 'Direction']
        dtemp = direction.split()
        direction = dtemp[0].lower()
        sitelocation = df.loc[index, 'SiteAddress']
        #operator = df.loc[index,'operator']
        operator = "telenor"
        source = pd.NaT
        destination = pd.NaT
       
        #p = CDR(aparty=aparty, bparty=bparty, ts=ts, duration=duration, cellid=cellid, imei=Imei, imsi=Imsi, calltype=calltype, direction=direction, SiteAddress=sitelocation, caseid=cc , cdrlist=cd,operator=operator)
        bulk_mgr.add(CDR(aparty=aparty, bparty=bparty, ts=ts, duration=duration, cellid=cellid, imei=Imei, imsi=Imsi, calltype=calltype, direction=direction, SiteAddress=sitelocation, caseid=cc , cdrlist=cd,operator=operator,source = source, destination=destination))
  
        #p.save()
        count = index+1;

    bulk_mgr.done()



#second telenor format
def telenor3(df,case_id,filename):
    #getting case id
    cc = Cases.objects.get(id=case_id)
    print(cc.id)

    # if("call_org_num" in df.columns):
    #     df.rename(columns={'call_org_num': 'CALL_ORIG_NUM',"lat":"LAT","longitude":"LONGITUDE","Lac_Id":"Cell_Lac_Id","Site_Id":"Cell_Site_Id"}, inplace=True)
    df['CALL_TYPE'] = np.where(df['CALL_TYPE']== "GSM", "call", "sms")
    df['B-Party'] = np.where(df['MSISDN'] == df['CALL_ORIG_NUM'],df['CALL_DIALED_NUM'], df['CALL_ORIG_NUM'])
    df = df[[ "MSISDN","B-Party", "CALL_ORIG_NUM","CALL_DIALED_NUM","IMSI","IMEI","CALL_START_DT_TM","CALL_END_DT_TM","INBOUND_OUTBOUND_IND","Call_Network_Volume","Cell_Lac_Id","Cell_Site_Id","ORIG_OPER_NAME","TERM_OPER_NAME","CALL_TYPE","Location"]]


    df.rename(columns={'MSISDN': 'Aparty',"B-Party":"BParty","CALL_TYPE":"CallType","Location":"SiteAddress","CALL_START_DT_TM":"ts",
        "A-Party":"Aparty","B-Party":"BParty", "Cell_Lac_Id":"cellid", "IMEI":"Imei","IMSI":"Imsi","INBOUND_OUTBOUND_IND":"Direction","Call_Network_Volume":"Duration","ORIG_OPER_NAME":"operator"}, inplace=True)
   
    print(df)
    #creating a cdr list record
    reference = df.loc[1, 'Aparty']
    ref = str(reference)
        
    
    cd = CDRList(reference=reference, operator="telenor", caseid=cc )
    cdrlistid = cd.save()

    df['Aparty'] = df['Aparty'].astype(str)
    df['BParty'] = df['BParty'].astype(str)

    bulk_mgr = BulkCreateManager(chunk_size=500)
    for index, row in df.iterrows():

        aparty = df.loc[index, 'Aparty']
        
        #check if it starts with 92
        if(aparty.startswith("92")):
            aparty=aparty[2:]
        if(aparty.startswith("0092")):
            aparty=aparty[4:]
        if(aparty.startswith("+92")):
            aparty=aparty[3:]
        if(aparty.startswith("092")):
            aparty=aparty[3:]
        if(aparty.endswith(".0")):
            aparty=aparty[:-2]


        bparty = df.loc[index, 'BParty']
        
        #check if it starts with 92
        if(bparty.startswith("92")):
            bparty=bparty[2:]
        if(bparty.startswith("0092")):
            bparty=bparty[4:]
        if(bparty.startswith("+92")):
            bparty=bparty[3:]
        if(bparty.startswith("092")):
            bparty=bparty[3:]
        if(bparty.endswith(".0")):
            bparty=bparty[:-2]

        ts = df.loc[index, 'ts']
        d = datetime.strptime(ts, "%Y-%m-%d%H:%M:%S")
        
        ts=str(d)
        # ts = pd.to_datetime(ts)
        # ts = str(ts)

        duration = df.loc[index, 'Duration']
        cellid = df.loc[index, 'cellid']
        Imei = df.loc[index, 'Imei']
        Imei = Imei.astype(str)
        if(Imei.endswith(".0")):
            Imei=Imei[:-2]
        Imsi = df.loc[index, 'Imsi']
        Imsi = Imsi.astype(str)
        if(Imsi.endswith(".0")):
            Imsi=Imsi[:-2]
        calltype = df.loc[index, 'CallType']
        direction = df.loc[index, 'Direction']
        dtemp = direction.split()
        direction = dtemp[0].lower()
        sitelocation = df.loc[index, 'SiteAddress']
        #operator = df.loc[index,'operator']
        operator = "telenor"
        source = pd.NaT
        destination = pd.NaT
       
        #p = CDR(aparty=aparty, bparty=bparty, ts=ts, duration=duration, cellid=cellid, imei=Imei, imsi=Imsi, calltype=calltype, direction=direction, SiteAddress=sitelocation, caseid=cc , cdrlist=cd,operator=operator)
        bulk_mgr.add(CDR(aparty=aparty, bparty=bparty, ts=ts, duration=duration, cellid=cellid, imei=Imei, imsi=Imsi, calltype=calltype, direction=direction, SiteAddress=sitelocation, caseid=cc , cdrlist=cd,operator=operator,source = source, destination=destination))
  
        #p.save()
        count = index+1;

    bulk_mgr.done()


#second jazz format
def telenor2(df,case_id,filename):
    #getting case id
    cc = Cases.objects.get(id=case_id)
    print(cc.id)

    # if("call_org_num" in df.columns):
    #     df.rename(columns={'call_org_num': 'CALL_ORIG_NUM',"lat":"LAT","longitude":"LONGITUDE","Lac_Id":"Cell_Lac_Id","Site_Id":"Cell_Site_Id"}, inplace=True)
    df['CALL_TYPE'] = np.where(df['CALL_TYPE']== "GSM", "call", "sms")
    df['B-Party'] = np.where(df['MSISDN'] == df['call_org_num'],df['CALL_DIALED_NUM'], df['call_org_num'])
    df = df[[ "MSISDN","B-Party", "call_org_num","CALL_DIALED_NUM","IMSI","IMEI","CALL_START_DT_TM","CALL_END_DT_TM","INBOUND_OUTBOUND_IND","Call_Network_Volume","Lac_Id","Cell_SITE_ID","CALL_TYPE","location","lat","longitude"]]
    #cellid misiing

    df.rename(columns={'MSISDN': 'Aparty',"B-Party":"BParty","CALL_TYPE":"CallType","location":"SiteAddress","CALL_START_DT_TM":"ts",
        "A-Party":"Aparty","B-Party":"BParty", "Cell_SITE_ID":"cellid", "IMEI":"Imei","IMSI":"Imsi","INBOUND_OUTBOUND_IND":"Direction","Call_Network_Volume":"Duration",}, inplace=True)
   
    print(df)
    #creating a cdr list record
    reference = df.loc[1, 'Aparty']
    ref = str(reference)
        
    
    cd = CDRList(reference=reference, operator="telenor", caseid=cc )
    cdrlistid = cd.save()

    df['Aparty'] = df['Aparty'].astype(str)
    df['BParty'] = df['BParty'].astype(str)

    bulk_mgr = BulkCreateManager(chunk_size=500)
    for index, row in df.iterrows():

        aparty = df.loc[index, 'Aparty']
        
        #check if it starts with 92
        if(aparty.startswith("92")):
            aparty=aparty[2:]
        if(aparty.startswith("0092")):
            aparty=aparty[4:]
        if(aparty.startswith("+92")):
            aparty=aparty[3:]
        if(aparty.startswith("092")):
            aparty=aparty[3:]
        if(aparty.endswith(".0")):
            aparty=aparty[:-2]


        bparty = df.loc[index, 'BParty']
        
        #check if it starts with 92
        if(bparty.startswith("92")):
            bparty=bparty[2:]
        if(bparty.startswith("0092")):
            bparty=bparty[4:]
        if(bparty.startswith("+92")):
            bparty=bparty[3:]
        if(bparty.startswith("092")):
            bparty=bparty[3:]
        if(bparty.endswith(".0")):
            bparty=bparty[:-2]

        ts = df.loc[index, 'ts']
        # d = datetime.strptime(ts, "%Y-%m-%d%H:%M:%S")
        
        # ts=str(d)
        ts = pd.to_datetime(ts)
        ts = str(ts)

        duration = df.loc[index, 'Duration']
        cellid = df.loc[index, 'cellid']
        Imei = df.loc[index, 'Imei']
        Imei = Imei.astype(str)
        if(Imei.endswith(".0")):
            Imei=Imei[:-2]
        Imsi = df.loc[index, 'Imsi']
        Imsi = Imsi.astype(str)
        if(Imsi.endswith(".0")):
            Imsi=Imsi[:-2]
        calltype = df.loc[index, 'CallType']
        direction = df.loc[index, 'Direction']
        dtemp = direction.split()
        direction = dtemp[0].lower()
        sitelocation = df.loc[index, 'SiteAddress']
        #operator = df.loc[index,'operator']
        operator = "telenor"
        source = df.loc[index, 'lat']
        destination = df.loc[index, 'longitude']
       
        #p = CDR(aparty=aparty, bparty=bparty, ts=ts, duration=duration, cellid=cellid, imei=Imei, imsi=Imsi, calltype=calltype, direction=direction, SiteAddress=sitelocation, caseid=cc , cdrlist=cd,operator=operator)
        bulk_mgr.add(CDR(aparty=aparty, bparty=bparty, ts=ts, duration=duration, cellid=cellid, imei=Imei, imsi=Imsi, calltype=calltype, direction=direction, SiteAddress=sitelocation, caseid=cc , cdrlist=cd,operator=operator,source = source, destination=destination))
  
        #p.save()
        count = index+1;

    bulk_mgr.done()




#second jazz format
def btstelenor2(df,case_id,filename):
    #getting case id
    cc = Cases.objects.get(id=case_id)
    print(cc.id)

    # if("call_org_num" in df.columns):
    #     df.rename(columns={'call_org_num': 'CALL_ORIG_NUM',"lat":"LAT","longitude":"LONGITUDE","Lac_Id":"Cell_Lac_Id","Site_Id":"Cell_Site_Id"}, inplace=True)
    df['CALL_TYPE'] = np.where(df['CALL_TYPE']== "GSM", "call", "sms")
    df['B-Party'] = np.where(df['MSISDN'] == df['call_org_num'],df['CALL_DIALED_NUM'], df['call_org_num'])
    df = df[[ "MSISDN","B-Party", "call_org_num","CALL_DIALED_NUM","IMSI","IMEI","CALL_START_DT_TM","CALL_END_DT_TM","INBOUND_OUTBOUND_IND","Call_Network_Volume","Lac_Id","Cell_SITE_ID","CALL_TYPE","location","lat","longitude"]]
    #cellid misiing

    df.rename(columns={'MSISDN': 'Aparty',"B-Party":"BParty","CALL_TYPE":"CallType","location":"SiteAddress","CALL_START_DT_TM":"ts",
        "A-Party":"Aparty","B-Party":"BParty", "Cell_SITE_ID":"cellid", "IMEI":"Imei","IMSI":"Imsi","INBOUND_OUTBOUND_IND":"Direction","Call_Network_Volume":"Duration",}, inplace=True)
   
    print(df)
    #creating a cdr list record
    reference = df.loc[1, 'Aparty']
    ref = str(reference)
        
    
    cd = BTSList(reference=reference, operator="telenor", caseid=cc )
    cdrlistid = cd.save()

    df['Aparty'] = df['Aparty'].astype(str)
    df['BParty'] = df['BParty'].astype(str)

    bulk_mgr = BulkCreateManager(chunk_size=500)
    for index, row in df.iterrows():

        aparty = df.loc[index, 'Aparty']
        
        #check if it starts with 92
        if(aparty.startswith("92")):
            aparty=aparty[2:]
        if(aparty.startswith("0092")):
            aparty=aparty[4:]
        if(aparty.startswith("+92")):
            aparty=aparty[3:]
        if(aparty.startswith("092")):
            aparty=aparty[3:]
        if(aparty.endswith(".0")):
            aparty=aparty[:-2]


        bparty = df.loc[index, 'BParty']
        
        #check if it starts with 92
        if(bparty.startswith("92")):
            bparty=bparty[2:]
        if(bparty.startswith("0092")):
            bparty=bparty[4:]
        if(bparty.startswith("+92")):
            bparty=bparty[3:]
        if(bparty.startswith("092")):
            bparty=bparty[3:]
        if(bparty.endswith(".0")):
            bparty=bparty[:-2]

        ts = df.loc[index, 'ts']
        # d = datetime.strptime(ts, "%Y-%m-%d%H:%M:%S")
        
        # ts=str(d)
        ts = pd.to_datetime(ts)
        ts = str(ts)

        duration = df.loc[index, 'Duration']
        cellid = df.loc[index, 'cellid']
        Imei = df.loc[index, 'Imei']
        Imei = Imei.astype(str)
        if(Imei.endswith(".0")):
            Imei=Imei[:-2]
        Imsi = df.loc[index, 'Imsi']
        Imsi = Imsi.astype(str)
        if(Imsi.endswith(".0")):
            Imsi=Imsi[:-2]
        calltype = df.loc[index, 'CallType']
        direction = df.loc[index, 'Direction']
        dtemp = direction.split()
        direction = dtemp[0].lower()
        sitelocation = df.loc[index, 'SiteAddress']
        #operator = df.loc[index,'operator']
        operator = "telenor"
        source = df.loc[index, 'lat']
        destination = df.loc[index, 'longitude']
       
        #p = CDR(aparty=aparty, bparty=bparty, ts=ts, duration=duration, cellid=cellid, imei=Imei, imsi=Imsi, calltype=calltype, direction=direction, SiteAddress=sitelocation, caseid=cc , cdrlist=cd,operator=operator)
        bulk_mgr.add(BTS(aparty=aparty, bparty=bparty, ts=ts, duration=duration, cellid=cellid, imei=Imei, imsi=Imsi, calltype=calltype, direction=direction, SiteAddress=sitelocation, caseid=cc , cdrlist=cd,operator=operator,source = source, destination=destination))
  
        #p.save()
        count = index+1;

    bulk_mgr.done()

#second jazz format
def btstelenor3(df,case_id,filename):
    #getting case id
    cc = Cases.objects.get(id=case_id)
    print(cc.id)

    # if("call_org_num" in df.columns):
    #     df.rename(columns={'call_org_num': 'CALL_ORIG_NUM',"lat":"LAT","longitude":"LONGITUDE","Lac_Id":"Cell_Lac_Id","Site_Id":"Cell_Site_Id"}, inplace=True)
    df['Call_Type'] = np.where(df['Call_Type']== "GSM", "call", "sms")
    #df['direction'] = np.where(df['RATED_USG_VOL']== "1", "incoming", "outgoing")
    df['CALL_DATE'] = pd.to_datetime(df['CALL_DATE']).dt.date

    df["cellid"] = df["CELL_SITE_ID"].astype(str)+df["CELL_LAC_ID"].astype(str)
    df["Direction"] = pd.NaT
    df = df[[ "CALL_DATE","CALL_TM", "ORIG_NUMBER_VAL","DIALED_NUMBER_VAL","IMSI","IMEI","NETWRK_USG_VOL","CELL_SITE_ID","CELL_LAC_ID","Location","Direction","cellid","Call_Type"]]
    #cellid misiing

    df.rename(columns={'ORIG_NUMBER_VAL': 'Aparty',"DIALED_NUMBER_VAL":"BParty","Call_Type":"CallType","Location":"SiteAddress","CALL_DATE":"ts","CALL_TM":"tst",
          "IMEI":"Imei","IMSI":"Imsi","NETWRK_USG_VOL":"Duration"}, inplace=True)
   
    print(df)
    #creating a cdr list record
    reference = df.loc[1, 'Aparty']
    ref = str(reference)
    

    
    cd = BTSList(reference=reference, operator="telenor", caseid=cc )
    cdrlistid = cd.save()

    df['Aparty'] = df['Aparty'].astype(str)
    df['BParty'] = df['BParty'].astype(str)

    bulk_mgr = BulkCreateManager(chunk_size=500)
    for index, row in df.iterrows():

        aparty = df.loc[index, 'Aparty']
        
        #check if it starts with 92
        if(aparty.startswith("92")):
            aparty=aparty[2:]
        if(aparty.startswith("0092")):
            aparty=aparty[4:]
        if(aparty.startswith("+92")):
            aparty=aparty[3:]
        if(aparty.startswith("092")):
            aparty=aparty[3:]
        if(aparty.endswith(".0")):
            aparty=aparty[:-2]
        if(aparty.startswith("0")):
            aparty=aparty[1:]


        bparty = df.loc[index, 'BParty']
        
        #check if it starts with 92
        if(bparty.startswith("92")):
            bparty=bparty[2:]
        if(bparty.startswith("0092")):
            bparty=bparty[4:]
        if(bparty.startswith("+92")):
            bparty=bparty[3:]
        if(bparty.startswith("092")):
            bparty=bparty[3:]
        if(bparty.endswith(".0")):
            bparty=bparty[:-2]
        if(aparty.startswith("0")):
            bparty=bparty[1:]

        ts = df.loc[index, 'ts']
        # d = datetime.strptime(ts, "%Y-%m-%d%H:%M:%S")
        
        ts = str(ts)
        print(ts)
        tst = df.loc[index, 'tst']
        tst = str(tst)

        ts = ts +" "+tst

        duration = df.loc[index, 'Duration']
        if(type(duration) != str):
            duration =  str(duration)
        if(duration.endswith(".0")):
            duration=duration[:-2]

        cellid = df.loc[index, 'cellid']
        Imei = df.loc[index, 'Imei']
        Imei = Imei.astype(str)
        if(Imei.endswith(".0")):
            Imei=Imei[:-2]
        Imsi = df.loc[index, 'Imsi']
        Imsi = Imsi.astype(str)
        if(Imsi.endswith(".0")):
            Imsi=Imsi[:-2]
        calltype = df.loc[index, 'CallType']
        direction = df.loc[index, 'Direction']
        sitelocation = df.loc[index, 'SiteAddress']
        #operator = df.loc[index,'operator']
        operator = "telenor"
        source = pd.NaT
        destination = pd.NaT
       
        #p = CDR(aparty=aparty, bparty=bparty, ts=ts, duration=duration, cellid=cellid, imei=Imei, imsi=Imsi, calltype=calltype, direction=direction, SiteAddress=sitelocation, caseid=cc , cdrlist=cd,operator=operator)
        bulk_mgr.add(BTS(aparty=aparty, bparty=bparty, ts=ts, duration=duration, cellid=cellid, imei=Imei, imsi=Imsi, calltype=calltype, direction=direction, SiteAddress=sitelocation, caseid=cc , cdrlist=cd,operator=operator,source = source, destination=destination))
  
        #p.save()
        count = index+1;

    bulk_mgr.done()



#first jazz format
def btsjazz1(df,case_id,filename):

    name = filename.split(".")
   
    new_name = int(name[0],16)

    #getting case id
    cc = Cases.objects.get(id=case_id)
    print(cc.id)

    df["IMSI"] = pd.NaT
    df["Cell ID"] = new_name
    df["Site"] = pd.NaT
  
    df['type'] = np.where(df['Duration']!= 0, "call", "sms")
    df = df[[ "Call Type", "A-Party","B-Party","Date & Time","Duration","Cell ID","IMEI","IMSI","type","Site"]]

    df.rename(columns={'Date & Time': 'ts',"Call Type":"Direction","type":"CallType","Site":"SiteAddress",
        "A-Party":"Aparty","B-Party":"BParty", "Cell ID":"cellid", "IMEI":"Imei","IMSI":"Imsi"}, inplace=True)
   
    print(df)
    filext = filename.split(".")
    filextt = filext[-1]
    #creating a cdr list record
    reference = df.loc[1, 'Aparty']
    ref = str(reference)
        
    
    cd = BTSList(reference=reference, operator="jazz", caseid=cc )
    cdrlistid = cd.save()

    df['Aparty'] = df['Aparty'].astype(str)
    df['BParty'] = df['BParty'].astype(str)
    data = []
    bulk_mgr = BulkCreateManager(chunk_size=500)
    for index, row in df.iterrows():

        aparty = df.loc[index, 'Aparty']
        
        #check if it starts with 92
        if(aparty.startswith("92")):
            aparty=aparty[2:]
        if(aparty.startswith("0092")):
            aparty=aparty[4:]
        if(aparty.startswith("0")):
            aparty=aparty[1:]
        if(aparty.startswith("+92")):
            aparty=aparty[3:]
        if(aparty.startswith("092")):
            aparty=aparty[3:]
        if(aparty.endswith(".0")):
            aparty=aparty[:-2]


        bparty = df.loc[index, 'BParty']
        
        #check if it starts with 92
        if(bparty.startswith("92")):
            bparty=bparty[2:]
        if(bparty.startswith("0")):
            bparty=bparty[1:]
        if(bparty.startswith("0092")):
            bparty=bparty[4:]
        if(bparty.startswith("+92")):
            bparty=bparty[3:]
        if(bparty.startswith("092")):
            bparty=bparty[3:]
        if(bparty.endswith(".0")):
            bparty=bparty[:-2]


        ts = df.loc[index, 'ts']
        ts = pd.to_datetime(ts)
        ts = str(ts)


        duration = df.loc[index, 'Duration']
        cellid = df.loc[index, 'cellid']
        
        Imei = df.loc[index, 'Imei']
        Imei = Imei.astype(str)
        if(Imei.endswith(".0")):
            Imei=Imei[:-2]
        Imsi = df.loc[index, 'Imsi']
        

        calltype = df.loc[index, 'CallType']
        direction = df.loc[index, 'Direction']
        dtemp = direction.split()
        direction = dtemp[0].lower()

        sitelocation = df.loc[index, 'SiteAddress']
        source = pd.NaT
        destination = pd.NaT
        
        bulk_mgr.add(BTS(aparty=aparty, bparty=bparty, ts=ts, duration=duration, cellid=cellid, imei=Imei, imsi=Imsi, calltype=calltype, direction=direction, SiteAddress=sitelocation, caseid=cc , cdrlist=cd ,source = source, destination=destination,operator="jazz"))
  
       
        # p = BTS(aparty=aparty, bparty=bparty, ts=ts, duration=duration, cellid=cellid, imei=Imei, imsi=Imsi, calltype=calltype, direction=direction, SiteAddress=sitelocation, caseid=cc , cdrlist=cd ,source = source, destination=destination)
        # p.save()
        # count = index+1;
        #data.append([aparty,bparty,"jazz",ts,duration,cellid,Imei,Imsi,calltype,direction,filextt,sitelocation,cc.id, cc.createdat,source,destination])
        count = index+1;

    #dfn = pd.DataFrame(data, columns=['aparty','bparty','operator','ts','duration','lac_cellid','imei','imsi','call_type','direction','filetype','site_address','CDR_id','cdr_dt','source','destination'])
    #nnn = "csv/"+aparty+".csv"
    #dfn.to_csv(nnn)
    bulk_mgr.done()
#first zong bts format
def btszong1(df,case_id,filename):

    #getting case id
    cc = Cases.objects.get(id=case_id)
    print(cc.id)

    df["IMSI"] = pd.NaT
    df["Cell_id"] = df["LAC_id"].astype(str)+df["Cell_id"].astype(str)
    df["Site"] = pd.NaT
    df['DIR_FLG'] = np.where(df['DIR_FLG']== "O", "outgoing", "incoming")
  
    df['type'] = np.where(df['DRTN']!= 0, "call", "sms")
    df = df[[ "DLD_NO", "CLD_IMIE","DLG_NO","CLG_IMEI","DIR_FLG","CLR_OEPRATOR","DRTN","STRT_TM","type","Cell_id","Site","IMSI"]]

    df.rename(columns={'STRT_TM': 'ts',"DIR_FLG":"Direction","type":"CallType","Site":"SiteAddress",
        "DLD_NO":"Aparty","DLG_NO":"BParty", "Cell_id":"cellid", "CLD_IMIE":"Imei","CLG_IMEI":"Imei2","IMSI":"Imsi","DRTN":"Duration"}, inplace=True)
   
    print(df)
    filext = filename.split(".")
    filextt = filext[-1]
    #creating a cdr list record
    reference = df.loc[1, 'Aparty']
    ref = str(reference)
        
    
    cd = BTSList(reference=reference, operator="zong", caseid=cc )
    cdrlistid = cd.save()

    df['Aparty'] = df['Aparty'].astype(str)
    df['BParty'] = df['BParty'].astype(str)
    data = []
    bulk_mgr = BulkCreateManager(chunk_size=500)
    for index, row in df.iterrows():

        aparty = df.loc[index, 'Aparty']
        
        #check if it starts with 92
        if(aparty.startswith("92")):
            aparty=aparty[2:]
        if(aparty.startswith("0092")):
            aparty=aparty[4:]
        if(aparty.startswith("+92")):
            aparty=aparty[3:]
        if(aparty.startswith("092")):
            aparty=aparty[3:]
        if(aparty.endswith(".0")):
            aparty=aparty[:-2]


        bparty = df.loc[index, 'BParty']
        
        #check if it starts with 92
        if(bparty.startswith("92")):
            bparty=bparty[2:]
        if(bparty.startswith("0092")):
            bparty=bparty[4:]
        if(bparty.startswith("+92")):
            bparty=bparty[3:]
        if(bparty.startswith("092")):
            bparty=bparty[3:]
        if(bparty.endswith(".0")):
            bparty=bparty[:-2]


        ts = df.loc[index, 'ts']
        ts = pd.to_datetime(ts)
        ts = str(ts)


        duration = df.loc[index, 'Duration']
        cellid = df.loc[index, 'cellid']
        
        Imei = df.loc[index, 'Imei']
        Imei = Imei.astype(str)
        if(Imei.endswith(".0")):
            Imei=Imei[:-2]
        Imsi = df.loc[index, 'Imsi']
        

        calltype = df.loc[index, 'CallType']
        direction = df.loc[index, 'Direction']
        Imei2 = df.loc[index, 'Imei2']
        dtemp = direction.split()
        direction = dtemp[0].lower()

        sitelocation = df.loc[index, 'SiteAddress']
        source = pd.NaT
        destination = pd.NaT
        bulk_mgr.add(BTS(aparty=aparty, bparty=bparty, ts=ts, duration=duration, cellid=cellid, imei=Imei, imsi=Imsi, calltype=calltype, direction=direction, SiteAddress=sitelocation, caseid=cc , cdrlist=cd ,source = source, destination=destination,operator="zong"))
  
       
        # p = BTS(aparty=aparty, bparty=bparty, ts=ts, duration=duration, cellid=cellid, imei=Imei, imsi=Imsi, calltype=calltype, direction=direction, SiteAddress=sitelocation, caseid=cc , cdrlist=cd ,source = source, destination=destination, imei2=Imei2)
        # p.save()
        # count = index+1;
        #data.append([aparty,bparty,"zong",ts,duration,cellid,Imei,Imsi,calltype,direction,filextt,sitelocation,cc.id, cc.createdat,source,destination])
        count = index+1;

    #dfn = pd.DataFrame(data, columns=['aparty','bparty','operator','ts','duration','lac_cellid','imei','imsi','call_type','direction','filetype','site_address','CDR_id','cdr_dt','source','destination'])
    
    #nnn = "csv/"+aparty+".csv"
    #dfn.to_csv(nnn)
    bulk_mgr.done()
#first zong bts format
def btsufone1(df,case_id,filename):

    #getting case id
    cc = Cases.objects.get(id=case_id)
    print(cc.id)    
  
    df['type'] = np.where(df['Call_Duration']!= 0, "call", "sms")
    df = df[[ "CALL_START_DT", "IMEI","IMSI","A_Number","B_Number","Call_Start_Time","Call_Duration","Cell_ID","type","CALL_INBOUND_OUTBOUND_DESC","LOCATION"]]

    df.rename(columns={'Call_Start_Time': 'ts',"CALL_INBOUND_OUTBOUND_DESC":"Direction","type":"CallType","LOCATION":"SiteAddress",
        "A_Number":"Aparty","B_Number":"BParty", "Cell_ID":"cellid", "IMEI":"Imei","IMSI":"Imsi","Call_Duration":"Duration"}, inplace=True)
   
    print(df)
    filext = filename.split(".")
    filextt = filext[-1]
  
    #creating a cdr list record
    reference = df.loc[1, 'Aparty']
    ref = str(reference)
        
    
    cd = BTSList(reference=reference, operator="ufone", caseid=cc )
    cdrlistid = cd.save()

    df['Aparty'] = df['Aparty'].astype(str)
    df['BParty'] = df['BParty'].astype(str)
    data = []
    bulk_mgr = BulkCreateManager(chunk_size=500)
    for index, row in df.iterrows():

        aparty = df.loc[index, 'Aparty']
        
        #check if it starts with 92
        if(aparty.startswith("92")):
            aparty=aparty[2:]
        if(aparty.startswith("0092")):
            aparty=aparty[4:]
        if(aparty.startswith("+92")):
            aparty=aparty[3:]
        if(aparty.startswith("092")):
            aparty=aparty[3:]
        if(aparty.endswith(".0")):
            aparty=aparty[:-2]


        bparty = df.loc[index, 'BParty']
        
        #check if it starts with 92
        if(bparty.startswith("92")):
            bparty=bparty[2:]
        if(bparty.startswith("0092")):
            bparty=bparty[4:]
        if(bparty.startswith("+92")):
            bparty=bparty[3:]
        if(bparty.startswith("092")):
            bparty=bparty[3:]
        if(bparty.endswith(".0")):
            bparty=bparty[:-2]


        ts = df.loc[index, 'ts']
        ts = str(ts)

        ts = pd.to_datetime(ts)
        ts = str(ts)


        duration = df.loc[index, 'Duration']
        cellid = df.loc[index, 'cellid']
        
        Imei = df.loc[index, 'Imei']
        Imei = Imei.astype(str)
        if(Imei.endswith(".0")):
            Imei=Imei[:-2]
        Imsi = df.loc[index, 'Imsi']
        

        calltype = df.loc[index, 'CallType']
        direction = df.loc[index, 'Direction']
        
        dtemp = direction.split()
        direction = dtemp[0].lower()

        sitelocation = df.loc[index, 'SiteAddress']
        source = pd.NaT
        destination = pd.NaT
        
        bulk_mgr.add(BTS(aparty=aparty, bparty=bparty, ts=ts, duration=duration, cellid=cellid, imei=Imei, imsi=Imsi, calltype=calltype, direction=direction, SiteAddress=sitelocation, caseid=cc , cdrlist=cd ,source = source, destination=destination,operator="ufone"))
  
        # p = BTS(aparty=aparty, bparty=bparty, ts=ts, duration=duration, cellid=cellid, imei=Imei, imsi=Imsi, calltype=calltype, direction=direction, SiteAddress=sitelocation, caseid=cc , cdrlist=cd ,source = source, destination=destination)
        # p.save()
        # count = index+1;
        #data.append([aparty,bparty,"ufone",ts,duration,cellid,Imei,Imsi,calltype,direction,filextt,sitelocation,cc.id, cc.createdat,source,destination])
        count = index+1;

   # dfn = pd.DataFrame(data, columns=['aparty','bparty','operator','ts','duration','lac_cellid','imei','imsi','call_type','direction','filetype','site_address','CDR_id','cdr_dt','source','destination'])
    #nnn = "csv/"+aparty+".csv"
    #dfn.to_csv(nnn)
    bulk_mgr.done()

#first telnor bts format
def btstelenor1(df,case_id,filename):

    #getting case id
    cc = Cases.objects.get(id=case_id)
    print(cc.id)
    df['type'] = np.where(df['Call_Network_Volume']!= 0, "call", "sms") 

    if 'Cell_Lac_Id' in df.columns:
        df["Cell_Lac_Id"] = df["Cell_Lac_Id"].astype(str)+df["Cell_Site_Id"].astype(str)
        df['B-Party'] = np.where(df['MSISDN'] == df['CALL_ORIG_NUM'],df['CALL_DIALED_NUM'], df['CALL_ORIG_NUM'])
        df = df[[ "MSISDN", "CALL_ORIG_NUM","B-Party","IMSI","IMEI","CALL_START_DT_TM","INBOUND_OUTBOUND_IND","Call_Network_Volume","type","Cell_Lac_Id","Location","LAT","LONGITUDE"]]
        df.rename(columns={'CALL_START_DT_TM': 'ts',"INBOUND_OUTBOUND_IND":"Direction","type":"CallType","Location":"SiteAddress",
        "MSISDN":"Aparty","B-Party":"BParty", "Cell_Lac_Id":"cellid", "IMEI":"Imei","IMSI":"Imsi","Call_Network_Volume":"Duration"}, inplace=True)
    else:
        df["Cell_Lac_Id"] = df["Lac_Id"].astype(str)+df["Site_Id"].astype(str)
        df["INBOUND_OUTBOUND_IND"] = np.where(df['INBOUND_OUTBOUND_IND']== 2, "incomming", "outgoing")
        df['B-Party'] = df['CALL_ORIG_NUM']
        df = df[[ "MSISDN", "CALL_ORIG_NUM","B-Party","IMSI","IMEI","CALL_START_DT_TM","INBOUND_OUTBOUND_IND","Call_Network_Volume","type","Cell_Lac_Id","LOCATION","LAT","LONGITUDE"]]
        df.rename(columns={'CALL_START_DT_TM': 'ts',"INBOUND_OUTBOUND_IND":"Direction","type":"CallType","LOCATION":"SiteAddress",
        "MSISDN":"Aparty","B-Party":"BParty", "Cell_Lac_Id":"cellid", "IMEI":"Imei","IMSI":"Imsi","Call_Network_Volume":"Duration"}, inplace=True)

    
    

    
   
    filext = filename.split(".")
    filextt = filext[-1]
  

   
    #creating a cdr list record
    reference= df['Aparty'].iloc[0]
   # reference = df.loc[2, 'Aparty']
    #reference = df.loc[1, 'Aparty']
    
    ref = str(reference)
        
    df['Aparty'] = df['Aparty'].astype(str)
    df['BParty'] = df['BParty'].astype(str)
    df['Duration'] = df['Duration'].astype(str)
    cd = BTSList(reference=reference, operator="telenor", caseid=cc )
    cdrlistid = cd.save()

    data = []
    bulk_mgr = BulkCreateManager(chunk_size=500)

    for index, row in df.iterrows():


        aparty = row['Aparty']
       
       
        
        
        #check if it starts with 92
        if(aparty.startswith("92")):
            aparty=aparty[2:]
        if(aparty.startswith("0092")):
            aparty=aparty[4:]
        if(aparty.startswith("+92")):
            aparty=aparty[3:]
        if(aparty.startswith("092")):
            aparty=aparty[3:]
        if(aparty.endswith(".0")):
            aparty=aparty[:-2]


        bparty = row['BParty']
        
        #check if it starts with 92
        if(bparty.startswith("92")):
            bparty=bparty[2:]
        if(bparty.startswith("0092")):
            bparty=bparty[4:]
        if(bparty.startswith("+92")):
            bparty=bparty[3:]
        if(bparty.startswith("092")):
            bparty=bparty[3:]
        if(bparty.endswith(".0")):
            bparty=bparty[:-2]



        ts = row['ts']
        ts = str(ts)

        ts = pd.to_datetime(ts)
        


        duration = row['Duration']
        
        #check if it starts with 92
        if(duration.endswith(".0")):
            duration=duration[:-2]




        cellid = row['cellid']
        
        Imei = row['Imei']
        Imei = str(Imei)
       
        if(Imei.endswith(".0")):
            Imei=Imei[:-2]
        Imsi = row['Imsi']
        

        calltype = row['CallType']
        if 'Cell_Lac_Id' in df.columns:
            direction = row['Direction']
            
            dtemp = str(direction).split()
            direction = dtemp[0].lower()
        else:
            direction = row['Direction']
            dtemp = str(direction).split()
            direction = dtemp[0].lower()


        sitelocation = row['SiteAddress']
        source = row['LAT']
        destination = row['LONGITUDE']
        
       
        # p = BTS(aparty=aparty, bparty=bparty, ts=ts, duration=duration, cellid=cellid, imei=Imei, imsi=Imsi, calltype=calltype, direction=direction, SiteAddress=sitelocation, caseid=cc , cdrlist=cd ,source = source, destination=destination)
        # p.save()
        bulk_mgr.add(BTS(aparty=aparty, bparty=bparty, ts=ts, duration=duration, cellid=cellid, imei=Imei, imsi=Imsi, calltype=calltype, direction=direction, SiteAddress=sitelocation, caseid=cc , cdrlist=cd ,source = source, destination=destination, operator="telenor"))
        #data.append([aparty,bparty,"telenor",ts,duration,cellid,Imei,Imsi,calltype,direction,filextt,sitelocation,cc.id, cc.createdat,source,destination])
        count = index+1;

    #dfn = pd.DataFrame(data, columns=['aparty','bparty','operator','ts','duration','lac_cellid','imei','imsi','call_type','direction','filetype','site_address','CDR_id','cdr_dt','source','destination'])
    #nnn = "csv/"+aparty+".csv"
    #dfn.to_csv(nnn)
    bulk_mgr.done()

