from django.contrib import admin
from .models import List,links,instructors,assignments,announcements,studList,studRecords,questr,ques,resAccess,qnr_attempt,qn_attempt,saved_models,practqn_attempt,extqnr,ext_attempt
# Register your models here.
admin.site.register(List)
admin.site.register(links)
admin.site.register(instructors)
admin.site.register(assignments)
admin.site.register(announcements)
admin.site.register(studList)
admin.site.register(studRecords)
admin.site.register(questr)
admin.site.register(ques)
admin.site.register(resAccess)
admin.site.register(qnr_attempt)
admin.site.register(qn_attempt)
admin.site.register(saved_models)
admin.site.register(practqn_attempt)
admin.site.register(extqnr)
admin.site.register(ext_attempt)