response = 'Rejected by arn:aws:iam::961354904951:user/sumit'

user = response.split("user/",1)[1]

print(user)