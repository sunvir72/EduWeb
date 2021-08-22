from django.shortcuts import render,redirect
from django.shortcuts import HttpResponse
from .models import List,studList,instructors,links,assignments,announcements,studRecords,questr,ques,resAccess,topic,qnr_attempt,qn_attempt,saved_models,practqn_attempt,extqnr,ext_attempt,saved_dataset,studentPractScore,practqn_attempt_resetted,practSummary
from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from django.contrib import messages
from django.db.models import Avg,Sum
from django.core.mail import send_mail
from django.conf import settings
from django.http import JsonResponse
from django.forms.models import model_to_dict
#from django.core import serializers
import pandas as pd
import numpy as np
import datetime
import csv
from django.views.generic import View
from django.template.loader import get_template
from .utils import render_to_pdf
from django.core.files.storage import default_storage
import pickle
import os

def Link2(request):
    if request.user.is_authenticated and not request.user.profile.ifTeacher:
        all_items=List.objects.filter()
        #reg=studlist.objects.filter(email=request.user.username)
        dct={'cid':[],'name':[],'regtd':[]}
        lst=[]
        for i in all_items:
            if studList.objects.filter(email=request.user.username,course=i,stat=True).exists():
                lst.append((i.id,i.item,True,i.desc))
            else:
                lst.append((i.id,i.item,False,i.desc))
        return render(request, 'Link2.html', {'lst':lst})
        '''
            dct['cid'].append(i.id)
            dct['name'].append(i.item)
            if studList.objects.filter(email=request.user.username,course=i).exists():
                dct['regtd'].append(True)
            else:
                dct['regtd'].append(False)
        return render(request, 'Link2.html', {'dct':dct})
        '''
    elif request.user.is_authenticated and request.user.profile.ifTeacher:
        if request.method=='POST':
            it=request.POST['item']
            if List.objects.filter(item=it).exists():
                messages.warning(request,('Course already exists!'))
            else:
                a=List(item=it)
                a.save()
            all_items=List.objects.all
            return render(request, 'Link2.html', {'all_items':all_items})
        else:
            all_items=List.objects.all
            return render(request, 'Link2.html', {'all_items':all_items})
    else:
        return redirect('login_S')

def embfiles(request,cid):
	course=List.objects.get(pk=cid)
	files=saved_dataset.objects.filter(course=course)
	return render(request, 'embfiles.html', {'files':files,'cid':cid,'cname':course.item})

def add_dataset(request,cid):
	if request.method=='POST':
		name=request.POST['name']
		newds=request.FILES['newds']
		course=List.objects.get(pk=cid)
		a=saved_dataset(dataset=newds,course=course,name=name)
		a.save()
		return redirect('embfiles',cid=cid)
	return redirect('Link2')

def del_dataset(request,dsid,cid):
	if not request.user.is_authenticated or not request.user.profile.ifTeacher:
		return redirect('Link2')
	a=saved_dataset.objects.get(pk=dsid)
	a.delete()
	return redirect('embfiles',cid=cid)

def crossofff(request,list_id):
    if not request.user.is_authenticated:
        return redirect('Link2')
    item=List.objects.get(pk=list_id)
    em=request.user.username
    try:
        s=studList.objects.get(email=em,course=item)
        s.stat=True
        s.save()
        messages.success(request,('You have registered for this course successfully!'))
    except:
        messages.warning(request,('You are not eligible to register for this course!'))
    return redirect('Link2')

def courseRO(request,cid):
    if not request.user.is_authenticated:
        return redirect('Link2')
    course=List.objects.get(pk=cid)
    if studList.objects.filter(course=course,email=request.user.username).exists()==False:
    	messages.warning(request,('You have not registered for this course!'))
    	return redirect('Link2')
    i=instructors.objects.filter(course=course)
    l=links.objects.filter(course=course,islive=True)
    ass=assignments.objects.filter(course=course,islive=True)
    ann=announcements.objects.filter(course=course)
    topics=topic.objects.filter(course=course)

    try:
        it=studRecords.objects.get(email=request.user.username,course=course.item,date=datetime.datetime.now())
        it.sum_click+=1
        it.save()
    except:
        it=studRecords(name=request.user.first_name+' '+request.user.last_name,email=request.user.username,course=course.item,sum_click=1)
        it.save()
    return render(request, 'courseInfoRO.html', {'cid':cid,'course':course,'topics':topics,'i':i,'l':l,'ass':ass,'ann':ann})

curr_course="hh"
curr_cid="hhh"
def courseInfo(request,cid):
    if not request.user.is_authenticated or not request.user.profile.ifTeacher:
        return redirect('Link2')
    course=List.objects.get(pk=cid)
    global curr_course
    global curr_cid
    curr_course=course
    curr_cid=cid
    i=instructors.objects.filter(course=course)
    l=links.objects.filter(course=course)
    ass=assignments.objects.filter(course=course)
    ann=announcements.objects.filter(course=course)
    topics=topic.objects.filter(course=course)
    return render(request, 'courseInfo.html', {'course':course,'topics':topics,'i':i,'l':l,'ass':ass,'ann':ann,'cid':cid})

def Raccess(request,cid,rtype,topic):
    course=List.objects.get(pk=cid)
    try:
        a=resAccess.objects.get(email=request.user.username,rType=rtype,topic=topic,course=course.item,date=datetime.datetime.now())
        a.sum_click+=1
        a.save()
    except:
        a=resAccess(name=request.user.first_name+' '+request.user.last_name,email=request.user.username,rType=rtype,topic=topic,course=course.item)
        a.save()
    return HttpResponse('')

def updatecred(request,cid):
    if request.method=='POST':
        newcred=request.POST['Credits']
        cr=float(newcred)
        curr_course=List.objects.get(pk=cid)
        curr_course.cred=cr
        curr_course.save()
        return redirect('courseInfo',cid=curr_cid)
    else:
        return redirect('Link2')

def editsyll(request,cid):
    if request.method=='POST':
        newsyll=request.POST['new']
        curr_course=List.objects.get(pk=cid)
        curr_course.syllabus=newsyll
        curr_course.save()
        return JsonResponse({'neww':model_to_dict(curr_course)},status=200)
        #return redirect('courseInfo',cid=curr_cid)
    else:
        return redirect('Link2')

def editdesc(request,cid):
    if request.method=='POST':
        newdesc=request.POST['new']
        curr_course=List.objects.get(pk=cid)
        curr_course.desc=newdesc
        curr_course.save()
        return redirect('courseInfo',cid=curr_cid)
    else:
        return redirect('Link2')
    
def addTopic(request,cid):
    if request.method=='POST':
        new=request.POST['topic']
        curr_course=List.objects.get(pk=cid)
        it=topic(name=new,course=curr_course,islive=False)
        it.save()
        return JsonResponse({'neww':model_to_dict(it)},status=200)
    else:
        return redirect('Link2')

def delTopic(request,tid):
    if not request.user.is_authenticated or not request.user.profile.ifTeacher:
        return redirect('Link2')
    it=topic.objects.get(pk=tid)
    it.delete()
    return JsonResponse({'result':'ok'},status=200)

def addInst(request,cid):
    if request.method=='POST':
        newInst=request.POST['Instructor']
        print("Add Instructor")
        curr_course=List.objects.get(pk=cid)
        it=instructors(inst=newInst,course=curr_course)
        it.save()
        return JsonResponse({'neww':model_to_dict(it)},status=200)
    else:
        return redirect('Link2')

def delInst(request,instid):
    if not request.user.is_authenticated or not request.user.profile.ifTeacher:
        return redirect('Link2')
    it=instructors.objects.get(pk=instid)
    it.delete()
    return JsonResponse({'result':'ok'},status=200)
    #return redirect('courseInfo',cid=curr_cid)

def addLink(request,cid):
    if request.method=='POST':
        newLink=request.POST['Link']
        topic1=request.POST['topic_']
        level1=request.POST['level_']
        curr_course=List.objects.get(pk=cid)
        live=False
        print(newLink)
        print(topic1)
        print(level1)
        print(curr_course)
        print(live)
        it=links(link=newLink,topic=topic1,level=level1,course=curr_course,islive=live)
        it.save()
        return JsonResponse({'neww':model_to_dict(it)},status=200)
        #return redirect('courseInfo',cid=curr_cid)
    else:
        return redirect('Link2')

def delLink(request,linkid):
    if not request.user.is_authenticated or not request.user.profile.ifTeacher:
        return redirect('Link2')
    it=links.objects.get(pk=linkid)
    it.delete()
    return JsonResponse({'result':'ok'},status=200)
    #return redirect('courseInfo',cid=curr_cid)

def addannc(request,cid):
    if request.method=='POST':
        print("Add Announcement")
        newannc=request.POST['Announcement']
        curr_course=List.objects.get(pk=cid)
        it=announcements(annc=newannc,course=curr_course)
        it.save()
        size=announcements.objects.filter(course=curr_course).count()
        return JsonResponse({'neww':model_to_dict(it),'size':size},status=200)
    else:
        return redirect('Link2')

def delannc(request,anncid):
    if not request.user.is_authenticated or not request.user.profile.ifTeacher:
        return redirect('Link2')
    it=announcements.objects.get(pk=anncid)
    it.delete()
    return JsonResponse({'result':'ok'},status=200)

def addassign(request,cid):
    if request.method=='POST':
        print("Add Assignment")
        file = request.FILES['file']
        name1=request.POST['aname']
        topic1=request.POST['topic_']
        level1=request.POST['level_']
        curr_course=List.objects.get(pk=cid)
        a=assignments(name=name1,assign=file,topic=topic1,level=level1,course=curr_course)
        a.save()
        return JsonResponse({'fileid':a.id,'name':a.name,'fileurl':a.assign.url,'topic':a.topic,'level':a.level},status=200)
        #return redirect('courseInfo',cid=curr_cid)
    else:
        return redirect('Link2')
    
def delassign(request,assid):
    if not request.user.is_authenticated or not request.user.profile.ifTeacher:
        return redirect('Link2')
    a=assignments.objects.get(pk=assid)
    a.delete()
    return JsonResponse({'result':'ok'},status=200)
    #return redirect('courseInfo',cid=curr_cid)
    
