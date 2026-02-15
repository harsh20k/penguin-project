# AWS Cognito

Cognito is a managed identity service that provides user pools for registration, authentication, and token issuance. It is used for the first authentication factor (user ID and password).

AWS Cognito is a managed identity and access management service. It provides user pools for registration, authentication, and token issuance, and supports configurable password policies and standard authentication flows.

![[1770637231325.gif]]
# DynamoDB

DynamoDB is a managed NoSQL database that stores key–value and document data with low latency and automatic scaling. It stores user profiles, security questions and answers, and Caesar cipher configuration for the second and third authentication factors.

Offers low-latency access and automatic scaling without server management. Suited for user profiles, session data, and other flexible schemas.

# AWS Lambda

Lambda is a serverless compute service that runs code in response to events or API calls. It is used to validate security questions, perform Caesar cipher verification, and read/write data in DynamoDB during multi-factor authentication.


# User Management & Authentication Module

This module implements sign-up validation and multi-factor authentication through a lightweight front-end and backend services. User data is stored in DynamoDB, a NoSQL database.

Authentication uses three factors. The first factor (user ID and password) is handled by AWS Cognito, which manages user pools and credential verification. The second factor (question-and-answer) is validated by Lambda functions that compare user responses with data stored in DynamoDB. The third factor (Caesar cipher) is also validated by Lambda, using cipher configuration and validation data from DynamoDB.

The flow is sequential: Cognito verifies credentials, then Lambda validates the security questions, and finally Lambda validates the Caesar cipher. Access is granted only after all three factors succeed


https://docs.aws.amazon.com/cognito/latest/developerguide/what-is-amazon-cognito.html



Three-Factor Authentication (3FA)

Three-Factor Authentication extends traditional 2FA by requiring three distinct proofs of identity before granting access. In this system, a multi-factor knowledge-based protocol is applied with the following factors:
 

- Factor 1 – Standard Login (Memorized Secret): Username and password establish the initial identity claim.  

- Factor 2 – Security Question (Knowledge-Based Authentication): The user answers pre-configured personal questions, validated against stored data.  

- Factor 3 – Caesar Cipher (Cognitive/Procedural Knowledge): The user solves a Caesar cipher challenge by applying a specified rotation to a given string.
 

### Stateful Authentication and Strict Sequencing

The authentication flow is **stateful** and enforces **Strict Sequential State Enforcement** via a server-side finite state machine (FSM). Each step \(N\) is only accessible if step \(N-1\) has successfully completed and recorded a “done” flag in secure server-side storage. The server, acting as the state authority, denies access to later steps by default (implicit deny) unless the session’s state explicitly indicates successful completion of all prior factors.

NTT DATA (retail client) – Uses Cognito for unified login across e‑commerce and mobile apps.

https://us.nttdata.com/en/blog/2020/april/specialty-retailer-fuels-customer-experience-with-devops-automation-aws-cognito

Purina (Nestlé) – Pet care brand. Uses Cognito for consumer identity and SSO across 14 digital services for 2M+ pet owners.

https://aws.amazon.com/solutions/case-studies/purina-amazon-cognito-case-study/

---

[9 tools called]

### 5. Data Analysis & Visualization Module (academic, concise)

This module provides analytics and reporting layer for all user types. Dispatch operators access an administrative dashboard, implemented with embedded Looker Studio, to monitor key operational metrics such as total clients and login statistics. All users can view client feedback presented in tabular form, retrieved from a data store (e.g., Firestore or Google Cloud Storage). The backend automatically performs sentiment analysis on the collected feedback using a natural language processing API and exposes the resulting sentiment scores and classifications to the front-end for visualisation.

### 6. Web Application Building and Deployment Module (academic, concise)

This module has web application and orchestrates deployment of all backend services. A modern front-end framework (e.g., React) is used to implement the user interface and to invoke backend APIs. The application is containerised and deployed on a managed container platform such as Google Cloud Run or AWS Fargate to ensure scalability. Infrastructure provisioning and configuration are automated using infrastructure-as-code (e.g., AWS CloudFormation or Terraform for cloud agnostic), enabling deployments and consistent environments across development, testing, and production.

---

### Tech stack – links and short descriptions

- **Google Looker Studio**  
  - **Link**: `https://cloud.google.com/looker/docs/studio`  
  - **Description**: A Google data visualisation and reporting tool that lets you build interactive dashboards and embed them into web applications using a wide range of data sources.
- https://support.google.com/looker-studio/answer/9171315

- **Google Firestore**  
  - **Link**: `https://cloud.google.com/firestore/docs`  
  - **Description**: A fully managed, serverless NoSQL document database that stores data in collections and documents, with real-time sync and automatic scaling.

- **Google Cloud Storage**  
  - **Link**: `https://cloud.google.com/storage/docs`  
  - **Description**: An object storage service for storing arbitrary files (e.g., CSV exports, feedback logs) in buckets, with multiple storage classes and strong durability.

https://cloud.google.com/natural-language/docs/analyzing-sentiment

- **Google Cloud Natural Language API**  
  - **Link**: `https://cloud.google.com/natural-language/docs`  
  - **Description**: A managed NLP service that provides sentiment analysis, entity extraction, and text classification, suitable for automatically analyzing user feedback.

- **React**  
  - **Link**: `https://react.dev/`  
  - **Description**: A JavaScript library for building component-based user interfaces, used here to implement the front-end and call backend services via HTTP APIs.

