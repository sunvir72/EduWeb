from django.db import models

class List(models.Model):
    item=models.CharField(max_length=200)
    desc=models.TextField(default='Edit description here')
    cred=models.FloatField(default=float(0.0))
    syllabus=models.TextField(default='Edit syllabus here')
    def __str__(self):
        return self.item + ' | ' + ' | ' +self.desc + ' | ' +self.syllabus


class saved_dataset(models.Model):
    name=models.CharField(max_length=300)
    DT=models.DateTimeField(auto_now=True)
    dataset=models.FileField(upload_to='dataset/')
    course=models.ForeignKey(List,on_delete=models.CASCADE)
    def __str__(self):
        return self.name
    
    def delete(self, *args, **kwargs):
        self.dataset.delete()
        super().delete(*args, **kwargs)

class topic(models.Model):
    name=models.CharField(max_length=200)
    islive=models.BooleanField(default=True)
    course=models.ForeignKey(List,on_delete=models.CASCADE)
    def __str__(self):
        return self.name

class links(models.Model):
    link=models.CharField(max_length=400)
    topic=models.CharField(max_length=200,default="None")
    course=models.ForeignKey(List,on_delete=models.CASCADE)
    level=models.IntegerField(default=1)
    islive=models.BooleanField(default=True)
    def __str__(self):
        return self.link

class instructors(models.Model):
    inst=models.CharField(max_length=200)
    course=models.ForeignKey(List,on_delete=models.CASCADE)
    def __str__(self):
        return self.inst

class assignments(models.Model):
    name=models.CharField(max_length=200,default='test')
    assign=models.FileField(upload_to='assign/')
    topic=models.CharField(max_length=200,default="None")
    level=models.IntegerField(default=1)
    course=models.ForeignKey(List,on_delete=models.CASCADE)
    islive=models.BooleanField(default=True)
    def __str__(self):
        return self.name
    
    def delete(self, *args, **kwargs):
        self.assign.delete()
        super().delete(*args, **kwargs)

class announcements(models.Model):
    annc=models.TextField()
    course=models.ForeignKey(List,on_delete=models.CASCADE)
    def __str__(self):
        return self.annc

class studList(models.Model):
    name=models.CharField(max_length=200,default='NA')
    email=models.CharField(max_length=200)
    stat=models.BooleanField(default=False)
    course=models.ForeignKey(List,on_delete=models.CASCADE)
    def __str__(self):
        return self.email

class studDetails(models.Model):
    name=models.CharField(max_length=200)
    email=models.CharField(max_length=200)
    gender=models.CharField(max_length=10)
    regDate=models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name+' | '+self.email
    
class resAccess(models.Model):
    name=models.CharField(max_length=200)
    email=models.CharField(max_length=200)
    rType=models.CharField(max_length=50)
    course=models.CharField(max_length=200)
    topic=models.CharField(max_length=200,default="none")
    date=models.DateField(auto_now=True)
    time=models.TimeField(auto_now=True)
    sum_click=models.IntegerField(default=1)
 
    def __str__(self):
        return self.name+' | '+self.rType+' | '+str(self.sum_click)


class studRecords(models.Model):
    name=models.CharField(max_length=200)
    email=models.CharField(max_length=200)
    course=models.CharField(max_length=200)
    sum_click=models.IntegerField(default=0)
    date=models.DateField(auto_now=True)

    def __str__(self):
        return self.email+' | '+self.course
  
class extqnr(models.Model):
    name=models.CharField(max_length=200)
    DT=models.DateTimeField(auto_now=True)
    mm=models.IntegerField(default=10)
    #islive=models.BooleanField(default=True)
    course=models.ForeignKey(List,on_delete=models.CASCADE)

    def __str__(self):
        return str(self.id)

class ext_attempt(models.Model):
    extqnr=models.ForeignKey(extqnr,on_delete=models.CASCADE)
    email=models.CharField(max_length=200,default='')
    marks=models.IntegerField()    

class questr(models.Model):
    name=models.CharField(max_length=200)
    DT=models.DateTimeField()
    time=models.CharField(max_length=10,default='NA')
    islive=models.BooleanField(default=True)
    course=models.ForeignKey(List,on_delete=models.CASCADE)

    def __str__(self):
        return str(self.id)

class ques(models.Model):
    ques=models.TextField()
    img=models.ImageField(upload_to='quesimage/',null=True,blank=True)
    feedback=models.TextField(null=True,blank=True)
    opt1=models.CharField(max_length=150)
    opt2=models.CharField(max_length=150)
    opt3=models.CharField(max_length=150)
    opt4=models.CharField(max_length=150)
    opt5=models.CharField(max_length=150)
    opt6=models.CharField(max_length=150)
    correct=models.CharField(max_length=12)
    marks=models.FloatField(default=float(1.0))
    neg=models.FloatField(default=float(0.0))
    isradio=models.BooleanField(default=True)
    topic=models.CharField(max_length=200,default="None")
    level=models.IntegerField(default=1)
    istest=models.IntegerField(default=0)
    qnr=models.ForeignKey(questr,on_delete=models.CASCADE,blank=True,null=True)
    courseid=models.IntegerField(default=-1)

    def delete(self, *args, **kwargs):
        self.img.delete()
        super().delete(*args, **kwargs) 

    def __str__(self):
        return self.ques

class qnr_attempt(models.Model):
    name=models.CharField(max_length=200)
    email=models.CharField(max_length=200)
    DT=models.DateTimeField()
    score=models.FloatField(default=float(0.0))
    qnr=models.ForeignKey(questr,on_delete=models.CASCADE)
    time_taken=models.IntegerField()

    def __str__(self):
        return self.email+' | '+self.qnr.name

class qn_attempt(models.Model):
    #email=models.CharField(max_length=200)
    #quesnr=models.ForeignKey(questr,on_delete=models.CASCADE)
    qnr_attempt=models.ForeignKey(qnr_attempt,on_delete=models.CASCADE)
    ques=models.ForeignKey(ques,on_delete=models.CASCADE)
    #something.ques.ques
    stat=models.IntegerField()

class practqn_attempt(models.Model):
    ques=models.ForeignKey(ques,on_delete=models.CASCADE)
    #integer field doesnt have max_length, so change this and above one to CharField in future
    stat=models.IntegerField()
    email=models.CharField(max_length=200)
    date=models.DateField(auto_now=True)
    time=models.TimeField(auto_now=True)
    time_taken=models.IntegerField()

class saved_models(models.Model):
    name=models.CharField(max_length=300)
    model=models.FileField(upload_to='saved_models/')
    def __str__(self):
        return self.name
    
    def delete(self, *args, **kwargs):
        self.model.delete()
        super().delete(*args, **kwargs)    

class studentPractScore(models.Model):
    email=models.CharField(max_length=200)
    course=models.ForeignKey(List,on_delete=models.CASCADE)
    topic=models.CharField(max_length=200)
    score=models.FloatField()

class practqn_attempt_resetted(models.Model):
    ques=models.ForeignKey(ques,on_delete=models.CASCADE)
    stat=models.IntegerField()
    email=models.CharField(max_length=200)
    date=models.DateField(auto_now=True)
    time=models.TimeField(auto_now=True)
    time_taken=models.IntegerField()

class practSummary(models.Model):
    email=models.CharField(max_length=200)
    course=models.ForeignKey(List,on_delete=models.CASCADE)
    topic=models.CharField(max_length=200)
    score_easy=models.FloatField()
    score_med=models.FloatField()
    score_hard=models.FloatField()
    quesCount_easy=models.IntegerField()
    quesCount_med=models.IntegerField()
    quesCount_hard=models.IntegerField()