stodel="hh"
curr_sl="hh"
studentid="hh"

def studlist(request,sidd):
    if not request.user.is_authenticated or not request.user.profile.ifTeacher:
        return redirect('Link2')
    item=List.objects.get(pk=sidd)
    global curr_sl
    global studentid
    studentid=sidd
    curr_sl=item
    sl=studList.objects.filter(course=item)
    return render(request, 'Link2_studlist.html', {'sl':sl,'sidd':sidd})

def addstud(request,list_id):
    if request.method=='POST':
    	crse=List.objects.get(pk=list_id)
    	name=request.POST['message']
    	name=name.replace("\r",",")
    	name=name.replace("\n","")
    	namelist=name.split(',')
    	subject = 'Course Invite'
    	message = 'This is an invite for the course: '+crse.item+'\n Click the below link to go to the registeration page \n \n http://sunvir.pythonanywhere.com/courses/ '
    	email_from = settings.EMAIL_HOST_USER
    	for i in namelist:
            if studList.objects.filter(email=i,course=crse).exists():
                print('Already exists: ',i)
            else:
                it=studList(email=i,course=crse)
                it.save()
    	recipient_list = namelist
    	try:
            send_mail(subject,message,email_from,recipient_list,fail_silently=False)
            return JsonResponse({'result':'ok'},status=200)
    	except:
    		return JsonResponse({'result':'notok'},status=200)
        #messages.success(request,('Email Invite sent successfully!'))
    else:
        return redirect('Link2')

    
def deleteStud(request,stud,sidd):
    if not request.user.is_authenticated or not request.user.profile.ifTeacher:
        return redirect('Link2')
    it=studList.objects.get(pk=stud)
    it.delete()
    return JsonResponse({'result':'ok'},status=200)
    #return redirect('studlist',sidd=sidd)

def studR(request):
    if not request.user.is_authenticated or not request.user.profile.ifTeacher:
        return redirect('Link2')
    srs=studRecords.objects.all()
    uniqcrs=List.objects.all().values_list('item', flat=True)
    crsfreq=[0]*len(uniqcrs)
    try:
        last_n = srs.order_by('-id')[:10]
    except:
        last_n = ras.order_by('-id')
    for i in range(0,len(uniqcrs)):
        crs_sum_click=srs.filter(course=uniqcrs[i])
        for j in crs_sum_click:
            crsfreq[i]+=j.sum_click
        #crsfreq.append(srs.filter(course=i).count())

    return render(request, 'studRecords.html', {'rows':srs.count(),'srs':last_n,'uniqcrs':list(uniqcrs),'crsfreq':crsfreq})

def RaccessT(request):
    if not request.user.is_authenticated or not request.user.profile.ifTeacher:
        return redirect('Link2')
    ras=resAccess.objects.all()
    try:
        last_n = ras.order_by('-id')[:10]
    except:
        last_n = ras.order_by('-id')
    rTypeSums={'rows':ras.count(),'ras':last_n,'link':0,'assignment':0,'questionnaire':0}
    for i in ras:
        rTypeSums[i.rType]+=i.sum_click
    return render(request, 'RaccessT.html', rTypeSums)
    
def RaTdown(request):
    allobj=resAccess.objects.all()
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="resource_access.csv"'

    writer = csv.writer(response)
    writer.writerow(['Name','Email','Course','Resource Type','Date','Last Time','Click sum'])

    for obj in allobj:
        writer.writerow([obj.name,obj.email,obj.course,obj.rType,obj.date,str(obj.time.hour) +':'+str(obj.time.minute),obj.sum_click])

    return response

def CaTdown(request):
    allobj=studRecords.objects.all()
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="course_access.csv"'

    writer = csv.writer(response)
    writer.writerow(['Name','Email','Course','Date','sum_click'])

    for obj in allobj:
        writer.writerow([obj.name,obj.email,obj.course,obj.date,obj.sum_click])

    return response

def deleteSR(request,sr):
    if not request.user.is_authenticated or not request.user.profile.ifTeacher:
        return redirect('Link2')
    item=studRecords.objects.get(pk=sr)
    item.delete()
    return redirect('studR')

def delete(request,list_id):
    if not request.user.is_authenticated or not request.user.profile.ifTeacher:
        return redirect('Link2')
    item=List.objects.get(pk=list_id)
    item.delete()
    return redirect('Link2')

def edit(request,cid):
    if request.method=='POST':
        newit=request.POST['item']
        curr_course=List.objects.get(pk=cid)
        curr_course.item=newit
        curr_course.save()
        return redirect('courseInfo',cid=curr_cid)
    else:
        return redirect('Link2')

def extq(request,cid):
    if not request.user.is_authenticated or not request.user.profile.ifTeacher:
        return redirect('Link2')
    course=List.objects.get(pk=cid)
    if request.method=='POST':
        course=List.objects.get(pk=cid)
        name=request.POST['extname']
        m=request.POST['mm']
        a=extqnr(name=name,mm=m,course=course)
        a.save()
        allobj=extqnr.objects.filter(course=course)
        return render(request, 'extq.html', {'allobj':allobj,'cid':cid})
    else:
        allobj=extqnr.objects.filter(course=course)
        return render(request, 'extq.html', {'allobj':allobj,'cid':cid})

def delext(request,cid,extid):
    if not request.user.is_authenticated or not request.user.profile.ifTeacher:
        return redirect('Link2')
    a=extqnr.objects.get(pk=extid)
    a.delete()
    return redirect('extq',cid=cid)

def editextmarks(request,ecid,extid):
    if not request.user.is_authenticated or not request.user.profile.ifTeacher:
        return redirect('Link2')
    newm=request.POST['newm']
    a=ext_attempt.objects.get(pk=ecid)
    a.marks=int(newm)
    a.save()
    return redirect('extcontent',extid=extid)

def extcontent(request,extid):
    if not request.user.is_authenticated or not request.user.profile.ifTeacher:
        return redirect('Link2')
    extq=extqnr.objects.get(pk=extid)
    course=extq.course
    stud=studList.objects.filter(course=course)
    if request.method=='POST':
        email=request.POST['studemail']
        m=request.POST['marks']
        a=ext_attempt(email=email,marks=m,extqnr=extq)
        a.save()
        allobj=ext_attempt.objects.filter(extqnr=extq)
        return render(request, 'extcontent.html', {'allobj':allobj,'extq':extq,'stud':stud,'extid':extid})
    else:
        allobj=ext_attempt.objects.filter(extqnr=extq)
        return render(request, 'extcontent.html', {'allobj':allobj,'extq':extq,'stud':stud,'extid':extid}) 

def bulkext(request,cid,extid):
    if not request.user.is_authenticated or not request.user.profile.ifTeacher:
        return redirect('Link2')
    if request.method=='POST':  
        extq=extqnr.objects.get(pk=extid)
        course=List.objects.get(pk=cid)
        studs=studList.objects.filter(course=course)
        allobj=ext_attempt.objects.filter(extqnr=extq)
        try:
            file = request.FILES['file']
            df=pd.read_csv(file,keep_default_na=False)
            r=df.shape[0]
            if (r>300):
                messages.warning(request,('Error! Maximum 300 entries allowed per upload'))
                return redirect('extcontent',extid=extid)
            #if not:
            df=df.iloc[:,:].values
            for i in range(0,r):
                ex=studs.filter(email=df[i][0]).exists()
                if(ex!=True):
                    messages.success(request,('Error! Make sure that each student in the file has been added to this course'))
                    return redirect('extcontent',extid=extid)
                if(allobj.filter(email=df[i][0]).exists()):
                    continue
                a=ext_attempt(email=df[i][0],marks=int(df[i][1]),extqnr=extq)                
                a.save()
            messages.success(request,('Entries uploaded successfully!'))
            return redirect('extcontent',extid=extid)
        except:
            messages.warning(request,('Error! Make sure uploaded file is in accordance with the sample file'))
            return redirect('extcontent',extid=extid)
    else:
        return redirect('Link2')



def delextcontent(request,extid,ecid):
    if not request.user.is_authenticated or not request.user.profile.ifTeacher:
        return redirect('Link2')
    a=ext_attempt.objects.get(pk=ecid)
    a.delete()
    return redirect('extcontent',extid=extid)

def quesRO(request,curr_c):
    if not request.user.is_authenticated:
        return redirect('Link2')
    curr_crse=List.objects.get(pk=curr_c)
    all_q=questr.objects.filter(course=curr_crse,islive=True)
    topics=topic.objects.filter(course=curr_crse,islive=True)
    return render(request, 'addqRO.html', {'all_q':all_q,'cr_crseid':curr_c,'topics':topics})

def quesr(request,cid):
    if not request.user.is_authenticated or not request.user.profile.ifTeacher:
        return redirect('Link2')
    curr_course=List.objects.get(pk=cid)
    if request.method=='POST':
        newq=request.POST['item']
        hrs1=request.POST['hrs']
        min1=request.POST['min']
        a=questr(name=newq,DT=datetime.datetime.now(),time=hrs1+':'+min1,course=curr_course,islive=False)
        a.save()

        all_q=questr.objects.filter(course=curr_course)
        topics=topic.objects.filter(course=curr_course)
        return render(request, 'addq.html', {'all_q':all_q,'cid':cid,'topics':topics})
    else:
        all_q=questr.objects.filter(course=curr_course)
        topics=topic.objects.filter(course=curr_course)
        return render(request, 'addq.html', {'all_q':all_q,'cid':cid,'topics':topics})

def changelive(request,cid,idd,act,type):
    if not request.user.is_authenticated or not request.user.profile.ifTeacher:
        return redirect('Link2')
    if type=='q':
        if act=='1':
            a=questr.objects.get(pk=idd)
            a.islive=False
            a.save()
        else:
            a=questr.objects.get(pk=idd)
            a.islive=True
            a.save()
        return redirect('quesr',cid=cid)
    else:
        if act=='1':
            a=topic.objects.get(pk=idd)
            a.islive=False
            a.save()
        else:
            a=topic.objects.get(pk=idd)
            a.islive=True
            a.save()
    return redirect('quesr',cid=cid)

