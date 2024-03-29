from django.shortcuts import render
from django.shortcuts import HttpResponse,redirect
from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from Link2.models import saved_models,List
import pandas as pd
from django.core.files.base import ContentFile
import pickle
import os
import datetime
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import confusion_matrix, roc_auc_score, roc_curve
from sklearn.preprocessing import LabelEncoder,OneHotEncoder
from django.http import JsonResponse
from django.forms.models import model_to_dict

from sklearn.tree import DecisionTreeClassifier
from sklearn.neighbors import KNeighborsClassifier
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.svm import SVC
from sklearn.linear_model import LogisticRegression
from sklearn.naive_bayes import GaussianNB
import numpy as np
import math
import scipy.stats as ss
import copy
from matplotlib import pyplot


def Link5(request):
    if request.user.is_authenticated and request.user.profile.ifTeacher:
        allmodels=saved_models.objects.all()
        all_items=List.objects.all()
        modeldict={'modelList':[],'all_items':all_items}
        for i in range(0,len(allmodels)):
            namelist=allmodels[i].name.split(',,')
            if len(namelist) == 1:
                #len =1 means this is an external model. This string(ExternalFile58091645) has been used to identify this in frontEnd. This is not a good approach, but does the work for now
                tmpList=["ExternalFile58091645",allmodels[i].name,"","","",""]
                modeldict['modelList'].append(tmpList)
                modeldict['modelList'][i].append(allmodels[i].model.url[20:])
                modeldict['modelList'][i].append(allmodels[i].id)
                continue
            modeldict['modelList'].append(namelist)
            modeldict['modelList'][i].append(allmodels[i].model.url[20:])
            modeldict['modelList'][i].append(allmodels[i].id)
        print(modeldict['modelList'])
        return render(request, 'Link5.html', modeldict)
    return redirect('login_T')

def rowcol(request):
    if request.method == 'POST':
        try:
            train_file = request.FILES['train']
            request.session['train_name'] = train_file.name
            test_file = request.FILES['test']
            train_dataset=pd.read_csv(train_file)
            test_dataset=pd.read_csv(test_file)
            count_row_train, count_col_train = train_dataset.shape
            count_row_test, count_col_test = test_dataset.shape
            
            train_df=train_dataset
            test_df=test_dataset
            request.session['train_df'] = train_dataset
            request.session['test_df'] = test_dataset
            train_lst=list(train_dataset)
            test_lst=list(test_dataset)

            train_df1=train_df[:10]
            test_df1=test_df[:10]

            return render(request, 'Link5_rc.html', {'train_arr':train_lst,'train_cols':count_col_train,'train_rows':count_row_train,'train_data1':train_df1.to_html(classes=["table table-bordered"]),  'test_arr':test_lst,'test_cols':count_col_test,'test_rows':count_row_test,'test_data1':test_df1.to_html(classes=["table table-bordered"])})
        except:
            return HttpResponse('ERROR')
    else:
        return redirect('Link5')
            
