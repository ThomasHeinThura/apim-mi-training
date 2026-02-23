# WSO2 APIM MI Advanced Traning.

## Infra Setup.

```sh
# clone the git
git clone https://github.com/ThomasHeinThura/apim-mi-docker.git

# buld docker and run the setup. 
docker compose up --build -d

```

### add `/etc/hosts` the IP and hostname

```
<VM / localhost IP > 	am-uat.example.com api-uat.example.com
```

## Training scope

1. API call with two API auth header
2. API key with header Policy
3. Add app user and fine grain access control.
4. Add advanced app permission creation and deletion.
5. Rest to SOAP genration.
6. SOAP backend to Rest APIs.

### 1. API call with two API header

### 2. API key with header Policy

### 3. Add app user and fine grain access control.

### 4. Add advanced app permission creation and deletion.


1. Sign in to WSO2 API-M Management Console (`https://<Server-Host>:9443/carbon`).
2. Click **Main** → **Registry** →  **Browse** .
   [![img](https://apim.docs.wso2.com/en/4.6.0/assets/img/learn/navigate-main-resources.png)](https://apim.docs.wso2.com/en/4.6.0/assets/img/learn/navigate-main-resources.png)
3. Go to the `/_system/governance/apimgt/applicationdata/workflow-extensions.xml` resource, click on `Edit as text` to edit the file, disable the Simple Workflow Executor, and enable **Approval Workflow Executor** for application creation.
   ```xml
   <WorkFlowExtensions>
       <!-- API Revision Deployment -->
       <APIRevisionDeployment executor="org.wso2.carbon.apimgt.impl.workflow.APIRevisionDeploymentSimpleWorkflowExecutor"/>
     
       <!-- Application Creation - APPROVAL WORKFLOW ENABLED -->
       <!--ApplicationCreation executor="org.wso2.carbon.apimgt.impl.workflow.ApplicationCreationSimpleWorkflowExecutor"/-->
       <ApplicationCreation executor="org.wso2.carbon.apimgt.impl.workflow.ApplicationCreationApprovalWorkflowExecutor"/>
     
       <!-- Application Registration - Production -->
       <ProductionApplicationRegistration executor="org.wso2.carbon.apimgt.impl.workflow.ApplicationRegistrationSimpleWorkflowExecutor"/>
     
       <!-- Application Registration - Sandbox -->
       <SandboxApplicationRegistration executor="org.wso2.carbon.apimgt.impl.workflow.ApplicationRegistrationSimpleWorkflowExecutor"/>
     
       <!-- Subscription Creation -->
       <SubscriptionCreation executor="org.wso2.carbon.apimgt.impl.workflow.SubscriptionCreationSimpleWorkflowExecutor"/>
     
       <!-- Subscription Update -->
       <SubscriptionUpdate executor="org.wso2.carbon.apimgt.impl.workflow.SubscriptionUpdateSimpleWorkflowExecutor"/>
     
       <!-- User Signup -->
       <UserSignUp executor="org.wso2.carbon.apimgt.impl.workflow.UserSignUpSimpleWorkflowExecutor"/>
     
       <!-- Subscription Deletion -->
       <SubscriptionDeletion executor="org.wso2.carbon.apimgt.impl.workflow.SubscriptionDeletionSimpleWorkflowExecutor"/>
     
       <!-- Application Deletion -->
       <ApplicationDeletion executor="org.wso2.carbon.apimgt.impl.workflow.ApplicationDeletionSimpleWorkflowExecutor"/>
     
       <!-- API State Change -->
       <APIStateChange executor="org.wso2.carbon.apimgt.impl.workflow.APIStateChangeSimpleWorkflowExecutor"/>
     
       <!-- API Product State Change -->
       <APIProductStateChange executor="org.wso2.carbon.apimgt.impl.workflow.APIProductStateChangeSimpleWorkflowExecutor"/>
     
   </WorkFlowExtensions>

   ```

### 5. Rest to SOAP genration.