def delquesr(request,pk1,cid):
    if not request.user.is_authenticated or not request.user.profile.ifTeacher:
        return redirect('Link2')
    a=questr.objects.get(pk=pk1)
    a.delete()
    return redirect('quesr',cid=cid)

'''
def searchques_stud(request,cid):
    if not request.user.is_authenticated:
        return redirect('Link2')
    if request.method=='POST':
        reg= studList.objects.filter(email=request.user.username,stat=True).exists()
        if(reg!=True):
            messages.warning(request,('You are not registered for this course!'))
            return redirect('quesRO',curr_c=cid)            
        stopic=request.POST['searchtopic']
        all_q=ques.objects.filter(topic=stopic,istest=0,courseid=cid).order_by('level')
        attempted=list(practqn_attempt.objects.filter(email=request.user.username).values_list('ques__id', flat=True))
        all_q1=all_q.exclude(pk__in=attempted)
        if(len(all_q1)==0):
            messages.warning(request,('You have attempted all questions in this topic!'))
            return redirect('quesRO',curr_c=cid)
        tid=topic.objects.get(name=stopic).id
        return render(request,'practQues.html',{'all_q':all_q1,'tid':tid,'cid':cid})
    return redirect('Link2')
'''
def getNextPQ(request,nextid):
	cq=ques.objects.get(pk=nextid)
	jdict={'qid':cq.id,'ques':cq.ques,'opt1':cq.opt1,'opt2':cq.opt2,'opt3':cq.opt3,'opt4':cq.opt4,'opt5':cq.opt5,'opt6':cq.opt6,'fb':cq.feedback,'isradio':cq.isradio}
	if(cq.img):
		jdict['imgurl']=cq.img.url
	else:
		jdict['imgurl']=''
	return JsonResponse(jdict,status=200)

def searchques_stud(request,cid):
    if not request.user.is_authenticated:
        return redirect('Link2')
    if request.method=='POST':
        reg= studList.objects.filter(email=request.user.username,stat=True).exists()
        if(reg!=True):
            messages.warning(request,('You are not registered for this course!'))
            return redirect('quesRO',curr_c=cid)            
        stopic=request.POST['searchtopic']
        all_q=ques.objects.filter(topic=stopic,istest=0,courseid=cid).order_by('level')
        attempted=list(practqn_attempt.objects.filter(email=request.user.username,stat=1).values_list('ques__id', flat=True))#CHANGE
        all_q1=list(all_q.exclude(pk__in=attempted).values_list('id',flat=True))
        print(stopic)
        print(all_q)
        print(attempted)
        print(all_q1)
        if(len(all_q1)==0):
            messages.warning(request,('You have attempted all questions in this topic!'))
            return redirect('quesRO',curr_c=cid)
        currques=ques.objects.get(pk=all_q1[0])
        t=topic.objects.get(name=stopic)
        return render(request,'practQues.html',{'all_q':all_q1[1:],'tid':t.id,'topic':t,'cid':cid,'currques':currques})
    return redirect('Link2')

def evaluatePQ(request,qid,cid):
    print("In evaluate PQ!!")
    question=ques.objects.get(pk=qid)
    course=List.objects.get(pk=cid)
    tt=request.POST['time']
    print(tt)
    if request.method == 'POST':
        result=-1     
        correct=-1
        fb=''
        if question.isradio:
            if question.correct == request.POST['options']:
                b=practqn_attempt(email=request.user.username,ques=question,stat=1,time_taken=tt)
                print("Correct Response Added !!")
                b.save()
                result=1
            else:
                b=practqn_attempt(email=request.user.username,ques=question,stat=2,time_taken=tt)
                print("Wrong Response Added !!")
                b.save()
                result=2
                correct=question.correct
                fb=question.feedback

        else:
            c=','.join(request.POST.getlist('options[]'))
            if question.correct == c:
                b=practqn_attempt(email=request.user.username,ques=question,stat=1,time_taken=tt)
                b.save()
                result=1
            else:
                b=practqn_attempt(email=request.user.username,ques=question,stat=2,time_taken=tt)
                b.save()
                result=2
                correct=question.correct
                fb=question.feedback
        return JsonResponse({'result':result,'correct':correct,'fb':fb},status=200)
    return redirect('Link2')

def evaluateQ(request,qnr_att_id,qid,nextid):
	qnr_att=qnr_attempt.objects.get(pk=qnr_att_id)
	cq=ques.objects.get(pk=qid)
	stat=0
	try:
		ans=request.POST['options']
		if ans==cq.correct:
			stat=1
			qnr_att.score+=cq.marks
		else:
			stat=2
			qnr_att.score-=cq.marks
	except:
		stat=3
	b=qn_attempt(qnr_attempt=qnr_att,ques=cq,stat=stat)
	b.save()
	print(stat)
	if nextid=='-1':
		#cq.tt
		messages.success(request,('Your answers have been successfully recorded!'))
		return JsonResponse({'finish':True},status=200)
	else:
		nq=ques.objects.get(pk=nextid)
		jdict={'qid':nq.id,'ques':nq.ques,'opt1':nq.opt1,'opt2':nq.opt2,'opt3':nq.opt3,'opt4':nq.opt4,'opt5':nq.opt5,'opt6':nq.opt6,'isradio':nq.isradio}
		print(jdict['ques'])
		print(jdict['opt1'])
		print(jdict['opt2'])
		if(nq.img):
			jdict['imgurl']=nq.img.url
		else:
			jdict['imgurl']=''
		return JsonResponse(jdict,status=200)

def reconnect(request):
	return JsonResponse({'result':'ok'},status=200)

def pretest(request,pk1,cid):
    if not request.user.is_authenticated:
        return redirect('Link2')
    thistest=questr.objects.get(pk=pk1)
    course=List.objects.get(pk=cid)
    if thistest.islive==False:
    	messages.warning(request,('This questionnaire is not live!'))
    	return redirect('quesRO',cid)
    #POST request for "start test" so that user cant access through link and thus a check if invalid user is not required again
    try:
        if studList.objects.filter(email=request.user.username,stat=True,course=course).exists():
            if qnr_attempt.objects.filter(qnr=thistest,email=request.user.username).exists():
                messages.warning(request,('You have already submitted this Test!'))
                return redirect('quesRO',cid)
            return render(request,'pretest.html',{'thistest':thistest,'pk1':pk1,'cid':cid})
        else:
            messages.warning(request,('Please register for the course to attempt this questionnaire!'))
            return redirect('quesRO',cid)
    #If test is live but there are no questions:
    except:
        if studList.objects.filter(email=request.user.username,stat=True,course=course).exists():
        	messages.warning(request,('This questionnaire is under construction!'))
        else:
            messages.warning(request,('Please register for the course to attempt this questionnaire!'))
        return redirect('quesRO',cid)

def test(request,pk1,cid):
	if not request.user.is_authenticated:
		return redirect('Link2')
	thistest=questr.objects.get(pk=pk1)
	course=List.objects.get(pk=cid)
	if request.method=='POST':
		all_q=ques.objects.filter(qnr=thistest)
		all_q1=list(all_q.values_list('id',flat=True))
		currques=ques.objects.get(pk=all_q1[0])
		#a=qnr_attempt(name=request.user.first_name,email=request.user.username,DT=datetime.datetime.now(),qnr=thistest,time_taken=-1)#CHANGE(time)
		#a.save()
		if len(all_q1)>1:
			return render(request, 'new_qnRO.html', {'pk1':pk1,'all_q':all_q1[1:],'curr_q':thistest,'cid':cid,'currques':currques,'qnr_att_id':0,'nqid':all_q1[1]})#CHANGE THIS
		else:
			return render(request, 'new_qnRO.html', {'pk1':pk1,'all_q':all_q1[1:],'curr_q':thistest,'cid':cid,'currques':currques,'qnr_att_id':0,'nqid':-1})#CHANGE THIS
	else:
		messages.warning(request,('Please access all questionnaires from this screen'))
		return redirect(quesRO,cid)

#evaluate test:(only POST)
def qnRO(request,pk1,cr_crseid):
    if not request.user.is_authenticated:
        return redirect('Link2')
    curr_q=questr.objects.get(pk=pk1)
    course=List.objects.get(pk=cr_crseid)
    if request.method == 'POST':
        #This part is for: if user goes back and tries to submit again
        if qnr_attempt.objects.filter(qnr=curr_q,email=request.user.username).exists():
            messages.warning(request,('You have already submitted this Test!'))
            return redirect('quesRO',cr_crseid)
        rt=int(request.POST['timeRemain'])
        temp=curr_q.time.split(':')
        testTimeSeconds=int(temp[0])*3600+int(temp[1])*60
        tt=testTimeSeconds-rt
        print(tt)
        #DELETE NEXT LINE(OUT IN PRETEST)
        a=qnr_attempt(name=request.user.first_name,email=request.user.username,DT=datetime.datetime.now(),qnr=curr_q,time_taken=tt)
        a.save()
        all_qns=ques.objects.filter(qnr=curr_q)
        n=all_qns.count()
        score=0
        lst=[]
        for i in range(0,n):
            if all_qns[i].isradio:
                try:
                    if all_qns[i].correct == request.POST[str(i)]:
                        b=qn_attempt(qnr_attempt=a,ques=all_qns[i],stat=1)
                        b.save()
                        score+=all_qns[i].marks
                    else:
                        b=qn_attempt(qnr_attempt=a,ques=all_qns[i],stat=2)
                        b.save()
                        score-=all_qns[i].neg
                except:
                    b=qn_attempt(qnr_attempt=a,ques=all_qns[i],stat=3)
                    b.save()
            else:
                c=','.join(request.POST.getlist(str(i)+'[]'))
                if c=='':
                    b=qn_attempt(qnr_attempt=a,ques=all_qns[i],stat=3)
                    b.save()
                elif all_qns[i].correct == c:
                    b=qn_attempt(qnr_attempt=a,ques=all_qns[i],stat=1)
                    b.save()
                    score+=all_qns[i].marks
                else:
                    b=qn_attempt(qnr_attempt=a,ques=all_qns[i],stat=2)
                    b.save()
                    score-=all_qns[i].neg

        a.score=score
        a.save()
        messages.success(request,('Your Answers have been recorded successfully!'))
        return redirect('quesRO',cr_crseid)