def prec(request):
    if request.method == 'POST':
        checks = request.POST.getlist('checks[]')
        target = request.POST['target']
        algo=request.POST.getlist('algo[]')
        checks = list(map(int, checks))
        #--mm-mm--m-m-mmmmm--m-m-m--m-m-------mmmmm----------mmmmmmmmmmm-m--m-m-mm--m
        request.session['colnos'] = checks

        target=int(target)
        request.session['y_col'] = target
        train_df=request.session['train_df']
        x=train_df.iloc[:,checks].values
        y=train_df.iloc[:,target].values
        #preprocessing:
        dtypes_list= list(train_df.dtypes)
        categorical_lst=[]
        for i in range(0,len(checks)):
            if(dtypes_list[checks[i]]=='object'):
                categorical_lst.append(i)
        
        labelencoder = LabelEncoder()
        for i in categorical_lst:
            x[:,i]=labelencoder.fit_transform(x[:,i])
            
        if len(categorical_lst)!=0:
            oneh=OneHotEncoder(categorical_features=categorical_lst)
            x=oneh.fit_transform(x).toarray()
        '''
        avoid dummy variable
        '''
        sc=StandardScaler()
        x=sc.fit_transform(x)
        #for y:-
        if dtypes_list[target]=='object':
            y=labelencoder.fit_transform(y)
        
        regnames=[]
        regList=[]

        for i in algo:
            if i=='dt':
                regressor=DecisionTreeClassifier(random_state=0)
                regressor.fit(x,y)
                regList.append(regressor)
                regnames.append('Decision Tree')
            elif i=='knn':
                regressor=KNeighborsClassifier(n_neighbors=5,metric='minkowski',p=2)
                regressor.fit(x,y)
                regList.append(regressor)
                regnames.append('KNN')
            elif i=='rf':
                regressor=RandomForestClassifier(n_estimators=500,random_state=0)
                regressor.fit(x,y)
                regList.append(regressor)
                regnames.append('Random Forest')
            elif i=='svm':
                regressor=SVC(kernel='linear',random_state=0, probability=True)
                regressor.fit(x,y)
                regList.append(regressor)
                regnames.append('SVM')
            elif i=='lr':
                regressor=LogisticRegression(random_state=0)
                regressor.fit(x,y)
                regList.append(regressor)
                regnames.append('Logistic Regression')
            elif i=='nb':
                regressor=GaussianNB()
                regressor.fit(x,y)
                regList.append(regressor)
                regnames.append('Naive Bayes')
            elif i=='xgb':
                regressor=GradientBoostingClassifier()
                regressor.fit(x,y)
                regList.append(regressor)
                regnames.append('XGBoost')
            request.session['regnames'] = regnames
            request.session['regList'] = regList

        return HttpResponse('')
    else:
        return redirect('Link5')

