from django.urls import path
from Link2 import views

urlpatterns = [
    path('', views.Link2, name='Link2'),
    path('crossofff/<list_id>', views.crossofff, name='crossofff'),
    path('courseRO/<cid>', views.courseRO, name='courseRO'),
    path('delete/<list_id>', views.delete, name='delete'),
    path('edit/<cid>', views.edit, name='edit'),
    path('addstud/<list_id>', views.addstud, name='addstud'),
    path('studlist/<sidd>', views.studlist, name='studlist'),
    path('deleteStud/<stud>/<sidd>', views.deleteStud, name='deleteStud'),
    path('courseInfo/<cid>', views.courseInfo, name='courseInfo'),
    path('updatecred/<cid>', views.updatecred, name='updatecred'),
    path('editsyll/<cid>', views.editsyll, name='editsyll'),
    path('editdesc/<cid>', views.editdesc, name='editdesc'),
    path('addTopic/<cid>', views.addTopic, name='addTopic'),
    path('delTopic/<tid>', views.delTopic, name='delTopic'),
    path('addInst/<cid>', views.addInst, name='addInst'),
    path('delInst/<instid>', views.delInst, name='delInst'),
    path('addLink/<cid>', views.addLink, name='addLink'),
    path('delLink/<linkid>', views.delLink, name='delLink'),
    path('addannc/<cid>', views.addannc, name='addannc'),
    path('delannc/<anncid>', views.delannc, name='delannc'),
    path('addassign/<cid>', views.addassign, name='addassign'),
    path('delassign/<assid>', views.delassign, name='delassign'),
    path('studR', views.studR, name='studR'),
    path('CaTdown', views.CaTdown, name='CaTdown'),
    path('CaTdown_', views.CaTdown_, name='CaTdown_'),
    path('RaccessT', views.RaccessT, name='RaccessT'),
    path('RaTdown', views.RaTdown, name='RaTdown'),
    path('RaTdowntype', views.RaTdowntype, name='RaTdowntype'),
    path('assessmenTdown', views.assessmenTdown, name='assessmenTdown'),
    path('deleteSR/<sr>', views.deleteSR, name='deleteSR'),
    path('quesr/<cid>', views.quesr, name='quesr'),
    path('extq/<cid>', views.extq, name='extq'),
    path('delext/<cid>/<extid>', views.delext, name='delext'),
    path('extcontent/<extid>', views.extcontent, name='extcontent'),
    path('bulkext/<cid>/<extid>', views.bulkext, name='bulkext'),
    path('delextcontent/<extid>/<ecid>', views.delextcontent, name='delextcontent'),
    path('editextmarks/<ecid>/<extid>', views.editextmarks, name='editextmarks'),
    path('qn/<pk1>/<cid>', views.qn, name='qn'),
    path('updateqn/<qid>/<pk1>/<cid>', views.updateqn, name='updateqn'),
    path('bulkqn/<pk1>/<cid>', views.bulkqn, name='bulkqn'),
    path('delquesr/<pk1>/<cid>', views.delquesr, name='delquesr'),
    path('delqn/<pk1>/<qpk>/<cid>', views.delqn, name='delqn'),
    path('delpractqn/<pk1>/<cid>', views.delpractqn, name='delpractqn'),
    path('quesRO/<curr_c>', views.quesRO, name='quesRO'),
    path('pretest/<pk1>/<cid>', views.pretest, name='pretest'),
    path('test/<pk1>/<cid>', views.test, name='test'),
    path('qnRO/<pk1>/<cr_crseid>', views.qnRO, name='qnRO'),
    path('reconnect', views.reconnect, name='reconnect'),
    path('evaluateQ/<qnr_att_id>/<qid>/<nextid>', views.evaluateQ, name='evaluateQ'),
    path('qnr_attempts/<pk1>/<cid>', views.qnr_attempts, name='qnr_attempts'),
    path('pq_attempts/<tid>/<cid>', views.pq_attempts, name='pq_attempts'),
    path('qn_attempts/<pk1>/<tid>/<email>', views.qn_attempts, name='qn_attempts'),
    path('email/<pk1>/<cid>', views.email, name='email'),
    path('Raccess/<cid>/<rtype>/<topic>', views.Raccess, name='Raccess'),
    path('searchques/<cid>/<tid>', views.searchques, name='searchques'),
    path('searchques_stud/<cid>', views.searchques_stud, name='searchques_stud'),
    path('getNextPQ/<nextid>', views.getNextPQ, name='getNextPQ'),
    path('evaluatePQ/<qid>/<cid>', views.evaluatePQ, name='evaluatePQ'),
    path('attemptscsv/<pk1>', views.attemptscsv, name='attemptscsv'),
    path('answersheet/<pk1>', views.answersheet, name='answersheet'),
    path('questionspdf/<qnrid>/<tid>', views.questionspdf, name='questionspdf'),
    path('courselogs', views.courselogs, name='courselogs'),
    path('logs', views.logs, name='logs'),
    path('changelive/<cid>/<idd>/<act>/<type>', views.changelive, name='changelive'),
    path('dashboard', views.dashboard, name='dashboard'),
    path('embfiles/<cid>', views.embfiles, name='embfiles'),
    path('add_dataset/<cid>', views.add_dataset, name='add_dataset'),
    path('del_dataset/<dsid>/<cid>', views.del_dataset, name='del_dataset'),
    path('courseAssessmentLogs', views.courseAssessmentLogs, name='courseAssessmentLogs'),
    path('changeLiveLink/<lid>', views.changeLiveLink, name='changeLiveLink'),
    path('changeLiveAssignLink/<lid>', views.changeLiveAssignLink, name='changeLiveAssignLink'),
    path('changeLevelLink/<lid>', views.changeLevelLink, name='changeLevelLink'),
    path('studentResources/<cid>/<tid>', views.studentResources, name='studentResources'),
    path('studentAssignments/<cid>/<tid>', views.studentAssignments, name='studentAssignments'),
    path('resetPractQues/<cid>/<tid>', views.resetPractQues, name='resetPractQues'),
]
