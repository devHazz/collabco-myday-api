# Get Alerts

### `GET alerts/v3?isMobile=false`
**Authorization:** `Bearer Token`  
**HTTP Query Params (Required):** `bool isMobile`

## Success Response
**Code:** `200 OK`  
**Example Response:**

```json
[
  {
            "channelId": "",
            "id": "",
            "ExpiryTime": "2022-09-20T09:35:57.3105596Z",
            "InAppExpiryTime": "2022-09-27T09:35:57.3105597Z",
            "action": "",
            "createdAt": "2022-09-13T09:35:47.8426058+00:00",
            "sentAt": "2022-09-13T09:35:57.3105613+00:00",
            "read": true,
            "inAppDismissed": false,
            "title": "The College will be closed on Monday 19 September",
            "message": "For the state funeral of Queen Elizabeth II",
            "content": null,
            "fcmRegistrationToken": "",
            "sender": "",
            "priority": "High",
            "categories": null,
            "imageUrl": null,
            "videoUrl": null,
            "popup": true,
            "tickbox": false,
            "tickboxText": null,
            "PartitionKey": "",
            "RowKey": "",
            "Timestamp": "2022-09-13T16:17:35.5206649+00:00",
            "ETag": "W/\"datetime'2022-09-13T16%3A17%3A35.5206649Z'\""
  }
]
```  

# Read Alert by ID

### `PUT alerts/v3/read?isMobile=false`
**Authorization:** `Bearer Token`  
**HTTP Query Params (Required):** `bool isMobile`  
**Request Body:** `{"alertIds": [{alertId}]}`

## Success Response
**Code:** `204 No Content`  

# Get Subscriptions

### `GET alerts/v3/subscriptions?isMobile=false`  
**Authorization:** `Bearer Token`  
**HTTP Query Params (Required):** `bool isMobile`  

## Success Response
**Code:** `200 OK`  
**Example Response:**

```json
[
  {
    "channel": {
      "id": "",
      "tenantId": "",
      "name": "essential_alerts",
      "displayName": "1 - Essential alerts all staff and learners",
      "description": "Essential alerts all staff and learners",
      "tags": [],
      "type": "Standard",
      "allowUserPreferences": false,
      "subscriptionOption": "Mandatory"
    },
    "userPreferences": null
  }
]
```  
