# 9fellas

A simple 12 Factor-based demo application written in Python that visualizes the number of instances currently running with cute animal icons. Application instances register themselves in a shared Redis datastore. 

## Commands

- Add threads by using the /addthread endpoint
- Delete threads using /deletethread endpoint
- Applications are hardcoded to send their data to a public application URL, which defaults to 9fellas.cfapps.io and should be changed by setting the all-apps environment variable


## Running 9fellas On Pivotal Web Services

Looking to run 9fellas on Cloud Foundry? Here’s some sample instructions for deploying 9fellas onto the hosted Pivotal Web Services cloud:

1. Make sure you have Git installed, available from https://git-scm.com/ 
2. 2. Login to your Cloud Foundry cloud. You can sign up for a free trial from http://run.pivotal.io. Once you’re signed up, login to your Pivotal Web Services cloud with<br>
  ```
  cf login -a api.run.pivotal.io
  ```
3. Make sure your have the Cloud Foundry CF CLI installed, available from http://docs.run.pivotal.io/devguide/installcf/install-go-cli.html  
4. Clone the 9fellas application into a local directory with<br>
  ```
  git clone https://github.com/mreider/9fellas.git
  ```
5. Deploy the application to create the application route, but don’t start it until you’ve attached the required Redis service. Choose a unique application name and replace “my-app-name”  with that name where it appears. Push the application without starting it using<br>
  ```
  cf push my-app-name --no-start
  ```
6.  Create a shared Redis datastore. PWS offers a free tier 30mb plan that you can provision with<br>
  ```
  cf create-service rediscloud 30mb my-app-name
  ```
7. Bind the Redis instance to your 9fellas app with<br>
  ```
  cf bind-service my-app-name rediscloud
  ```
8. The 9fellas app instances report to a URL using the all-apps environment variable. Set the reporting URL endpoint using<br>
  ```
  cf set-env my-app-name “all-apps” "my-app-name.cfapps.io" 
  ```
9. Restage and start the application with<br>
  ```
  cf push my-app-name  	
	```
10. Scale the app up to 6 instances to see more animal icons appear using<br>
  ```
  cf scale my-app-name -i 6 		
  ```


Afterwards, tear down your app with:
```
cf delete my-app-name 
cf delete-service rediscloud	
cf apps 	# check no apps are found
```
