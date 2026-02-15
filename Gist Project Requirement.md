# **WinterCloud Dispatch System (WCDS)**
**CSCI 5410 / W26 – Project Summary**
## **Project Overview**
- **Title:** WinterCloud Dispatch System (WCDS)
- **Team Size:** ~3 members
- **Duration:** ~2.5 months
- **Objective:**
    Build a **serverless, multi-cloud data plumbing system** to manage winter service requests (snow removal, de-icing, etc.) with role-based access, automation, messaging, analytics, and a simple web UI.
---

## **Core Concept**
- Serverless architecture
- Multi-cloud deployment (AWS + GCP)
- Backend-as-a-Service (BaaS)
- Event-driven, on-demand processing
- Easy-to-use web interface
---

## **User Types & Capabilities**
### **1. Guests**
- View service availability and pricing
- Use virtual assistant for navigation
- View aggregated service feedback and sentiment
### **2. Registered Clients (Customers)**
- All Guest features
- Registration & login notifications
- **3-step sequential MFA**
    1. Username/Password (AWS Cognito)
    2. Security Question/Answer
    3. Caesar Cipher challenge
- Book services (date & time)
- Chatbot for booking reference details
- Communicate with dispatch operators
- Submit service feedback
### **3. Dispatch Operators (Admins/Franchise)**
- All Guest features
- Same 3-step MFA
- Manage services (add/update pricing, discounts)
- Retrieve booking details
- Asynchronous communication with clients
- View analytics and dashboards
---
## **Mandatory Serverless Modules**
### **1. User Management & Authentication**
- AWS Cognito + Lambda + DynamoDB
- Sequential MFA implementation
- NoSQL-based user storage
### **2. Virtual Assistant (Chatbot)**
- **AWS Lex + Lambda + DynamoDB**
    **OR**
    **GCP Dialogflow + Cloud Functions + Firestore**
- Navigation help
- Booking lookup
- Client concern intake
### **3. Message Passing**
- GCP Pub/Sub
- Client issues published → randomly assigned dispatch operator
- All messages logged in NoSQL DB
### **4. Notifications**
- AWS SNS + SQS
- Registration, login, booking success/failure
- Event-driven workflows using queues and Lambdas
### **5. Data Analysis & Visualization*
- Feedback sentiment analysis using NLP API
- Feedback displayed for all users
- Admin dashboard (e.g., Looker Studio)
- Login stats and total clients
### **6. Web Application & Deployment**
- Frontend: React (or similar)
- Hosting: AWS Fargate or GCP Cloud Run
- Infrastructure: CloudFormation or GCP Deployment Manager.
---
## **Testing & Quality Requirements**
- Authentication success/failure tests.
- Chatbot valid/invalid utterances
- API & Lambda/Cloud Function testing
- Database integrity checks
- Screenshots required as evidence
- Maintain clean, readable, reusable code
- Regular Git commits (especially Sprint 2 & 3)
- Use project management tools
---
## **Deliverables & Timeline**
### **Sprint 1 – 25%**
- 5-page planning & research report
- Meeting logs (mandatory)
- Non-evaluative Q&A with Project Lead
- **Due:** Feb 5, 2026
### **Sprint 2 – 25%**
- 4+ page report
- Architecture design
- At least 2 completed modules
- Pseudocode, flowcharts, Gantt chart
- **Due:** Mar 6, 2026
### **Sprint 3 – 25%**
- Final 4-page report
- Complete system implementation
- Full testing & documentation
- **Due:** Apr 6, 2026
### **Final Q&A – 10%**
- 20–30 min group session
- **Window:** Mar 23–31, 2026
### **Final Demo / Presentation – 15%**
- 40-min individual contribution video
- 5-min silent app demo
- **Due:** Mar 31, 2026
---
## **Academic Integrity & Conduct**
- No collaboration outside assigned team
- No verbatim copying; proper citations required
- **AI tools are NOT allowed**
- Equal contribution expected
- Individual grades may vary
- Respectful behavior mandatory (“Culture of Respect”)
---
## **Evaluation Criteria**
- Completeness
- Correctness
- Novelty
- Clarity
- Evidence of group work & coordination
---
