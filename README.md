# API-IMAGE

This is a small Django Rest Framework (DRF) project that allows users to upload images and obtain links to their thumbnails.

## INSTALATION

With Docker

1. Clone this reposotory to your local machine: https://github.com/MateuszSwist/Api-Image.git.
2. Type some password in settings SECRET_KEY
3. In your shell enter directory with file docker-compose.
4. Type 'docker-compose up'.
5. Now u can login on localhost:8000/admin/, there is preloaded superuser with login: admin password: admin.

Without Docker

1. Clone this reposotory to your local machine: https://github.com/MateuszSwist/Api-Image.git.
2. Type some password in settings SECRET_KEY
3. Create venv:
- python -m venv venv
- source venv/bin/activate
- pip install -r requirements.txt
4. Make initial migrations: python manage.py migrate.
5. Load initial data: python manage.py loaddata fixtures/01.built_in_account_tiers.json.
6. Create superuser.
7. Now u can login on localhost:8000/admin/.


The project includes 3 build-in levels of accounts: Basic, Premium, and Enterprise.

## Capabilities

In the project, I have adopted a model where each user has their own client account with a specific tier. 
To allow a registered user to use the API, they need to be assigned a client account first. In the future, 
it would be a good idea to implement automatic association of a user's newly created account with a basic 
client account during user registration. We have three built-in account tiers available, but the admin can 
create new account tiers with custom capabilities, such as specifying different thumbnail sizes, adding any 
number of generated thumbnails with specific dimensions, determining the generation of links to the original 
image and an time expiring link.


## Endpoints

  Authorization ie set up on basic option (BasicAuthentication, SessionAuthentication)
  
1. "add-image/" - In the HTTP request, the user needs to be authorized and an image should be added. Subsequently,
   the application saves images with appropriate sizes on the disk (in this case, in the media/ folder within the
   project directory) depending on the user's account tier. It returns links under which the images can be displayed.

2. "image/int:pk/" - In this request, the user provides the ID of their image (which they receive when generating a link)
   and can retrieve the link to the specific image again.

3. "images/" In this request user get a list with all images (generated links).

4. "time-expiring/" - In this request, the user must authenticate in the request body, provide the image ID that they
   previously uploaded to the website, and specify the expiration time for the link (in seconds, minimum 300,
   maximum 30000). In response, they will receive a link and secound to expire value.
 
5. "time-expiring/str:link_name/" - In this endpoint, in the response, we provide the image associated with a previously
   generated time-expiring link or information about its expiration. No authentication is required.

## Admin panel

In the project, I have extended the admin panel, striving to make it transparent and providing all the essential 
functions for management. You can add new thumbnail sizes, create custom account tiers, and save them under 
specific names. It's easy to check the generated links along with information about the thumbnail sizes they lead to 
or the remaining time until expiration in the case of time-expiring links.

## Tests and validation

According to the coverage data, the project is covered by unit tests at 98%. I have made efforts to sensibly 
validate data, preventing the input of absurd data such as negative image sizes or adding images in formats 
other than required. At the same time, I have avoided excessive querying of the database when it is unnecessary.

## Future ideas

In the future, it would be worthwhile to consider at least three things. Mentioned earlier by me is the automatic 
association of users with client accounts. It would be good to contemplate the implementation of a queuing system 
like Celery to handle a large number of requests asynchronously. Additionally, it would certainly be valuable to connect 
the application to some cloud service like Google Cloud to store uploaded images there. This way, image resizing could be 
offloaded to the cloud, which would relieve the application.

## Author comment

The code I have created is a solution to a recruitment task. At first glance, it seemed simple to me, but over time, 
it turned out that there were several important dilemmas to address, and the choice of a specific algorithm was not so 
straightforward. The most interesting part of it, in my opinion, is its flexibility in handling different types 
of accounts. The application can handle any configuration, regardless of the permissions we grant it or how many 
and what kind of thumbnails we want to generate.

Mateusz Świst