#---------------------------------------------------------------------------------------------------------------------If reques is not POST:
    return redirect('Link2')

def searchques(request,cid,tid):
    if not request.user.is_authenticated or not request.user.profile.ifTeacher:
        return redirect('Link2')
    stopic=topic.objects.get(pk=tid)
    all_q=ques.objects.filter(topic=stopic.name,istest=0,courseid=cid)
    return render(request, 'practQuesT.html', {'cid':cid,'all_q':all_q,'topic':stopic})

def updateqn(request,qid,pk1,cid):
    if not request.user.is_authenticated or not request.user.profile.ifTeacher:
        return redirect('Link2')
    if request.method=='POST':
        question=ques.objects.filter(pk=qid)#get doesnt work here
        quesn=request.POST['item']
        fb=request.POST['feedback']
        image=request.FILES.get('img',None)
        op1=request.POST['op1']
        op2=request.POST['op2']
        op3=request.POST['op3']
        op4=request.POST['op4']
        op5=request.POST['op5']
        op6=request.POST['op6']
        c1=request.POST.getlist('correct[]')
        marks1=request.POST['marks']
        neg1=request.POST['neg']
        topic1=request.POST['topic_']
        level=request.POST['level']
        sameimage=request.POST['sameimage']
        if question[0].istest==1:
            if len(c1)==1:
                if sameimage=='same':
                    question.update(ques=quesn,feedback=fb,opt1=op1,opt2=op2,opt3=op3,opt4=op4,opt5=op5,opt6=op6,correct=c1[0],isradio=True,topic=topic1,level=level,marks=marks1,neg=neg1)
                else:
                    question.update(ques=quesn,feedback=fb,opt1=op1,opt2=op2,opt3=op3,opt4=op4,opt5=op5,opt6=op6,correct=c1[0],isradio=True,topic=topic1,level=level,marks=marks1,neg=neg1)
                    a=question[0]
                    a.img.delete()
                    a.img=image
                    a.save()
            else:
                c=','.join(c1)
                if sameimage=='same':
                    question.update(ques=quesn,feedback=fb,opt1=op1,opt2=op2,opt3=op3,opt4=op4,opt5=op5,opt6=op6,correct=c,topic=topic1,level=level,isradio=False,marks=marks1,neg=neg1)
                else:
                    question.update(ques=quesn,feedback=fb,opt1=op1,opt2=op2,opt3=op3,opt4=op4,opt5=op5,opt6=op6,correct=c,topic=topic1,level=level,isradio=False,marks=marks1,neg=neg1)
                    a=question[0]
                    a.img=image
                    a.save()
        else:
            if len(c1)==1:
                if sameimage=='same':
                    question.update(ques=quesn,feedback=fb,opt1=op1,opt2=op2,opt3=op3,opt4=op4,opt5=op5,opt6=op6,correct=c1[0],isradio=True,topic=topic1,level=level,marks=marks1,neg=neg1)
                else:
                    print("here")
                    question.update(ques=quesn,feedback=fb,opt1=op1,opt2=op2,opt3=op3,opt4=op4,opt5=op5,opt6=op6,correct=c1[0],isradio=True,topic=topic1,level=level,marks=marks1,neg=neg1)
                    a=question[0]
                    a.img.delete()
                    a.img=image
                    a.save()
            else:
                c=','.join(c1)
                if sameimage=='same':
                    question.update(ques=quesn,feedback=fb,opt1=op1,opt2=op2,opt3=op3,opt4=op4,opt5=op5,opt6=op6,correct=c,level=level,isradio=False,marks=marks1,neg=neg1)
                else:
                    question.update(ques=quesn,feedback=fb,opt1=op1,opt2=op2,opt3=op3,opt4=op4,opt5=op5,opt6=op6,correct=c,level=level,isradio=False,marks=marks1,neg=neg1)
                    a=question[0]
                    a.img=image
                    a.save()

        if pk1=='-1':
            topicid=topic.objects.get(name=topic1).id
            return redirect(searchques,cid=cid,tid=topicid)
        return redirect(qn,pk1=pk1,cid=cid)
    else:
        return redirect('Link2')

def qn(request,pk1,cid):
    if not request.user.is_authenticated or not request.user.profile.ifTeacher:
        return redirect('Link2')
    curr_c=List.objects.get(pk=cid)
    topics=topic.objects.filter(course=curr_c)
    if request.method=='POST':
        quesn=request.POST['item']
        fb=request.POST['feedback']
        image=request.FILES.get('img',None)
        op1=request.POST['op1']
        op2=request.POST['op2']
        op3=request.POST['op3']
        op4=request.POST['op4']
        op5=request.POST['op5']
        op6=request.POST['op6']
        c1=request.POST.getlist('correct[]')
        marks1=request.POST['marks']
        neg1=request.POST['neg']
        topic1=request.POST['topic_']
        level=request.POST['level']
        #-1 for pract ques upload in addq.html
        if(pk1!='-1'):
            curr_q=questr.objects.get(pk=pk1)
            
            if len(c1)==1:
                a=ques(ques=quesn,feedback=fb,img=image,opt1=op1,opt2=op2,opt3=op3,opt4=op4,opt5=op5,opt6=op6,correct=c1[0],topic=topic1,level=level,marks=marks1,neg=neg1,istest=1,qnr=curr_q,courseid=cid)
                a.save()
            else:
                c=','.join(c1)
                a=ques(ques=quesn,feedback=fb,img=image,opt1=op1,opt2=op2,opt3=op3,opt4=op4,opt5=op5,opt6=op6,correct=c,topic=topic1,level=level,isradio=False,marks=marks1,neg=neg1,istest=1,qnr=curr_q,courseid=cid)
                a.save()                
            all_q=ques.objects.filter(qnr=curr_q)
            return render(request, 'qn.html', {'cid':cid,'pk1':pk1,'all_q':all_q,'curr_q':curr_q,'topics':topics})
        else:
            if len(c1)==1:
                a=ques(ques=quesn,feedback=fb,img=image,opt1=op1,opt2=op2,opt3=op3,opt4=op4,opt5=op5,opt6=op6,correct=c1[0],topic=topic1,level=level,marks=marks1,neg=neg1,istest=0,courseid=cid)
                a.save()
            else:
                c=','.join(c1)
                a=ques(ques=quesn,feedback=fb,img=image,opt1=op1,opt2=op2,opt3=op3,opt4=op4,opt5=op5,opt6=op6,correct=c,topic=topic1,level=level,isradio=False,marks=marks1,neg=neg1,istest=0,courseid=cid)
                a.save()
            tid=topic.objects.get(name=topic1,course=curr_c).id
            return redirect('searchques',cid=cid,tid=tid)

    else:
        if(pk1!='-1'):
            try:
                curr_q=questr.objects.get(pk=pk1)
                all_q=ques.objects.filter(qnr=curr_q)
                return render(request, 'qn.html', {'cid':cid,'pk1':pk1,'all_q':all_q,'curr_q':curr_q,'topics':topics})
            except:
                return render(request, 'qn.html', {'cid':cid,'pk1':pk1,'curr_q':curr_q,'topics':topics})
        else:
            return redirect('Link2')

def bulkqn(request,pk1,cid):
    if not request.user.is_authenticated or not request.user.profile.ifTeacher:
        return redirect('Link2')
    
    if request.method=='POST':
        #-1 when uploading prract questions
        if(pk1!="-1"):
            curr_q=questr.objects.get(pk=pk1)
            try:
                file = request.FILES['file']
                df=pd.read_csv(file,keep_default_na=False)
                r=df.shape[0]
                #checking if rows>300
                if (r>300):
                    messages.warning(request,('Error! Maximum 300 questions allowed per upload'))
                    try:
                        all_q=ques.objects.filter(qnr=curr_q)
                        return render(request, 'qn.html', {'pk1':pk1,'all_q':all_q,'curr_q':curr_q})
                    except:
                        return render(request, 'qn.html', {'pk1':pk1,'curr_q':curr_q})
                #if not:
                df=df.iloc[:,:].values
                for i in range(0,r):
                    if len(df[i][7])==1:
                        a=ques(ques=df[i][0],opt1=df[i][1],opt2=df[i][2],opt3=df[i][3],opt4=df[i][4],opt5=df[i][5],opt6=df[i][6],correct=df[i][7],marks=df[i][8],neg=df[i][9],level=int(df[i][10]),topic=df[i][11],feedback=df[i][12],istest=1,qnr=curr_q,courseid=cid)                
                        a.save()
                    else:
                        a=ques(ques=df[i][0],opt1=df[i][1],opt2=df[i][2],opt3=df[i][3],opt4=df[i][4],opt5=df[i][5],opt6=df[i][6],correct=df[i][7],marks=df[i][8],neg=df[i][9],level=int(df[i][10]),topic=df[i][11],feedback=df[i][12],istest=1,isradio=False,qnr=curr_q,courseid=cid)                
                        a.save()
                #all_q=ques.objects.filter(qnr=curr_q)
                return redirect('qn',pk1=pk1,cid=cid)
                #return render(request, 'qn.html', {'cid':cid,'pk1':pk1,'all_q':all_q,'curr_q':curr_q,'topics':topics})
            except:
                messages.warning(request,('Error! Please look at the sample file to make sure your file meets the requirements'))
                return redirect('qn',pk1=pk1,cid=cid)
        else:
            try:
                tp=request.POST['topicname']
                tid=topic.objects.get(name=tp).id
                file = request.FILES['file']
                df=pd.read_csv(file,keep_default_na=False)
                r=df.shape[0]
                #checking if rows>300
                if (r>300):
                    messages.warning(request,('Error! Maximum 300 questions allowed per upload'))
                    return redirect('quesr',cid=cid)
                #if not:
                df=df.iloc[:,:].values
                for i in range(0,r):
                    if len(df[i][7])==1:
                        a=ques(ques=df[i][0],opt1=df[i][1],opt2=df[i][2],opt3=df[i][3],opt4=df[i][4],opt5=df[i][5],opt6=df[i][6],correct=df[i][7],marks=df[i][8],neg=df[i][9],level=int(df[i][10]),feedback=df[i][11],topic=tp,istest=0,courseid=cid)                
                        a.save()
                    else:
                        a=ques(ques=df[i][0],opt1=df[i][1],opt2=df[i][2],opt3=df[i][3],opt4=df[i][4],opt5=df[i][5],opt6=df[i][6],correct=df[i][7],marks=df[i][8],neg=df[i][9],level=int(df[i][10]),feedback=df[i][11],topic=tp,istest=0,isradio=False,courseid=cid)                
                        a.save()
                messages.success(request,('Questions uploaded successfully!'))
                return redirect('searchques',cid=cid,tid=tid)
            except:
                messages.warning(request,('Error! Please look at the sample file to make sure your file meets the requirements'))
                return redirect('searchques',cid=cid,tid=tid)

    else:
        return redirect('Link2')


