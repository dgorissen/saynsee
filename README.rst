Motivation
==========

The idea for Say & See arose from the frustrations of using Skype to communicate with distant family and relatives.
Particularly if those relatives are not very technologically literate.  What happened in practise was that every 
few months I would write down all instructions on a piece of paper, painstakingly explain how everything worked and
hope that something stuck.

However, after a while they would loose the piece of paper, get infected by malaware, Skype/Windows would install
an updated and things no longer worked as before, forget their username, password, or email address, etc, etc.  

So, I really needed a video chat service that:

* did not require a local installation or special, expensive hardware (e.g., iPad)
* worked out of the box
* had NO passwords or usernames that could be forgotten
* did not require an email address
* no contact lists (especially where ones person can appear multiple times)
* has a very, very, very, simple, barebones UI

You get the point.  

For a tech savy person this may seem silly but you would be suprised at how many people already have problems dealing
with email.  However, if such users have family/friends in distant places, the computer and Internet provide a wonderful opportunity for
them to stay in touch.  The problem is that its just not easy enough for some people.

A group of us got the chance to develop this idea at the Google/FutureGov Interactivism event.  What you see here is a cleaned up
version of the initial prototype that was thrown together in (literally) a couple of hours. 

The site is currently hosted at http://www.saynsee.com

Implementation
===============

The first reaction of developers is of course "how are you going to authenticate?", "what about spammers?", etc.

The initial idea was to use phone/sms based authentication, but we needed something working so we started with email.
Eventually you could think about more fancy mechanism such as face recognition or waving a QR code in front of the camera.

Anyways, the prototype is a very thin Django-nonrel wrapper (since we are running on appengine) around the tokbox API.
Do a grep for "TODO:" and you will notice there are quite a few things left to do :)  However, the main functionality should be there.
That being said:

  **The current code is prototype, proof of principle code and not secure, pretty, or production ready in any way.  It will eat your cat,
  dog, pet goldfish, and I'm quite sure it will take one of your children too if you're not looking.**

The good news is, though, that you can help do something about it. The codebase is very simple, small and easy to get into. And by
helping grandma stay in touch with little Amy, you would be helping society as well.

Installation
============

* Download and install the `GAE Python SDK <http://code.google.com/appengine/downloads.html#Google_App_Engine_SDK_for_Python>`_. 
* Follow the `Django-nonrel installation instructions <http://www.allbuttonspressed.com/projects/djangoappengine>`_.  
* Make sure autoload, dbindexer, django, djangoappengine, djangotoolbox are linked into the src folder.
* running "python manage.py" should get you going.

Thoughts, comments, questions? Drop me a line at dgorissen@gmail.com