# Lab 1 Auth0 - Flask
## Author: Todd O'Neil

[Demo Link](https://www.youtube.com/watch?v=N35v9OeLOoM)

### Requirements
This project requires the following to be installed locally:
- Python 3.12 or higher
- python3-pip
- python3-venv

The above can be installed using
```bash
sudo apt update
sudo apt upgrade
sudo apt install python3 python3-pip python3-venv
```

### Instructions:

#### Step 1:
clone this repository.

#### Step 2:
Once the repo has been clone create a .env in the root of the project with the following variables:
```
AUTH0_DOMAIN=<your domain key>
AUTH0_CLIENT_ID =<your client id>
AUTH0_CLIENT_SECRET=<your client secret>
AUTH0_SECRET=<your secret>
AUTH0_REDIRECT_URI=<your redirect uri>
```
These variables will be populated with the information from your Auth0 application.

#### Step 3: 
Create an free account (if you don't already have one) on [Auth0](https://auth0.com/). After you create your account, on the dashboard navigate to the Applications tab and click Create Application. Select Regular Web Application and give your app a name.  Once it's created click on your newly created application and populate your Environment Variables above with the information provided in your app.  

In order to populate the AUTH0_SECRET variable you will need to generate a key yourself. The following command will generate a hash string.  
```bash
openssl rand -hex 64
```

#### Step 4:
Create a virtual environment for your application with venv
```bash
python3 -m venv venv
source venv/bin/activate
```
this will create the virtual environment and start it.
Once the environment is start run
```bash
pip install -r requirements.txt
```
this will install all required application dependencies.

#### Step 5:
The application should be ready and can be started with the following command:
```bash
python3 app.py
```
this will run the application locally. On first inital run when asked to log in there will be no credentials available so clicking the "register" link/button on the login screen will allow you to use whatever credentials you wish to make up/use i.e. user@test.com.

### How the Application Works (High‑Level Overview)
This Flask app integrates Auth0 authentication into a Python web application. It uses Auth0’s async Python SDK, but because Flask is synchronous, the app includes a small helper (run_async) that safely runs async Auth0 calls inside Flask routes.

When a request comes in, the app stores the Flask request object in g.store_options so the Auth0 SDK can access it. Public routes (like /) check whether a user is logged in by calling auth0.get_user(). If a user is authenticated, their profile is passed to the template; otherwise, the page shows a login option.

The /login route starts the Auth0 login flow by redirecting the user to Auth0’s hosted login page. After authentication, Auth0 redirects back to /callback, where the app completes the login transaction and stores the session.

Protected routes such as /profile and /protected verify the user session; if no user is found, the app redirects to the login page. The /logout route clears the session and redirects the user through Auth0’s logout endpoint before returning them to the home page.

### Things I Learned
I wasn't aware that Flask can have some async issues when using Auth0's async library.  My understanding was that Flask itself was asynchronous but I guess that's not the case.  After doing some reasearch and asking Copilot why I was running into "event loop closed" errors when trying to log in after logging out, that's when I discovered I needed a helper function to aid in that communication.