def delqn(request,pk1,qpk,cid):
    if not request.user.is_authenticated or not request.user.profile.ifTeacher:
        return redirect('Link2')
    #if request.method=='POST':
    a=ques.objects.get(pk=pk1)
    stopic=a.topic
    a.delete()
    if qpk=='-1':
        course=List.objects.get(pk=cid)
        tid=topic.objects.get(name=stopic,course=course).id
        all_q=ques.objects.filter(topic=stopic,istest=0,courseid=cid)
        return redirect('searchques',cid=cid,tid=tid)
    else:
        return redirect('qn',pk1=qpk,cid=cid)
    #return redirect('Link2')

def delpractqn(request,pk1,cid):
    if not request.user.is_authenticated or not request.user.profile.ifTeacher:
        return redirect('Link2')
    a=ques.objects.get(pk=pk1)
    a.delete()
    return redirect('quesr',cid=cid)

def email(request,pk1,cid):
    course=List.objects.get(pk=cid)
    quesr=questr.objects.get(pk=pk1)
    subject = 'Reminder for Questionnaire'
    message = 'This is to remind you that you have not yet attempted the quesstionnaire: '+quesr.name+', for the course: '+course.item
    email_from = settings.EMAIL_HOST_USER
    #for visualization:
    #recipient_list = ['sunvirsingh72@gmail.com',]
    #actual code:
    
    regstuds=studList.objects.filter(course=course,stat=True)
    uniqatt=qnr_attempt.objects.filter(qnr=quesr).values_list('email', flat=True).distinct()
    notyet=regstuds
    for i in range(0,len(uniqatt)):
        notyet=notyet.exclude(email=uniqatt[i])
    mailTo=list(notyet.values_list('email', flat=True))
    recipient_list = mailTo
    
    try:
        send_mail(subject,message,email_from,recipient_list,fail_silently=False)
        messages.success(request,('Email Reminder sent successfully!'))
    except:
        #send_mail(subject,message,email_from,recipient_list,fail_silently=False)
        messages.warning(request,('Error! Email Reminder was not sent'))
    
    return redirect('qnr_attempts',pk1=pk1,cid=cid)


def qnr_attempts(request,pk1,cid):
    if not request.user.is_authenticated or not request.user.profile.ifTeacher:
        return redirect('Link2')
    #PUT THIS IN TRY!!
    curr_q=questr.objects.get(pk=pk1)
    curr_crse=List.objects.get(pk=cid)
    try:
        attempts=qnr_attempt.objects.filter(qnr=curr_q)
        mean=attempts.aggregate(Avg('score'))
        scores=attempts.values_list('score', flat=True)
        names=attempts.values_list('email', flat=True)
        regstuds=studList.objects.filter(course=curr_crse,stat=True)
        uniqatt=attempts.values_list('email', flat=True).distinct()
        notyet=regstuds
        for i in range(0,len(uniqatt)):
            notyet=notyet.exclude(email=uniqatt[i])
        sendmail=",".join(list(notyet.values_list('email', flat=True)))
        return render(request, 'attempts_.html', {'pk1':pk1,'cid':cid,'curr_q':curr_q,'curr_crse':curr_crse,'attempts':attempts,'names':list(names),'scores':list(scores),'mean':mean['score__avg'],'regstuds':regstuds,'notyet':notyet,'sendmail':sendmail})
    except:
        return render(request, 'attempts_.html', {'pk1':pk1,'curr_q':curr_q})

def pq_attempts(request,tid,cid):
	if not request.user.is_authenticated or not request.user.profile.ifTeacher:
		return redirect('Link2')
	course=List.objects.get(pk=cid)
	t=topic.objects.get(pk=tid)
	students=studList.objects.filter(course=course)
	totalq=len(ques.objects.filter(courseid=cid,topic=t.name,istest=False))
	lst=[]
	for i in students:
		a=practqn_attempt.objects.filter(ques__courseid=cid,ques__topic=t.name,email=i.email)
		if(len(a)==totalq):
			corr=0
			for j in a:
				if(j.stat==1):
					corr+=1
			lst.append((i.email,round(corr/totalq*100,2)))

	return render(request, 'pqAttempts.html', {'tid':tid,'topic':t.name,'cid':cid,'students':lst,'solved':len(lst),'notsolved':len(students)-len(lst)})

def qn_attempts(request,pk1,tid,email):
    if not request.user.is_authenticated:
        return redirect('Link2')
    #email is not -1 when teaches accesses practice question sheet
    if email!='-1':
    	t=topic.objects.get(pk=tid)
    	atts=practqn_attempt.objects.filter(email=email,ques__topic=t.name,ques__istest=False)
    	jdict={'quesns':[],'ans':[],'negM':[],'posM':[],'imgurl':[]}
    	for i in atts:
	        jdict['quesns'].append(i.ques.ques)
	        jdict['ans'].append(i.stat)
	        jdict['posM'].append(i.ques.marks)
	        jdict['negM'].append(i.ques.neg)
	        if i.ques.img:
	        	jdict['imgurl'].append(i.ques.img.url)
	        else:
	        	jdict['imgurl'].append('')
    	return JsonResponse(jdict,status=200)
    #-1 when request coming from student dashboard. In this case qnr id is sent(tid), In other case qnr_attempt id is sent 
    if pk1=='-1':
        curr_att=qnr_attempt.objects.get(qnr__id=tid,email=request.user.username)
    else:
        curr_att=qnr_attempt.objects.get(pk=pk1)
    q_attempts=qn_attempt.objects.filter(qnr_attempt=curr_att)
    jdict={'quesns':[],'ans':[],'negM':[],'posM':[],'fb':[],'imgurl':[]}
    for i in q_attempts:
        jdict['quesns'].append(i.ques.ques)
        jdict['ans'].append(i.stat)
        jdict['posM'].append(i.ques.marks)
        jdict['negM'].append(i.ques.neg)
        #jdict['correct'].append(i.ques.correct)
        jdict['fb'].append(i.ques.feedback)
        if i.ques.img:
	        	jdict['imgurl'].append(i.ques.img.url)
        else:
        	jdict['imgurl'].append('')
    return JsonResponse(jdict,status=200)
    return render(request, 'attempts_q.html', {'q_attempts':q_attempts,'name':curr_att.name,'qnr':curr_att.qnr.name})


def attemptscsv(request,pk1):
    quesr=questr.objects.get(pk=pk1)
    #fname="attempts-"+quesr.name+".csv"
    allobj=qnr_attempt.objects.filter(qnr=quesr)
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="attempts.csv"'

    writer = csv.writer(response)
    writer.writerow(['Name','Email','Date','Time','Score'])

    for obj in allobj:
        writer.writerow([obj.name,obj.email,obj.DT.date(),str(obj.DT.time().hour)+':'+str(obj.DT.time().minute),obj.score])

    return response

def answersheet(request,pk1, *args, **kwargs):
    qnrattepmt=qnr_attempt.objects.get(pk=pk1)
    qattempts=qn_attempt.objects.filter(qnr_attempt=qnrattepmt)
    template = get_template('attempts_q.html')
    context = {
        "qnrattepmt": qnrattepmt,
        "q_attempts": qattempts,
    }
    html = template.render(context)
    pdf = render_to_pdf('attempts_q.html', context)
    if pdf:
        response = HttpResponse(pdf, content_type='application/pdf')
        filename = "AnswerSheet.pdf"
        content = "inline; filename=%s" %(filename)
        download = request.GET.get("download")
        if download:
            content = "attachment; filename='%s'" %(filename)
        response['Content-Disposition'] = content
        return response
    return HttpResponse("Not found")

def questionspdf(request,qnrid,tid, *args, **kwargs):
    if tid=='-1':
        questionnaire=questr.objects.get(pk=qnrid)
        questions=ques.objects.filter(qnr=questionnaire)
        context = {
        "questions": questions,
        "qnrname": questionnaire.name,
        "isqnr":True,
        }
    else:
        topic1=topic.objects.get(pk=tid)
        questions=ques.objects.filter(topic=topic1.name,istest=0)
        context = {
        "questions": questions,
        "topicname": topic1.name,
        "isqnr":False,
        }

    #qnrattepmt=qnr_attempt.objects.get(pk=pk1)
    #qattempts=qn_attempt.objects.filter(qnr_attempt=qnrattepmt)
    template = get_template('questionspdf.html')
    '''
    context = {
        "qnrattepmt": qnrattepmt,
        "q_attempts": qattempts,
    }
    '''
    html = template.render(context)
    pdf = render_to_pdf('questionspdf.html', context)
    if pdf:
        response = HttpResponse(pdf, content_type='application/pdf')
        filename = "questions.pdf"
        content = "inline; filename=%s" %(filename)
        download = request.GET.get("download")
        if download:
            content = "attachment; filename='%s'" %(filename)
        response['Content-Disposition'] = content
        return response
    return HttpResponse("Not found")

