# ecommerce_web_store "homewearstore"

Stack
--
+ Backend: Python(Django)
+ Database: PostgreSQL
+ Frontend: Wepback, Bootstrap
+ Payment service: LiqPay
+ Virtualization: Docker, docker-compose
+ Background Task Queue: Celery
+ Development broker: Redis
+ Production broker: Amazon SQS
+ Server: AWS Elastic Beanstalk
+ Cloud storage: AWS S3 bucket

About
--
"Homewearstore" is ecommerce django project. It's web store for home clothing.

Product can have multiple images. Also it can have multiple colors and sizes i.e variations. And multiple reviews. 

User can buy one or multiple products with 'Liqpay' payment service. User can choose product variation.
He can buy products with or without registration. After that user will receive email with his order information.
When user is registered, he gets access to his dashboard with information about his orders and profile.
He can edit his profile and can change his password, also user can check his wishlist of products.

After registration user receive an activation email to activate his account. User can log in with his email and password.
Because this project has a custom user model.

User can add products or remove products from his wishlist only if he is registered.

User can search products with product name. User can filter products by category, price and price range.

After buying a product user can leave a review(rating and comment) about current product.
Average product rating displayed on product detail page.

For 'add to cart', 'add to wishlist' and 'remove from wishlist' used AJAX requests.

Email are sent using Celery.

Development
--
For development mode redis is used as celery broker. Use docker-compose to run application.

Deployment
--
For production mode Amazon SQS is user as celery broker and for static files and media files is uses Amazon S3 bucket.
App deployed on AWS Elastic Beanstalk. Link: http://django-homewearstore-env.eba-ytvk4fvr.us-west-2.elasticbeanstalk.com/

