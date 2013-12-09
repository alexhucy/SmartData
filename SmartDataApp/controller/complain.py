#coding:utf-8
import datetime
from django.http import HttpResponse
import simplejson
from django.contrib.auth.decorators import login_required
from django.shortcuts import render_to_response, redirect
from django.views.decorators.csrf import csrf_exempt
from django.db import transaction
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.contrib.auth.models import User
from SmartDataApp.models import Complaints
from SmartDataApp.views import index
from SmartDataApp.models import ProfileDetail

def return_error_response():
    response_data = {'error': 'Just support POST method.'}
    return HttpResponse(simplejson.dumps(response_data), content_type='application/json')

def return_404_response():
    return HttpResponse('', content_type='application/json', status=404)

@csrf_exempt
@login_required(login_url='/login/')
def complain(request):
        if not request.user.is_staff:
            return render_to_response('complains.html', {'user': request.user})
        else:
            complains = Complaints.objects.all()
            deal_person_list = ProfileDetail.objects.filter(is_admin=True)
            if len(complains) > 0:
                return render_to_response('admin_complains.html', {
                    'complains': list(complains),
                    'show': True,
                    'user': request.user,
                    'deal_person_list':deal_person_list
                })
            else:
                return render_to_response('admin_complains.html', {
                    'show': False,
                    'user': request.user
                })

@transaction.atomic
@csrf_exempt
def complain_create(request):
    if request.method != u'POST':
        return redirect(index)
    else:
        complain_content = request.POST.get('content', None)
        complain_type = request.POST.get('category', None)
        upload__complain_src = request.FILES.get('upload_complain_img', None)
        complain_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%I:%S")
        if complain_content or complain_type:
            complain = Complaints(author=request.user)
            complain.content = complain_content
            complain.timestamp = complain_time
            complain.type = complain_type
            if upload__complain_src:
                complain.src = upload__complain_src
            complain.save()
            return render_to_response('complain_sucess.html', {'user': request.user})
        else:
            return render_to_response('complains.html', {'user': request.user})


@transaction.atomic
@csrf_exempt
def complain_deal(request):
    if request.method != u'POST':
        return redirect(index)
    else:
        complain_array = request.POST.get("selected_complain_string", None)
        deal_person_id = request.POST.get("deal_person_id", None)
        if complain_array and deal_person_id:
            list_complain_ = str(complain_array).split(",")
            for i in range(len(list_complain_)):
                com_id = int(list_complain_[i])
                complain = Complaints.objects.get(id=com_id)
                complain.status = True
                user_obj = User.objects.get(id=deal_person_id)
                if user_obj:
                    profile = ProfileDetail.objects.get(profile=user_obj)
                    complain.handler.add(profile)
                complain.save()
            response_data = {'success': True, 'info': '授权成功！'}
            return HttpResponse(simplejson.dumps(response_data), content_type="application/json")

@transaction.atomic
@csrf_exempt
def own_complain(request):
    complains=Complaints.objects.filter(author=request.user)
    profile=ProfileDetail.objects.get(profile=request.user)
    if len(complains) > 0:
        paginator = Paginator(complains, 5)
        page = request.GET.get('page')
        try:
            complains_list = paginator.page(page)
        except PageNotAnInteger:
            complains_list = paginator.page(1)
        except EmptyPage:
            complains_list = paginator.page(paginator.num_pages)
        return render_to_response('own_complain.html', {
                        'complains':complains_list,
                        'user':request.user,
                        'profile':profile ,
                        'show': True
                    })
    return render_to_response('own_complain.html',{ 'show': False ,'user':request.user,'profile':profile })


@transaction.atomic
@csrf_exempt
@login_required
def complain_response(request):
    if request.method != u'POST':
        return redirect(index)
    else:
        complain_id = request.POST.get("complain_id", None)
        response_content = request.POST.get("response_content", None)
        selected_pleased = request.POST.get("selected_radio", None)
        profile=ProfileDetail.objects.get(profile=request.user)
        complain=Complaints.objects.get(id=complain_id)
        if complain:
            complain.pleased_reason=response_content
            complain.pleased=selected_pleased
            complain.save()
            response_data = {'success': True, 'info': '评论成功！'}
            return HttpResponse(simplejson.dumps(response_data), content_type="application/json")
        else:
            return render_to_response('own_complain.html',{ 'show': True ,'user':request.user,'profile':profile })


@transaction.atomic
@csrf_exempt
@login_required
def api_complain_create(request):
    if request.method != u'POST':
        return return_error_response()
    else:
        complain_content = request.POST.get('content', None)
        complain_type = request.POST.get('category', None)
        upload__complain_src = request.FILES.get('upload_complain_img', None)
        complain_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%I:%S")
        if complain_content or complain_type:
            complain = Complaints(author=request.user)
            complain.content = complain_content
            complain.timestamp = complain_time
            complain.type = complain_type
            if upload__complain_src:
                complain.src = upload__complain_src
            complain.save()
            return HttpResponse(simplejson.dumps({'error': False, 'info': u'投诉创建成功'}),content_type='application/json')
        else:
            return HttpResponse(simplejson.dumps({'error': True, 'info': u'请选择投诉类型或填写投诉内容'}),
                                    content_type='application/json')