def logs(request):
    if request.method =='POST':
        start_date=request.POST['start']
        end_date=request.POST['end']

        logtype=request.POST['logtype']
        c_id=request.POST['course']
        course=List.objects.get(pk=int(c_id))

        stud_list=studList.objects.filter(course=course)
        students=list(stud_list.values_list('email', flat=True))
        flist=[]

        if(logtype=='p'):
            pract_qns=list(ques.objects.filter(istest=0,courseid=c_id).values_list('id',flat=True))
            b=practqn_attempt.objects.filter(email__in=students,ques__id__in=pract_qns,date__range=[start_date, end_date])
            for i in b:
                flist.append((i.ques.id,i.ques.topic,i.ques.level,i.email,i.stat,i.date))

            response = HttpResponse(content_type='text/csv')
            response['Content-Disposition'] = 'attachment; filename="practicelogs.csv"'
            csv_out=csv.writer(response)
            csv_out.writerow(['quesID','topic','level','student','result','date'])
            for row in flist:
                csv_out.writerow(row)
            return response

        elif(logtype=='r'):
            r=resAccess.objects.filter(course=course.item,email__in=students,date__range=[start_date, end_date])
            for i in r:
                flist.append((i.email,i.rType,i.topic,i.date,i.sum_click))

            response = HttpResponse(content_type='text/csv')
            response['Content-Disposition'] = 'attachment; filename="resourcelogs.csv"'
            csv_out=csv.writer(response)
            csv_out.writerow(['student','resource type','topic','date','sum_click'])
            for row in flist:
                csv_out.writerow(row)
            return response

        elif(logtype=='t'):
            t=qnr_attempt.objects.filter(qnr__course=course,email__in=students,DT__date__range=[start_date, end_date])
            for i in t:
                flist.append((i.qnr.id,i.email,i.score,i.DT.date()))

            response = HttpResponse(content_type='text/csv')
            response['Content-Disposition'] = 'attachment; filename="testlogs.csv"'
            csv_out=csv.writer(response)
            csv_out.writerow(['test_ID','student','score','date_submission'])
            for row in flist:
                csv_out.writerow(row)
            return response
        else:
            t=list(qnr_attempt.objects.filter(qnr__course=course,email__in=students,DT__date__range=[start_date, end_date]).values_list('id',flat=True))
            tq=qn_attempt.objects.filter(qnr_attempt__id__in=t)
            for i in tq:
                flist.append((i.qnr_attempt.qnr.id,i.ques.id,i.ques.topic,i.ques.level,i.qnr_attempt.email,i.stat,i.qnr_attempt.DT.date()))

            response = HttpResponse(content_type='text/csv')
            response['Content-Disposition'] = 'attachment; filename="testquestionslogs.csv"'
            csv_out=csv.writer(response)
            csv_out.writerow(['test_ID','ques_ID','topic','level','student','result','date'])
            for row in flist:
                csv_out.writerow(row)
            return response
    return redirect('Link2')


def courselogs(request):
    if request.method =='POST':
        start_date=request.POST['start']
        end_date=request.POST['end']
        #a=qnr_attempt.objects.filter(DT__date__range=["2011-01-01", "2020-05-31"])

        c_id=request.POST['course']
        print(start_date)
        print(end_date)

        final=pd.DataFrame()
        course=List.objects.get(pk=int(c_id))
        print(course.item)
        stud_list=studList.objects.filter(course=course)
        students=list(stud_list.values_list('email', flat=True))
        print(students)
        final["student"]=students
        studrecords=studRecords.objects.filter(course=course.item,date__range=[start_date, end_date])
        crse_clicks=[0]*len(students)
        last_crse_click=[0]*len(students)

        res_access=resAccess.objects.filter(course=course.item,date__range=[start_date, end_date])
        ques_clicks=[0]*len(students)
        assign_clicks=[0]*len(students)
        link_clicks=[0]*len(students)
        test_qnrs=questr.objects.filter(course=course)
        test_qnr_scores=[[0]*len(students) for i in range(len(test_qnrs))]

        pract_qnid=[]
        pq=ques.objects.filter(istest=0,courseid=c_id)
        for j in pq:
            pract_qnid.append(j.id)

        all_pract_qns=[[0]*len(students) for i in range(len(pract_qnid))]

        topics=topic.objects.filter(course=course)
        topic_clicks=[[0]*len(students) for i in range(len(topics))]
        topic_scores_test=[[0]*len(students) for i in range(len(topics))]
        for i in range(0,len(students)):
            s=studrecords.filter(email=students[i])
            last=0
            if len(s)!=0:
                last=s[0].date
            for j in s:
                crse_clicks[i]+=j.sum_click
                if(j.date>last):
                    last=j.date
            if(last!=0):
                last_crse_click[i]=(datetime.datetime.now().date()-last).days

            studq=res_access.filter(email=students[i])
            x=studq.filter(rType="questionnaire")
            if len(x)!=0:
                for j in x:
                    ques_clicks[i]+=j.sum_click

            y=studq.filter(rType="link")
            if len(y)!=0:
                for j in y:
                    link_clicks[i]+=j.sum_click

            z=studq.filter(rType="assignment")
            if len(z)!=0:
                for j in z:
                    assign_clicks[i]+=j.sum_click

            for j in range(0,len(topics)):
                c=studq.filter(topic=topics[j])
                if len(c)!=0:
                    for w in c:
                        topic_clicks[j][i]+=w.sum_click

            for j in range(0,len(test_qnrs)):
                if qnr_attempt.objects.filter(email=students[i],qnr=test_qnrs[j],DT__date__range=[start_date, end_date]).exists():
                    a=qnr_attempt.objects.get(email=students[i],qnr=test_qnrs[j],DT__date__range=[start_date, end_date])
                    test_qnr_scores[j][i]=a.score

                    qs=qn_attempt.objects.filter(qnr_attempt=a)
                    for m in range(0,len(topics)):
                        qq=qs.filter(ques__topic=topics[m])#to access fields of foreignkey, '.' is replaced by '__'
                        for h in qq:
                            if h.stat==1:
                                topic_scores_test[m][i]+=h.ques.marks
                            elif h.stat==2:
                                topic_scores_test[m][i]-=h.ques.neg

            for j in range(0,len(pract_qnid)):
                try:
                    #change here
                    pqa=practqn_attempt.objects.get(ques__id=pract_qnid[j],email=students[i],date__range=[start_date, end_date])
                    all_pract_qns[j][i]=pqa.stat
                except:
                    continue


        final["course_clicks"]=crse_clicks
        final["last_course_access(days)"]=last_crse_click
        final["questionnaire_clicks"]=ques_clicks
        final["link_clicks"]=link_clicks
        final["assignment_clicks"]=assign_clicks
        for i in range(0,len(topic_clicks)):
            final["topic("+topics[i].name + ")_sum_click"]=topic_clicks[i]
        for i in range(0,len(topic_scores_test)):
            final["topic("+topics[i].name + ")test_score_sum"]=topic_scores_test[i]
        for i in range(0,len(test_qnrs)):
            final["test_questionnaire("+test_qnrs[i].name + ")_score"]=test_qnr_scores[i]
        for i in range(0,len(pract_qnid)):
            final["Pract_Qid("+str(pract_qnid[i])+")"]=all_pract_qns[i]
        
        print(final)
        
        response = HttpResponse(content_type='text/csv')
        fname=course.item
        response['Content-Disposition'] = 'attachment; filename='+fname+' logs.csv'

        final.transpose().to_csv(path_or_buf=response)
        return response
        
        return HttpResponse('Done')
        return redirect(Link2)

