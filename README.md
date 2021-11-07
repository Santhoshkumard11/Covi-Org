# Covi-Org
Covi Org is a Power App that provides you the ability to view trends and tracker your employees status and alert co-workers in case of emergency. It can help you collect vaccination status and other details in just click of a button through Outlook Actionable Message. Send periodic notification to all the unvaccinated employees to update their status (configurable). The most important feature is generating near real-time graphs with the data from Cosmos DB.

## YouTube Demo Video 📺📺

[Youtube Link](https://youtube.com)

## Architecture Diagram
<img src="https://github.com/Santhoshkumard11/Covi-Org/blob/main/images/architecture_diagram.png" height="380" width="1300" alt="architecture diagram">

## Power Apps Content
<img src="https://github.com/Santhoshkumard11/Covi-Org/blob/main/images/flow_diagram.png" alt="Content">


## Services Used
- __Power Apps__
- __Power Automate__
- Azure Cosmos DB
- Azure Blob Storage
- Adaptive Cards (Outlook Actionable Message)

## Power Automate Flows
Send Adaptive Card - compose and send adaptive cards via mail
Adaptive Card Receiver - receive the submit trigger from adaptive card and updated the document in Cosmos DB
Send Email Notification - Send an email notification or an email to all your surrounding people (Get Relevant People from Office 365 Users is used) 


## Sample Graphs
<img src="https://github.com/Santhoshkumard11/Covi-Org/blob/main/images/graph-1.png" height="580" alt="Content">

<img src="https://github.com/Santhoshkumard11/Covi-Org/blob/main/images/graph-2.png" height="580" alt="Content">

<img src="https://github.com/Santhoshkumard11/Covi-Org/blob/main/images/graph-3.png" height="580" alt="Content">

## TODO:

