# 9fellas
##Overview
This will show the instances being added to pivotal web service in CF

For each instance , at the index.html it will show one row of animals.
For each thread , an animal picutre is shown

You can add threads by using end point /addthread
Delete thread using /deletethread

Instance to which , adding thread and deleteing thread is decided by load balancer
Based on the load balancer's decision thread is added to some particular instance and it's tracked.

##Registering application

Go to application url then register

eg :

http://cute-party3.cfapps.io/register

Then , if you want to see the application details use any of these applications , and endpoint /applications

http://cute-party1.cfapps.io/applications

or 

http://cute-party3.cfapps.io/applications