def dashboard(request):
    if request.user.is_authenticated:
        u=request.user
        enrolled=list(studList.objects.filter(email=u.username,stat=True).values_list('course__id', flat=True))

        mycourses=list(List.objects.filter(pk__in=enrolled))
        for i in range(0,len(mycourses)):
            print("Considered Course is: ",i)
            #totalpq.append(ques.objects.filter(istest=0))
            topics1=list(topic.objects.filter(course=mycourses[i]).values_list('name',flat=True))
            topicIds=list(topic.objects.filter(course=mycourses[i]).values_list('pk',flat=True))
            print(topicIds)
            att=practqn_attempt.objects.filter(email=u.username,ques__courseid=mycourses[i].id)
            #topicscores=[0]*len(topics1)
            topicscores=[]
            ts_ov=0
            tqa_ov=0
            for tp in range(0,len(topics1)):
                tqa=att.filter(ques__topic=topics1[tp])
                #ts=tqa.filter(stat=1).count()#change this
                easy_count=len(set((list(tqa.filter(ques__level=1).values_list('ques__id',flat=True)))))
                medium_count=len(set((list(tqa.filter(ques__level=2).values_list('ques__id',flat=True)))))
                hard_count=len(set((list(tqa.filter(ques__level=3).values_list('ques__id',flat=True)))))
                print("Easy Count:",easy_count)
                print("Medium Count:",medium_count)
                print("Hard Count:",hard_count)

                easy=0
                medium=0
                hard=0

                if(easy_count!=0):
                    easy=round(0.3/easy_count,2)
                if(medium_count!=0):
                    medium=round(0.3/medium_count,2)
                if(hard_count!=0):
                    hard=round(0.4/hard_count,2)

                if(easy_count!=0 or medium_count!=0 or hard_count!=0):
                    if(easy_count==0 and medium_count==0):
                        hard=round(1/hard_count,2)
                    elif(easy_count==0 and hard_count==0):
                        medium=round(1/medium_count,2)
                    elif(medium_count==0 and hard_count==0):
                        easy=round(1/easy_count,2)
                    elif(easy_count!=0 and medium_count!=0 and hard_count==0):
                        easy=round(0.4/easy_count,2)
                        medium=round(0.6/medium_count,2)
                    elif(easy_count!=0 and medium_count==0 and hard_count!=0):
                        easy=round(0.6/easy_count,2)
                        hard=round(0.4/hard_count,2)
                    elif(easy_count==0 and medium_count!=0 and hard_count!=0):
                        hard=round(0.4/hard_count,2)
                        medium=round(0.6/medium_count,2)


                ts=0
                tq=0
                qids=list(tqa.values_list('ques__id',flat=True))
                qids=set(qids)
                print("qids: ",qids)
                tq=len(set(qids))
                # tq=len(tqa.filter(stat=1))
                for qid in qids:
                    tmp=tqa.filter(ques__id=qid)
                    #print(len(tmp))

                    #l=ques.objects.filter(id=qid)
                    #print(l)
                    l=tmp.values('ques__level')
                    #print(l)
                    lev=l[0]['ques__level']
                    print("Question Level is:")
                    print(lev)
                    val=1
                    if(lev==1):
                        val=easy
                    elif(lev==2):
                        val=medium
                    elif(lev==3):
                        val=hard
                    print("Value is:")
                    print(val)
                    #print("Length of attempts:")
                    #print(len(tmp))
                    if(len(tmp)==1 and tmp[0].stat==1):
                    	ts=ts+(val*1)
                    elif(len(tmp)==1 and tmp[0].stat==2):
                    	print("wrong!")
                    elif(len(tmp)==2):
                    	if(tmp[0].stat==1 or tmp[1].stat==1):
                    		ts=ts+(val*0.67)#red 33%
                    	else:
                    		print("wrong!")
                    elif(len(tmp)==3):
                    	if(tmp[0].stat==1 or tmp[1].stat==1 or tmp[2].stat==1):
                    		ts=ts+(val*0.34)#reduce 66%
                    	else:
                    		print("wrong!")
                    else:
                    	print("wrong!")
                    print("TS is:")
                    print(ts)

                tqa=tq
                #tqa=tqa.count()#till this
                tqa_ov+=tqa
                ts_ov+=ts
                totq=ques.objects.filter(courseid=mycourses[i].id,topic=topics1[tp],istest=0).count()
                try:
                    print("Overall Success Rate of Student: ",ts_ov,tqa_ov,round(ts*100,2))
                    topicscores.append((topics1[tp],tqa,totq,round((ts*100),2),topicIds[tp]))
                    try:
                        obj=studentPractScore.objects.get(email=u.username,course=mycourses[i],topic=topics1[tp])
                        obj.score=round(ts*100,2)
                        obj.save()
                    except:
                        obj=studentPractScore(email=u.username,course=mycourses[i],topic=topics1[tp],score=round(ts*100,2))
                        obj.save()
                    #topicscores.append((topics1[tp],tqa,totq,round(ts*100/tqa,2),topicIds[tp]))
                    #TODO: TRY CATCH WAS NEEDED FOR ABOVE FORMULA. IF IT'S NOT BEING USED, REMOVE TRY CATCH 
                except:
                    topicscores.append((topics1[tp],tqa,totq,0,topicIds[tp]))
                    try:
                        obj=studentPractScore.objects.get(email=u.username,course=mycourses[i],topic=topics1[tp])
                        obj.score=round(ts*100,2)
                        obj.save()
                    except:
                        obj=studentPractScore(email=u.username,course=mycourses[i],topic=topics1[tp],score=0)
                        obj.save()

            mycourses[i].pqa=tqa_ov
            mycourses[i].topics=topicscores
            if(tqa_ov>0):
                mycourses[i].sr=round((ts_ov/tqa_ov), 3)*100
            else:
                mycourses[i].sr=0

            tests=questr.objects.filter(course=mycourses[i],islive=True)#check this. agar test khatam krne ke bad teacher ne islive false kr diya to student ko show to hona chahiye
            studs=studList.objects.filter(course=mycourses[i])
            mypos=list(studs.values_list('email',flat=True)).index(u.username)
            
            myScoreTestWise=[]
            studscores=[]
            studscores_ov=[0]*len(studs)

            iDidntAttempt=False
            #id i didn't attempt, then browser mei 0 ki jagah NA show krna. But starting mei 0 hi rakhna hoga
            for j in tests:
                a=qnr_attempt.objects.filter(qnr=j)
                iDidntAttempt=False
                scoreListTestWise=[]

                for k in range(0,len(studscores_ov)):
                    try:
                        b=a.get(email=studs[k].email)
                        studscores_ov[k]+=b.score
                        scoreListTestWise.append(b.score)
                    except:
                        scoreListTestWise.append(0)
                        if(studs[k].email==request.user.username):
                            iDidntAttempt=True
                if(iDidntAttempt):
                    myScoreTestWise.append((j.id,j.name,'NA',np.quantile(scoreListTestWise, .25),np.quantile(scoreListTestWise, .50),np.quantile(scoreListTestWise, .75)))
                else:
                    myScoreTestWise.append((j.id,j.name,scoreListTestWise[mypos],np.quantile(scoreListTestWise, .25),np.quantile(scoreListTestWise, .50),np.quantile(scoreListTestWise, .75)))

            mycourses[i].myScoreTestWise=myScoreTestWise
            print("____________________________________")
            print(myScoreTestWise)
            print(iDidntAttempt)
            '''
            myatt=qnr_attempt.objects.filter(qnr__course=mycourses[i],email=u.username)
            myatts=[]
            for j in myatt:
                myatts.append((j.qnr.name,j.score,np.quantile(studscores, .25),np.quantile(studscores, .50),np.quantile(studscores, .75)))
            mycourses[i].myatts=myatts
            '''

            #mycourses[i].mytotatt=myatt.count()
            mycourses[i].testcount=tests.count()
            
            if(studscores_ov[mypos]<np.quantile(studscores_ov, .25)):
                mycourses[i].myrange_ov=12.5
            elif (studscores_ov[mypos]>=np.quantile(studscores_ov, .75)):
                mycourses[i].myrange_ov=87.5
            elif (studscores_ov[mypos]>=np.quantile(studscores_ov, .50)):
                mycourses[i].myrange_ov=62.5
            else:
                mycourses[i].myrange_ov=37.5

           
        return render(request,'dashboard.html',{'mycourses':mycourses})
    return redirect('Link2')


def RaTdowntype(request):
    if not request.user.is_authenticated or not request.user.profile.ifTeacher:
        return redirect('Link5')

    response = HttpResponse(content_type='text/csv')
    
    if request.method == 'POST':
        data_ = request.POST['data_']

        if data_=='rtype':
            df = pd.DataFrame(list(resAccess.objects.all().values('email', 'course', 'rType', 'sum_click')))
            course=df.course.unique()

            fname='ResourceWise_Course_logs.csv'
            response['Content-Disposition'] = 'attachment; filename='+fname
            
            for i in course:
                #access course id
                cor = List.objects.get(item=i)
                #access students registered for i course through cor.id
                students = pd.DataFrame(list(studList.objects.filter(course=cor.id).values('email')))
                row_ind=students.email.unique()

                mod_df= df.loc[df['course'] == i]
                col_ind=mod_df.rType.unique()

                course_df = pd.DataFrame(0,columns=col_ind, index=row_ind)
                ind=mod_df.index.to_list()
                for j in ind:
                    row=mod_df['email'][j]
                    col=mod_df['rType'][j]
                    val=course_df.at[row,col]
                    course_df.at[row,col]=val+mod_df['sum_click'][j]

                #create course column for final dataframe
                clist=[i for j in range(len(course_df))]
        
                #insert email and course as columns
                course_df.insert(loc=0, column='course', value=clist)
                course_df.insert(loc=1, column='email', value=course_df.index)
                course_df.to_csv(path_or_buf=response,float_format='%.2f',index=False)

        elif data_=='date':
            df = pd.DataFrame(list(resAccess.objects.all().values('email', 'course', 'date', 'sum_click')))
            course=df.course.unique()

            fname='DayWise_Course_logs.csv'
            response['Content-Disposition'] = 'attachment; filename='+fname

            for i in course:
                #access course id
                cor = List.objects.get(item=i)
                #access students registered for i course through cor.id
                students = pd.DataFrame(list(studList.objects.filter(course=cor.id).values('email')))
                row_ind=students.email.unique()
                
                mod_df= df.loc[df['course'] == i]
                col_ind=mod_df.date.unique()

                course_df = pd.DataFrame(0,columns=col_ind, index=row_ind)
                ind=mod_df.index.to_list()
                for j in ind:
                    row=mod_df['email'][j]
                    col=mod_df['date'][j]
                    val=course_df.at[row,col]
                    course_df.at[row,col]=val+mod_df['sum_click'][j]

                #replace dates by Day1, Day2 etc. in column names
                ls_len=len(course_df.columns)
                new_names=[]
                for j in range(1,ls_len+1):
                    name='Day_'+str(j)
                    new_names.append(name)

                course_df.columns=new_names

                #create course column for final dataframe
                clist=[i for j in range(len(course_df))]
        
                #insert email and course as columns
                course_df.insert(loc=0, column='course', value=clist)
                course_df.insert(loc=1, column='email', value=course_df.index)
                course_df.to_csv(path_or_buf=response,float_format='%.2f',index=False)

    return response

def assessmenTdown(request):
    if not request.user.is_authenticated or not request.user.profile.ifTeacher:
        return redirect('Link5')

    response = HttpResponse(content_type='text/csv')
    fname='All_Course_Assessment_logs.csv'
    response['Content-Disposition'] = 'attachment; filename='+fname

    df = pd.DataFrame(list(List.objects.all().values('id','item')))
    #print(df)
    course = df['id'].to_list()
    #print(course)
    c_ind=0
    for i in course:
        #get course name
        c_name=df['item'][c_ind]
        c_ind=c_ind+1

        #print("Considering Course: ",i)

        #extract all students enrolled in the course
        students = pd.DataFrame(list(studList.objects.filter(course=i).values('email')))
        row_ind=students['email'].to_list()

        #print("Course ",i," has students: ",len(row_ind))

        #get all external tests for respective course
        df1 = pd.DataFrame(list(extqnr.objects.filter(course=i).values('id','name','DT','mm','course')))
        #print(df1)

        if not df1.empty:
            #for each test get id and names
            test=df1['id'].to_list()
            test_name_list=df1['name'].to_list()

            #create new df for coursewise marks
            new_df=pd.DataFrame(columns=test_name_list,index=row_ind)
            #print(test)
            #print(test_name_list)
            ind=0
            for j in test:
                #get test name
                test_name=df1['name'][ind]
                ind=ind+1
                #print("Considering Test: ",test_name)

                #get attempted data for test
                df2 = pd.DataFrame(list(ext_attempt.objects.filter(extqnr=j).values('email','marks')))
                #print(df2)
                #print("Number of Attempts for ", test_name," are: ",len(df2))
                #get index of df2
                ind1=df2.index.to_list()
                #print(ind1)
                for k in ind1:
                    row=df2['email'][k]
                    col=test_name
                    #print("row ",row," col ",col)
                    val=new_df.at[row,col]
                    new_df.at[row,col]=df2['marks'][k]
                    #print("old: ",val," new val:",new_df.at[row,col])
                    
            new_df.columns=test_name_list
            clist=[c_name for k in range(len(new_df))]
            new_df.insert(loc=0, column='course', value=clist)
            new_df.insert(loc=1, column='email', value=row_ind)
            #print(new_df)

            new_df.to_csv(path_or_buf=response,float_format='%.2f',index=False)

    return response


