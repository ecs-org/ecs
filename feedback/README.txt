Creating a feedback entry:

curl -F feedbacktype=q -F summary=meep -F description=meep2 -F origin=meep3 -F username=user -F email=user@example.com http://ecsdev.ep3.at:8082/feedback/

Result:
{
    "origin": "meep3", 
    "username": "user", 
    "description": "meep2", 
    "summary": "meep", 
    "id": 1, 
    "feedbacktype": "q", 
    "pub_date": "2009-12-22 14:28:29", 
    "email": "user@example.com"
}

Running the above command 2 times more.

Listing Feedback entries:

curl http://ecsdev.ep3.at:8082/feedback/

Result:
[
    {
        "origin": "meep3", 
        "username": "user", 
        "description": "meep2", 
        "summary": "meep", 
        "id": 1, 
        "feedbacktype": "q", 
        "pub_date": "2009-12-22 14:28:29", 
        "email": "user@example.com"
    }, 
    {
        "origin": "meep3", 
        "username": "user", 
        "description": "meep2", 
        "summary": "meep", 
        "id": 2, 
        "feedbacktype": "q", 
        "pub_date": "2009-12-22 14:33:17", 
        "email": "user@example.com"
    }, 
    {
        "origin": "meep3", 
        "username": "user", 
        "description": "meep2", 
        "summary": "meep", 
        "id": 3, 
        "feedbacktype": "q", 
        "pub_date": "2009-12-22 14:33:19", 
        "email": "user@example.com"
    }
]

curl http://ecsdev.ep3.at:8082/feedback/all/0/1

Result:
[
    {
        "origin": "meep3", 
        "username": "user", 
        "description": "meep2", 
        "summary": "meep", 
        "id": 1, 
        "feedbacktype": "q", 
        "pub_date": "2009-12-22 14:28:29", 
        "email": "user@example.com"
    }
]
curl http://ecsdev.ep3.at:8082/feedback/all//2

Result:
[
    {
        "origin": "meep3", 
        "username": "user", 
        "description": "meep2", 
        "summary": "meep", 
        "id": 1, 
        "feedbacktype": "q", 
        "pub_date": "2009-12-22 14:28:29", 
        "email": "user@example.com"
    }, 
    {
        "origin": "meep3", 
        "username": "user", 
        "description": "meep2", 
        "summary": "meep", 
        "id": 2, 
        "feedbacktype": "q", 
        "pub_date": "2009-12-22 14:33:17", 
        "email": "user@example.com"
    }
]

curl http://ecsdev.ep3.at:8082/feedback/q/meep3/last/1

Result:
[
    {
        "origin": "meep3", 
        "username": "user", 
        "description": "meep2", 
        "summary": "meep", 
        "id": 3, 
        "feedbacktype": "q", 
        "pub_date": "2009-12-22 14:33:19", 
        "email": "user@example.com"
    }
]

curl http://ecsdev.ep3.at:8082/feedback/q/meep2/last/1

Result:
[]

Updating Feedback entries:

curl -F feedbacktype=q -F summary=meep -F description=meep2 -F origin=meep3 -F username=user -F email=user@example.com --request PUT http://ecsdev.ep3.at:8082/feedback/2

Result:
{
    "origin": "meep3", 
    "username": "user", 
    "description": "meep2", 
    "summary": "meep", 
    "id": 2, 
    "feedbacktype": "q", 
    "pub_date": "2009-12-22 14:33:17", 
    "email": "user@example.com"
}

It implements the API as descriped in https://ecsdev.ep3.at/project/ecs/blog/DailyScrum171209, with the following changes:

pk is returned as field id.
feedback posts are returned as JS objects.
pk for PUT is put into the URL part.