- **Google Cloud Run**  
  - **Link**: `https://cloud.google.com/run/docs`  
  - **Description**: A fully managed serverless container platform that runs HTTP- or event-driven containers, auto-scales to zero, and abstracts away server management.

- **AWS Fargate**  
  - **Link**: `https://aws.amazon.com/fargate/`  
  - **Description**: A serverless compute engine for containers that runs ECS or EKS tasks without managing EC2 instances, provisioning CPU and memory per task.

https://docs.aws.amazon.com/AmazonECS/latest/developerguide/AWS_Fargate.html

- **AWS CloudFormation**  
  - **Link**: `https://docs.aws.amazon.com/cloudformation/`  
  - **Description**: An infrastructure-as-code service that defines AWS resources in templates (YAML/JSON) and deploys them as stacks for repeatable, versioned environments.

- **Google Cloud Deployment Manager**  
  - **Link**: `https://cloud.google.com/deployment-manager/docs`  
  - **Description**: An infrastructure-as-code tool for defining and deploying Google Cloud resources via configuration files; note it is scheduled for end of support in 2026.

[1] “Make a Caesar's Cipher with Python,” Medium, Operaho. https://medium.com/@Operaho/make-a-caesars-cipher-with-python-8958ffa1e90d

[2] “Caesar Cipher Tutorial,” YouTube. https://youtu.be/sMOZf4GN3oc?si=fAsS_-Xa8UfW67Kp

[3] “How Amazon Lex Works,” Amazon Web Services. https://docs.aws.amazon.com/lex/latest/dg/how-it-works.html

[4] “Amazon Lex Overview,” YouTube. https://www.youtube.com/watch?v=-KNnitvr-Hc

[5] “AWS Lambda,” Wikipedia. https://en.wikipedia.org/wiki/AWS_Lambda

[6] “Fan-out Amazon SNS notifications to Amazon SQS queues for asynchronous processing,” Amazon Web Services. https://docs.aws.amazon.com/sns/latest/dg/sns-sqs-as-subscriber.html

[7] “Amazon SQS, Amazon SNS, or Amazon EventBridge?,” Amazon Web Services. https://docs.aws.amazon.com/decision-guides/latest/sns-or-sqs-or-eventbridge/sns-or-sqs-or-eventbridge.html

[8] “What is Amazon Cognito?,” Amazon Web Services. https://docs.aws.amazon.com/cognito/latest/developerguide/what-is-amazon-cognito.html

[9] “Purina Builds a Strategic Consumer IAM Solution for an Optimized User Journey Using Amazon Cognito,” Amazon Web Services. https://aws.amazon.com/solutions/case-studies/purina-amazon-cognito-case-study/

[10] “Looker Studio Help,” Google. https://support.google.com/looker-studio/answer/9171315

[11] “Analyzing Sentiment,” Google Cloud. https://cloud.google.com/natural-language/docs/analyzing-sentiment

[12] “Architect for AWS Fargate for Amazon ECS,” Amazon Web Services. https://docs.aws.amazon.com/AmazonECS/latest/developerguide/AWS_Fargate.html

---
# Original references 
**

# References

[https://medium.com/@Operaho/make-a-caesars-cipher-with-python-8958ffa1e90d](https://medium.com/@Operaho/make-a-caesars-cipher-with-python-8958ffa1e90d)

[https://youtu.be/sMOZf4GN3oc?si=fAsS_-Xa8UfW67Kp](https://youtu.be/sMOZf4GN3oc?si=fAsS_-Xa8UfW67Kp)

  

[https://docs.aws.amazon.com/lex/latest/dg/how-it-works.html](https://docs.aws.amazon.com/lex/latest/dg/how-it-works.html)

[https://www.youtube.com/watch?v=-KNnitvr-Hc](https://www.youtube.com/watch?v=-KNnitvr-Hc)

[https://en.wikipedia.org/wiki/AWS_Lambda](https://en.wikipedia.org/wiki/AWS_Lambda)

AWS docs Fan-out pattern SNS to SQS

[https://docs.aws.amazon.com/sns/latest/dg/sns-sqs-as-subscriber.html](https://docs.aws.amazon.com/sns/latest/dg/sns-sqs-as-subscriber.html)

AWS guide on when to use SNS, SQS 

[https://docs.aws.amazon.com/decision-guides/latest/sns-or-sqs-or-eventbridge/sns-or-sqs-or-eventbridge.html](https://docs.aws.amazon.com/decision-guides/latest/sns-or-sqs-or-eventbridge/sns-or-sqs-or-eventbridge.html)

AWS Cognito

[https://docs.aws.amazon.com/cognito/latest/developerguide/what-is-amazon-cognito.html](https://docs.aws.amazon.com/cognito/latest/developerguide/what-is-amazon-cognito.html)

[https://aws.amazon.com/solutions/case-studies/purina-amazon-cognito-case-study/](https://aws.amazon.com/solutions/case-studies/purina-amazon-cognito-case-study/)

https://support.google.com/looker-studio/answer/9171315

[https://cloud.google.com/natural-language/docs/analyzing-sentiment](https://cloud.google.com/natural-language/docs/analyzing-sentiment)

https://docs.aws.amazon.com/AmazonECS/latest/developerguide/AWS_Fargate.html

**
