from django.contrib.auth.decorators import login_required
from django.shortcuts import render_to_response
from django.http import HttpResponseRedirect
from django.contrib.auth.models import User
from django.template import RequestContext
from django.contrib.auth import authenticate, login
from django.contrib.auth import logout
from django.core.mail import send_mail
import random
import string
from saynsee.models import ChatRequest
import smtplib
import settings
from saynsee import captcha
from saynsee.OpenTokSDK import OpenTokSDK
import re

# TODO: Stop hardcoding view urls

# TODO: use djangos error handling system
# Simply redirect to a page that will display the passed error message
def display_error(request, msg):
    return render_to_response("error.html", {'msg':msg}, context_instance=RequestContext(request))

@login_required
# The main page from where you can invite people
def main(request):
    return render_to_response('main.html', {}, context_instance=RequestContext(request))

@login_required
# The page shown while we are waiting for the user to verify his email address
def verify_wait(request):
    return render_to_response('verify_wait.html', {}, context_instance=RequestContext(request))

# Verify the user owns the email address
def verify_user(request):
    # TODO: use a token of some sort instead of an email address
    email = request.GET.get('email', None)
    
    if not email:
        return display_error(request,"Please wait for the verification email")
    else:
        try:
            # Check if the user exists in Django's local database
            user = User.objects.get(username=email)
        except User.DoesNotExist:
            return display_error(request,"No verification request was put in for this email address")

    if user.is_authenticated():
        # user is already logged in, ignore
        pass
    else:
        # user exsits, authenticate the user and log him in
        # TODO: fixed password
        # TODO: refactor auth code to single fun
        pwd = "qwerty123"
        user = authenticate(username=email, password=pwd)
        
        if user is not None:
            login(request, user)
        else:
            return display_error(request,"Unable to authenticate")
    
    # ensure user is active
    user.is_active = True
    user.save()
    
    # redirect to the main page
    return HttpResponseRedirect('/main')

def chat(request, token):
    
    # if we are running locally run tokbox in sandbox mode
    testmode = request.META['REMOTE_ADDR'] == '127.0.0.1'
    
    if testmode:
        apikey = 1127;
        auth_token = 'devtoken';
        sid = '153975e9d3ecce1d11baddd2c9d8d3c9d147df18';
    else:        
        if not token or token == "/":
            return display_error(request, "You were not invited.")
        
        # check if the token is valid
        try:
            req = ChatRequest.objects.get(token=token)
        except:
            return display_error(request,"Invalid token used.")

        apikey = settings.TOKBOX_API_KEY
        auth_token = req.auth_token
        sid = req.session_id
    
    # TODO: remove token after chat or support auto-expire
    data = {
            'token':token,
            'apikey': apikey,
            'auth_token':auth_token,
            'sid':sid,
            'testmode': testmode
            }
    
    return render_to_response("chat.html", data, context_instance=RequestContext(request))

# Simple email validation
def valid_email(email):
    return re.match("^[a-zA-Z0-9._%-+]+@[a-zA-Z0-9._%-]+.[a-zA-Z]{2,6}$", email)