def prec_(request):
    if request.method == 'POST':
        checks = request.POST.getlist('checks_[]')
        target = request.POST['target_']
        typedata=request.POST.get('typedata_')
        checks = list(map(int, checks))
        target=int(target)

        print(typedata)
        #global test_df
        test_df=request.session['test_df']
        x=test_df.iloc[:,checks].values
        y=test_df.iloc[:,target].values.astype('int64')

        train_df=request.session['train_df']
        x_tr=train_df.iloc[:,checks].values
        y_tr=train_df.iloc[:,target].values
        #preprocessing:
        dtypes_list= list(test_df.dtypes)
        categorical_lst=[]
        for i in range(0,len(checks)):
            if(dtypes_list[checks[i]]=='object'):
                categorical_lst.append(i)
        
        labelencoder = LabelEncoder()
        for i in categorical_lst:
            x[:,i]=labelencoder.fit_transform(x[:,i])
            x_tr[:,i]=labelencoder.fit_transform(x_tr[:,i])
            
        if len(categorical_lst)!=0:
            oneh=OneHotEncoder(categorical_features=categorical_lst)
            x=oneh.fit_transform(x).toarray()
            x_tr=oneh.fit_transform(x_tr).toarray()
        '''
        avoid dummy variable
        '''

        sc=StandardScaler()
        x=sc.fit_transform(x)
        x_tr=sc.fit_transform(x_tr)
        
        regList=request.session['regList']
        regnames=request.session['regnames']
        print(regnames)
        resultDict={'regs':len(regList),'regnames':regnames,'auc':[],'tp':[],'tn':[],'fn':[],'fp':[],'accuracy':[],'recall':[],'precision':[],'f1':[]}

        if(typedata=='train'):
            x=x_tr
            y=y_tr


        for i in range(0,len(regList)):
            y_pred=regList[i].predict(x)
            cm=confusion_matrix(y,y_pred.round())
            # predict probabilities
            probs = regList[i].predict_proba(x)
            # keep probabilities for the positive outcome only
            probs = probs[:, 1]
            auc_value = roc_auc_score(y, probs)
            resultDict['auc'].append(auc_value)
            resultDict['tp'].append(int(cm[0][0]))
            resultDict['tn'].append(int(cm[1][1]))
            resultDict['fn'].append(int(cm[0][1]))
            resultDict['fp'].append(int(cm[1][0]))
            accuracy=(cm[0][0]+cm[1][1])/(cm[0][0]+cm[1][0]+cm[0][1]+cm[1][1])
            resultDict['accuracy'].append(round(accuracy,4))
            recall=cm[0][0]/(cm[0][0]+cm[0][1])
            precision=cm[0][0]/(cm[0][0]+cm[1][0])
            resultDict['recall'].append(round(recall,4))
            resultDict['precision'].append(round(precision,4))
            resultDict['f1'].append(round((2*(recall * precision) / (recall + precision)),4))
        #Next line to be used in savemodel function
        request.session['f1']=resultDict['f1']

        #TOPSIS
        arr=[]
        for i in range(0,resultDict['regs']):
            arr.append([])
            arr[i].append(resultDict['tp'][i])
            arr[i].append(resultDict['tn'][i])
            arr[i].append(resultDict['fn'][i])
            arr[i].append(resultDict['fp'][i])
            arr[i].append(resultDict['accuracy'][i])
            arr[i].append(resultDict['recall'][i])
            arr[i].append(resultDict['precision'][i])
            arr[i].append(resultDict['f1'][i])
        print(arr)
        w =[1,1,1,1,1,1,1,1]
        f=['+','+','-','-','+','+','+','+']
        sqr=[]
        nm=[]
        #ds=pd.read_csv('topsis.csv')
        target1=resultDict['regnames']

        ord_arr = copy.deepcopy(arr)
        ds=arr
        rows=len(arr)
        cols=len(arr[0])

        for i in range(0,cols):
            sum1=0
            for j in range(0,rows):
                sum1=sum1+(ds[j][i]*ds[j][i])
            sum1=math.sqrt(sum1)
            sqr.append(sum1)
        sum2=0 
        for i in range(0,cols):
            sum2=sum2+w[i] 
        for i in range(0,cols):
            w[i]=w[i] /sum2
        for i in range(0,cols):
            for j in range(0,rows):
                ds[j][i]=(ds[j][i]/sqr[i])*w[i]
        max1=[]
        min1=[]
        best=[]
        worst=[]
        for i in range(0,cols):
            max2=-100000
            min2=100000
            for j in range(0,rows):
                if(ds[j][i]>max2):
                    max2=ds[j][i]
                if(ds[j][i]<min2):
                    min2=ds[j][i]
            if(f[i]=='+'):
                best.append(max2)
                worst.append(min2)
            elif(f[i]=='-'):
                best.append(min2)
                worst.append(max2)

        sip=[]
        sin=[]
        for i in range(0,rows):
            sumsip=0
            sumsin=0
            for j in range(0,cols):
                sumsip=sumsip+(ds[i][j]-best[j])*(ds[i][j]-best[j])
                sumsin=sumsin+(ds[i][j]-worst[j])*(ds[i][j]-worst[j])
            sip.append(math.sqrt(sumsip))
            sin.append(math.sqrt(sumsin))
        p=[]
        for i in range(0,rows):
            p.append(sin[i]/(sip[i]+sin[i]))

        print(p)
        #rank array, convert float to int, convert np arr to python list
        lst=(len(p)-ss.rankdata(p)+1).astype(int).tolist()

        print(lst)
        x = np.array(lst)
        unq=np.unique(x)
        unq=unq.tolist()
        
        for i in unq:
            count=0
            for ind,j in enumerate(lst):
                if(i==j):
                    lst[ind]=j+count
                    count=count+1
        print(lst)

        resultDict['models']=[]

        for j in range(0,len(lst)):
            i=lst.index(j+1)
            resultDict['models'].append(ord_arr[i])
            resultDict['models'][j].append(regnames[i])
            #next line to pass origninal index so that it can be used when save model button clicked
            resultDict['models'][j].append(i)

        return JsonResponse(resultDict,status=200)        
    else:
        return redirect('Link5')

    
