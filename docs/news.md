# Get News by Partition

### `GET newsroom/v2/news/partition/{rowKey}/{feedId}`
Authorization: `Bearer Token`  
Params: `rowKey, feedId`

## Success Response
**Code:** `200 OK`  
**Example Response:**

```json
[
  {
    "id": "2517391535471890345|10ae62fb-8217-49b1-8db2-5849288bded5",
    "feedId": "2c0b5531-1c53-4053-a031-312e91f2e85b",
    "title": "Become a Student Ambassador",
    "summary": "Earn money, gain skills and build your confidence",
    "created": "2022-09-14T09:20:52.8109807+00:00",
    "updated": "2022-09-14T09:27:50.9637062+00:00",
    "image": "6a373e0b-106a-4fea-88cc-19e502b68419.jpg",
    "body": "",
    "author": "Communications",
    "postedBy": "",
    "importance": "Normal"
  }
]
```