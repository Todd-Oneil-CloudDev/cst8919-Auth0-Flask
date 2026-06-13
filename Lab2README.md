## Lab 2 - Threat Detection And KQL
### Todd O'Neil

### [Link To Demo](https://www.youtube.com/watch?v=XhUaK3iMtUQ)

### Challenges
The largest challenge I faced was handling the failed login attempt logic with Auth0.  Since when logging in with invlaid credentials the IdP does all of the error handling from their end and never invokes the /callback endpoint.

### Suggestions For Improvement
According to Auth0 official documentation you are able to stream Auth0 logs into something like Azure Event Grid.  By doing so the the application gets events for failed login attempts that it normally would not see.  From there configuring the Event Grid to send those events into Log Analytics would be the next step.  This allows for custom KQL queries to be executed.  The Microsoft documentation for configuring Auth0 event streaming into Event Grid can be found here: https://learn.microsoft.com/en-us/azure/event-grid/auth0-how-to

### KQL
```KQL
AppServiceConsoleLogs
| where ResultDescription has "LOGIN_FAILURE"
```
The above KQL query was used to find failed login attempts that were logged by application service and the running application.  Searching for the log level of Error wasn't enough as even successful login attempts are written as Error level rows.

### Things I Learned Part 2 (Lab2)
One thing I was surprised by was that Even successful login attempts logged with pythons 'logger.warning()' produce an Error level row in a Log Analytics Workspace.  Another thing I learned was taht when using Auth0 (and by extention I imagine any IdP) when using the HTTPClient extention to test the login workflow that would produce an error the path variables 
"?code=<'someInvalidToken'>&state=<'somefakevalue'>" must be added. If these are not added and you try to hit the /callback endpoint nothing will happen. Save if you try to use bad credentials in Auth0's actual login page. Auth0 handles the credential error itself on it's own side and /callback is never called.