def savemodel(request,mno):
    train_df=request.session['train_df']
    colnos=request.session['colnos']
    y_col=request.session['y_col']
    f1_list=request.session['f1']
    train_name=request.session['train_name']
    regnames=request.session['regnames']

    colList=list(train_df.columns)
    colnames=""
    for i in colnos:
        colnames+=colList[i]+','
    colnames+=','+colList[y_col]

    regList=request.session['regList']
    index=int(mno)
    modelname=train_name
    filename=train_name
    filename+='_'+str(len(colnos))+'-columns'+'_'+str(datetime.datetime.now())[:-7]+'.pkl'
    modelname+=',,'+colnames+',,'+regnames[index]+',,'+str(datetime.datetime.now())[:-7]+',,'+str(f1_list[index])
    
    model_to_save=regList[index]

    data_entry = saved_models(name=modelname)
    content = pickle.dumps(model_to_save)
    fid = ContentFile(content)
    data_entry.model.save(filename, fid)
    fid.close()
    
    return JsonResponse({'stat':'ok'},status=200)

'''
def smml(request):
    if request.method == 'POST':
        try:
            test_file_sm = request.FILES['test_sm']

            test_dataset_sm=pd.read_csv(test_file_sm)
            count_row_test_sm, count_col_test_sm = test_dataset_sm.shape
            request.session['test_df_sm']=test_dataset_sm
            test_lst_sm=list(test_dataset_sm)
            
            request.session['test_lstt_sm']=test_lst_sm
            test_df1_sm=test_dataset_sm[:10]
            allmodels=saved_models.objects.all()
            modeldict={'modelList':[],'test_arr_sm':test_lst_sm,'test_cols_sm':count_col_test_sm,'test_rows_sm':count_row_test_sm,'test_data1_sm':test_df1_sm.to_html(classes=["table table-bordered"])}
            for i in range(0,len(allmodels)):
                namelist=allmodels[i].name.split(',,')
                modeldict['modelList'].append(namelist)
                modeldict['modelList'][i].append(allmodels[i].model.url[20:])
                modeldict['modelList'][i].append(allmodels[i].id)
            return render(request, 'sm_uploaded.html', modeldict)
        except:
            return HttpResponse('ERROR')
    else:
        return redirect('Link5')
'''

def smml(request):
    if request.method == 'POST':
        try:
            test_file_sm = request.FILES['test_sm']
            request.session['filename_sm_pred'] = test_file_sm.name
            torp=request.POST['torp']

            test_dataset_sm=pd.read_csv(test_file_sm)
            count_row_test_sm, count_col_test_sm = test_dataset_sm.shape
            request.session['test_df_sm']=test_dataset_sm
            test_lst_sm=list(test_dataset_sm)
            
            request.session['test_lstt_sm']=test_lst_sm
            test_df1_sm=test_dataset_sm[:10]
            allmodels=saved_models.objects.all()
            modeldict={'modelList':[],'test_arr_sm':test_lst_sm,'test_cols_sm':count_col_test_sm,'test_rows_sm':count_row_test_sm,'test_data1_sm':test_df1_sm.to_html(classes=["table table-bordered"])}
            for i in range(0,len(allmodels)):
                namelist=allmodels[i].name.split(',,')
                modeldict['modelList'].append(namelist)
                modeldict['modelList'][i].append(allmodels[i].model.url[20:])
                modeldict['modelList'][i].append(allmodels[i].id)
            if torp=='t':
                return render(request, 'sm_uploaded.html', modeldict)
            else:
                return render(request, 'sm_uploaded_pred.html', modeldict)
        except:
            return HttpResponse('ERROR')
    else:
        return redirect('Link5')

def sm_pred(request):
    if request.method == 'POST':
        checks = request.POST.getlist('checks_[]')
        smid=request.POST['smodel']
        smid=int(smid)
        checks = list(map(int, checks))
        test_df_sm=request.session['test_df_sm']
        x=test_df_sm.iloc[:,checks].values

        #preprocessing:
        dtypes_list= list(test_df_sm.dtypes)
        categorical_lst=[]
        for i in range(0,len(checks)):
            if(dtypes_list[checks[i]]=='object'):
                categorical_lst.append(i)
        
        labelencoder = LabelEncoder()
        for i in categorical_lst:
            x[:,i]=labelencoder.fit_transform(x[:,i])
            
        if len(categorical_lst)!=0:
            oneh=OneHotEncoder(categorical_features=categorical_lst)
            x=oneh.fit_transform(x).toarray()

        sc=StandardScaler()
        x=sc.fit_transform(x)

        smodel=saved_models.objects.get(pk=smid)

        loaded_model = pickle.load(smodel.model)
        y_pred = loaded_model.predict(x)
        print(y_pred)
        print(test_df_sm)
        test_df_sm['prediction']=list(y_pred)
        print(test_df_sm)
        request.session['downloadFile']=test_df_sm
        resultDict={'result':'ok'}
        
        return JsonResponse(resultDict,status=200)   

    else:
        return redirect('Link5')