@login_required
def invite(request):

    # Check the user is active, else he is not allowed to invite
    if not request.user.is_active:
        return HttpResponseRedirect('/verify_wait')
    
    # TODO: use django model forms
    if request.method == 'POST':
        email = request.POST.get('email')

        if not valid_email(email):
            return display_error(request, "Invalid email address")
            
        # create our simple token
        # Keep it short and simple so, for example, its easy to communicate over phone/sms
        inviter = request.user.username
        # TODO: token may already exist!
        token = ''.join(random.choice(string.digits) for x in range(6))
        
        # TODO: reuse old sessions?
        # create a new tokbox session
        production_mode = request.META['REMOTE_ADDR'] != '127.0.0.1'
        
        opentok = OpenTokSDK(settings.TOKBOX_API_KEY,settings.TOKBOX_API_SECRET, production_mode)
        session = opentok.create_session(request.META['REMOTE_ADDR'], properties={})
        sid = session.session_id

        # create the invite url
        url = "%s/chat_%s" % (settings.SITE_URL,token)
        
        #send email
        # TODO: move to separate file
        body = """Hello,
            
You have been invited to video chat by %s. Please click here to accept and start: 
                
         %s

Note that the invitation will expire in 24 hours.
                    
Thanks,
                
The Say & See Team"""  % (inviter,url)

        try:
            send_mail('Say & See invitation', body, settings.FROM_EMAIL, [email], fail_silently=False)
            
            # save the request
            
            # generate an authentication token
            auth_token = opentok.generate_token(sid)
            # Store the request in the DB
            # Note: using the db to communicate the sid/auth token (instead of the url)
            # since this makes it easier to also support SMS (only require our own short token)
            req = ChatRequest(fromUser=request.user,
                              toUser=email,
                              token=token,
                              session_id=sid,
                              auth_token=auth_token)
            req.save()
            
        except smtplib.SMTPException, e:
            #TODO: better error handling
            return display_error(request,"Failed to send the invitation email.")                
        
        # invitation sent
        # forward to the chat window
        return HttpResponseRedirect('/chat_%s' %(token))

    else:
        return HttpResponseRedirect('/main')

# TODO: only create user on verification, not on login (cleaner)
# TODO: support OpenID
def dologin(request):
    
    html_captcha = captcha.displayhtml(settings.RECAPTCHA_PUB_KEY)
    
    if request.method == 'POST':
        
        check_captcha = captcha.submit(request.POST['recaptcha_challenge_field'],
                        request.POST['recaptcha_response_field'],
                        settings.RECAPTCHA_PRIVATE_KEY, request.META['REMOTE_ADDR'])
        
        #TODO: dont redirect but use ajax
        if not check_captcha.is_valid:
            return display_error(request,"You filled in the wrong capcha value, please try again")
        
        # TODO: use the django form api + allow users to set a friendly username
        email = request.POST.get('email')
        # TODO: not used, using fixed pwd
        p1 = request.POST.get('password1')
        p2 = request.POST.get('password2')
        pwd = "qwerty123"
        
        if not valid_email(email):
            return display_error(request, "Invalid email address")
        
        existed = False
        
        try:
            # Check if the user already exists in Django's local database
            user = User.objects.get(username=email)
            existed = True
        except User.DoesNotExist:
            # create the user
            # TODO: empty password used
            user = User.objects.create_user(email,email,pwd)
            # disable user until verified (will block sending invites)
            user.is_active = False;
            user.save()
        
        # is he active?
        is_active = user.is_active
        
        # authenticate the user and log him in
        user = authenticate(username=email, password=pwd)
        
        if user is not None:
            login(request, user)
            if existed:
                if is_active:
                    return HttpResponseRedirect('/invite')
                else:
                    return HttpResponseRedirect('/verify_wait')
            else:
                # TODO: use a unique verification token & record stored in db
                
                # send him the verification message
                body = """Welcome to Say & See !  

Please click here to verify your email address:
                        
    %s/verify_user?email=%s
                                
Thanks,
                        
The Say & See Team""" %(settings.SITE_URL,email)
                
                try:
                    send_mail('Say & See verification', body, settings.FROM_EMAIL, [email], fail_silently=False)
                except smtplib.SMTPException, e:
                    #TODO: better error handling
                    return display_error(request,"Failed to send the verification email, sorry.")
                
                return render_to_response('verify_wait.html', {'isphone':False}, context_instance=RequestContext(request))
        else:
            return display_error("Sorry, you were unable to authenticate.")

    else:
        return render_to_response("login.html", {'html_captcha': html_captcha},context_instance=RequestContext(request))

@login_required
def dologout(request):
    logout(request)
    # TODO: dont hardcode login url
    return HttpResponseRedirect('/accounts/login/')