def CaTdown_(request):
    if not request.user.is_authenticated or not request.user.profile.ifTeacher:
        return redirect('Link5')
    
    response = HttpResponse(content_type='text/csv')
    fname='All_DayWise_Course_Interaction_logs.csv'
    response['Content-Disposition'] = 'attachment; filename='+fname

    df = pd.DataFrame(list(studRecords.objects.all().values('email', 'course', 'date', 'sum_click')))
    course=df.course.unique()

    for i in course:
        #print("Considering Course: ",i)
              
        mod_df= df.loc[df['course'] == i]
        col_ind=mod_df.date.unique()
        row_ind=mod_df.email.unique()

        course_df = pd.DataFrame(0,columns=col_ind, index=row_ind)
        #print(course_df)
        ind=mod_df.index.to_list()
        for j in ind:
            row=mod_df['email'][j]
            col=mod_df['date'][j]
            val=course_df.at[row,col]
            course_df.at[row,col]=val+mod_df['sum_click'][j]

        #replace dates by Day1, Day2 etc. in column names
        ls_len=len(course_df.columns)
        new_names=[]
        for j in range(1,ls_len+1):
            name='Day_'+str(j)
            new_names.append(name)
        course_df.columns=new_names
        
        #create course column for final dataframe
        clist=[i for j in range(len(course_df))]
        
        #insert email and course as columns
        course_df.insert(loc=0, column='course', value=clist)
        course_df.insert(loc=1, column='email', value=course_df.index)
        course_df.to_csv(path_or_buf=response,float_format='%.2f',index=False)

    return response

def courseAssessmentLogs(request):
    if request.method =='POST':
        c_id=request.POST['course']
        course=List.objects.get(pk=int(c_id))

        stud_list=studList.objects.filter(course=course)
        students=list(stud_list.values_list('email', flat=True))
        flist=[]
        df = pd.DataFrame()
        df["Student"] = students
        # print(df)
        allTests = questr.objects.filter(course=course)
        
        for test in allTests:
            scoreList=[]
            for stud in students:
                try:
                    studAttempt = qnr_attempt.objects.get(qnr=test,email=stud)
                    scoreList.append(studAttempt.score)
                except:
                    scoreList.append(0)
            df[test.name] = scoreList
        allTopics = topic.objects.filter(course=course)
        topicNames=list(allTopics.values_list('name', flat=True))
        # p = practqn_attempt.objects.filter(ques__topic__in=topicNames)
        p_attempts=practqn_attempt.objects.filter(ques__courseid=course.id)

        for topicName in topicNames:
            topicWiseScoreList=[]
            tqa1=p_attempts.filter(ques__topic=topicName)
            # qids=list(tqa.values_list('ques__id',flat=True))
            for stud in students:
                tqa=tqa1.filter(email = stud)
                qids=list(tqa.values_list('ques__id',flat=True))
                ts=0
                for qid in qids:
                    tmp=tqa.filter(ques__id=qid)
                    print(len(tmp))
                    if(len(tmp)==1 and tmp[0].stat==1):
                        ts+=1
                    elif(len(tmp)==1 and tmp[0].stat==2):
                        print("wrong!")
                    elif(len(tmp)==2):
                        if(tmp[0].stat==1 or tmp[1].stat==1):
                            ts+=0.67#red 33%
                        else:
                            print("wrong!")
                    elif(len(tmp)==3):
                        if(tmp[0].stat==1 or tmp[1].stat==1 or tmp[2]==1):
                            ts+=0.34#reduce 66%
                        else:
                            print("wrong!")
                    else:
                        print("wrong!")
                tqa=tqa.count()#till this
                try:
                    topicWiseScoreList.append(round(ts*100/tqa,2))
                except:
                    topicWiseScoreList.append(0)
            df[topicName] = topicWiseScoreList
        ext_qnrs=extqnr.objects.filter(course=course)
        for ext_qnr in ext_qnrs:
            extQnrScoreList=[]
            studAttempts = ext_attempt.objects.filter(extqnr = ext_qnr)
            for stud in students:
                try:
                    studAttempt = studAttempts.get(email = stud)
                    extQnrScoreList.append(studAttempt.marks)
                except:
                    extQnrScoreList.append(0)
            df[ext_qnr.name] = extQnrScoreList


        print(df)
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="courseAssessmentLogs.csv"'
        df.to_csv(path_or_buf=response,index=False)
        return response
        # return HttpResponse('Done')
        
def changeLiveLink(request,lid):
    if not request.user.is_authenticated or not request.user.profile.ifTeacher:
        return redirect('Link2')
    a=links.objects.get(pk=lid)
    if a.islive:
        a.islive=False
    else:
        a.islive=True
    a.save()
    return JsonResponse({'result':'ok'},status=200)

def changeLiveAssignLink(request,lid):
    if not request.user.is_authenticated or not request.user.profile.ifTeacher:
        return redirect('Link2')
    a=assignments.objects.get(pk=lid)
    if a.islive:
        a.islive=False
    else:
        a.islive=True
    a.save()
    return JsonResponse({'result':'ok'},status=200)

def changeLevelLink(request,lid):
    if not request.user.is_authenticated or not request.user.profile.ifTeacher:
        return redirect('Link2')
    a=links.objects.get(pk=lid)
    level=request.POST['level']
    a.level=level
    a.save()
    return HttpResponse('Level changed. This functionality is yet to be improved using Ajax')

def studentResources(request,cid,tid):
    if not request.user.is_authenticated:
        return redirect('Link2')
    course=List.objects.get(pk=cid)
    t=topic.objects.get(pk=tid)
    sps=studentPractScore.objects.get(course=course,topic=t.name,email=request.user.username)
    r=links.objects.filter(course=course)
    if sps.score<40:
        r=r.filter(level=1)
    elif sps.score>80:
        r=r.filter(level=3)
    else:
        r=r.filter(level=2)
    return render(request,'studentResources.html',{'resources':r})


def studentAssignments(request,cid,tid):
    if not request.user.is_authenticated:
        return redirect('Link2')
    course=List.objects.get(pk=cid)
    t=topic.objects.get(pk=tid)
    sps=studentPractScore.objects.get(course=course,topic=t.name,email=request.user.username)
    r=assignments.objects.filter(course=course)
    if sps.score<40:
        r=r.filter(level=1)
    elif sps.score>80:
        r=r.filter(level=3)
    else:
        r=r.filter(level=2)
    return render(request,'studentAssignments.html',{'assignments':r})

def resetPractQues(request,cid,tid):
    if not request.user.is_authenticated:
        return redirect('Link2')
    course=List.objects.get(pk=cid)
    t=topic.objects.get(pk=tid)
    sps=studentPractScore.objects.get(course=course,topic=t.name,email=request.user.username)
    allPractQuesAttempts = practqn_attempt.objects.filter(email=request.user.username,ques__topic=t.name,ques__courseid=course.id)
    #---TODO: Move this logic to where studentPractScore objects are created(add new cols in the table)
    #---Make logic consistent with dashboard
    tqa=allPractQuesAttempts
    qids=list(allPractQuesAttempts.values_list('ques__id',flat=True))
    ts=0
    ts_easy=0
    ts_med=0
    ts_hard=0
    q_easy=0
    q_med=0
    q_hard=0
    for qid in qids:
        tmp=allPractQuesAttempts.filter(ques__id=qid)
        print(len(tmp))
        if(len(tmp)==1 and tmp[0].stat==1):
            ts+=1
        elif(len(tmp)==1 and tmp[0].stat==2):
            print("wrong!")
        elif(len(tmp)==2):
            if(tmp[0].stat==1 or tmp[1].stat==1):
                ts+=0.67#red 33%
            else:
                print("wrong!")
        elif(len(tmp)==3):
            if(tmp[0].stat==1 or tmp[1].stat==1 or tmp[2]==1):
                ts+=0.34#reduce 66%
            else:
                print("wrong!")
        else:
            print("wrong!")
        currQues=ques.objects.get(pk=qid)
        if(currQues.level==1):
            ts_easy+=ts
            q_easy+=1
        elif(currQues.level==2):
            ts_med+=ts
            q_med+=1
        else:
            ts_hard+=ts
            q_hard+=1
        ts=0
    allPractQuesAttemptsCount=allPractQuesAttempts.count()
    percentageScore_easy=0
    percentageScore_med =0
    percentageScore_hard=0
    try:
        percentageScore_easy=round(ts_easy*100/allPractQuesAttemptsCount,2)
    except:
        percentageScore_easy=0
    try:
        percentageScore_med =round(ts_med*100/allPractQuesAttemptsCount,2)
    except:
        percentageScore_med=0
    try:
        percentageScore_hard=round(ts_hard*100/allPractQuesAttemptsCount,2)
    except:
        percentageScore_hard=0
    #---
    obj=practSummary(score_easy=percentageScore_easy,score_med=percentageScore_med,score_hard=percentageScore_hard,quesCount_easy=q_easy,quesCount_med=q_med,quesCount_hard=q_hard,email=request.user.username,topic=t.name,course=course)
    obj.save()
    for i in allPractQuesAttempts:
        a=practqn_attempt_resetted(email=i.email,ques=i.ques,stat=i.stat,date=i.date,time=i.time,time_taken=i.time_taken)
        a.save()
        i.delete()
    return redirect('dashboard')