def downloadFile(request):
    dataframe=request.session['downloadFile']
    response = HttpResponse(content_type='text/csv')
    fname=request.session['filename_sm_pred']
    response['Content-Disposition'] = 'attachment; filename='+fname+' logs.csv'

    dataframe.to_csv(path_or_buf=response)
    return response

def VisualizePredData(request):
    if not request.user.is_authenticated or not request.user.profile.ifTeacher:
        return redirect('Link5')
    dataframe=request.session['downloadFile']
    return render(request, 'VisualizePredData.html', {'data_list':dataframe})


def sm_test(request):
    if request.method == 'POST':
        checks = request.POST.getlist('checks_[]')
        target = request.POST['target_']
        smid=request.POST['smodel']
        smid=int(smid)
        checks = list(map(int, checks))
        target=int(target)
        test_df_sm=request.session['test_df_sm']
        x=test_df_sm.iloc[:,checks].values
        y=test_df_sm.iloc[:,target].values.astype('int64')

        #preprocessing:
        dtypes_list= list(test_df_sm.dtypes)
        categorical_lst=[]
        for i in range(0,len(checks)):
            if(dtypes_list[checks[i]]=='object'):
                categorical_lst.append(i)
        
        labelencoder = LabelEncoder()
        for i in categorical_lst:
            x[:,i]=labelencoder.fit_transform(x[:,i])
            
        if len(categorical_lst)!=0:
            oneh=OneHotEncoder(categorical_features=categorical_lst)
            x=oneh.fit_transform(x).toarray()
        '''
        avoid dummy variable
        '''
        sc=StandardScaler()
        x=sc.fit_transform(x)
        
        if dtypes_list[target]=='object':
            y=labelencoder.fit_transform(y)
        
        sc=StandardScaler()
        x=sc.fit_transform(x)

        resultDict={'tp':0,'tn':0,'fn':0,'fp':0,'accuracy':0,'recall':0,'precision':0,'f1':0}

        smodel=saved_models.objects.get(pk=smid)

        loaded_model = pickle.load(smodel.model)
        y_pred = loaded_model.predict(x)
        cm = confusion_matrix(y,y_pred.round())

        resultDict['tp']=int(cm[0][0])
        resultDict['tn']=int(cm[1][1])
        resultDict['fn']=int(cm[0][1])
        resultDict['fp']=int(cm[1][0])
        resultDict['accuracy']=(cm[0][0]+cm[1][1])/(cm[0][0]+cm[1][0]+cm[0][1]+cm[1][1])
        recall=cm[0][0]/(cm[0][0]+cm[0][1])
        precision=cm[0][0]/(cm[0][0]+cm[1][0])
        resultDict['recall']=round(recall,4)
        resultDict['precision']=round(precision,4)
        resultDict['f1']=round((2*(recall * precision) / (recall + precision)),4)

        return JsonResponse(resultDict,status=200)        
    else:
        return redirect('Link5')
    
def delsm(request,smid):
    if not request.user.is_authenticated or not request.user.profile.ifTeacher:
        return redirect('Link5')
    sm=saved_models.objects.get(pk=int(smid))
    sm.delete()
    return JsonResponse({'result':'ok'},status=200)

def uploadModel(request):
    if not request.user.is_authenticated or not request.user.profile.ifTeacher:
        return redirect('Link5')
    if request.method == 'POST':
        try:
            uploadedModel = request.FILES['uploadedModel']
            modelName = request.POST['modelName']
            a=saved_models(name=modelName,model=uploadedModel)
            a.save()
        except:
            print("Error")
    return redirect('Link5')

