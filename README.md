# flask-boiler

[![Build Status](https://travis-ci.com/billyrrr/flask-boiler.svg?branch=master)](https://travis-ci.com/billyrrr/flask-boiler)
[![Coverage Status](https://coveralls.io/repos/github/billyrrr/flask-boiler/badge.svg?branch=master)](https://coveralls.io/github/billyrrr/flask-boiler?branch=master)
[![Documentation Status](https://readthedocs.org/projects/flask-boiler/badge/?version=latest)](https://flask-boiler.readthedocs.io/en/latest/?badge=latest)

"boiler": **B**ackend-**O**riginated **I**nstantly-**L**oaded **E**ntity **R**epository 

Flask-boiler manages your application state with Firestore. 
You can create view models that aggregates underlying data 
sources and store them immediately and permanently in Firestore. 
As a result, your front end development will be as easy as 
using Firestore. Flask-boiler is comparable to Spring Web Reactive. 

Demo: 

When you change the attendance status of one of the participants 
in the meeting, all other participants receive an updated version 
of the list of people attending the meeting. 

![Untitled_2](https://user-images.githubusercontent.com/24789156/71137341-be0e1000-2242-11ea-98cb-53ad237cac43.gif)



Some reasons that you may want to use this framework:
- The automatically documented API accelerates your development
- You want to use Firestore to build your front end, but
    you have to give up because your data contains many
    relational reference
- You want to move some business logic to back end
- You are open to trying something new and contributing to a framework
- You want to develop a new reactive service to your existing flask app

This framework is at ***beta testing stage***. 
API is not guaranteed and ***may*** change. 

Documentations: [readthedocs](https://flask-boiler.readthedocs.io/)

Quickstart: [Quickstart](https://flask-boiler.readthedocs.io/en/latest/quickstart_link.html)

API Documentations: [API Docs](https://flask-boiler.readthedocs.io/en/latest/apidoc/flask_boiler.html)

Example of a Project using flask-boiler: [gravitate-backend](https://github.com/billyrrr/gravitate-backend)

## Installation
In your project's requirements.txt, 

```

# Append to requirements, unless repeating existing requirements

google-cloud-firestore
flask-boiler  # Not released to pypi yet 

```

Configure virtual environment 
```
pip install virtualenv
virtualenv env
source env/bin/activate
```

In your project directory, 

```
pip install -r requirements.txt
```

See more in [Quickstart](https://flask-boiler.readthedocs.io/en/latest/quickstart_link.html). 

<!--## Usage-->

<!--### Business Properties Binding-->
<!--You can bind a view model to its business properties (underlying domain model).-->
<!--See `examples/binding_example.py`. (Currently breaking)-->

<!--```python-->

<!--vm: Luggages = Luggages.new(vm_ref)-->

<!--vm.bind_to(key=id_a, obj_type="LuggageItem", doc_id=id_a)-->
<!--vm.bind_to(key=id_b, obj_type="LuggageItem", doc_id=id_b)-->
<!--vm.register_listener()-->

<!--```-->

### State Management

You can combine information gathered in domain models and serve them in Firestore, so 
that front end can read all data required from a single document or collection, 
without client-side queries and excessive server roundtrip time. 

There is a medium [article](https://medium.com/resolvejs/resolve-redux-backend-ebcfc79bbbea) 
 that explains a similar architecture called "reSolve" architecture. 

See ```examples/meeting_room/view_models``` on how to use flask-boiler 
to expose a "view model" in firestore that can be queried directly 
by front end without aggregation.  

### Save data

```python

from flask_boiler.domain_model import DomainModel
from flask_boiler import attrs

class City(DomainModel):

    city_name = attrs.bproperty()
    country = attrs.bproperty()
    capital = attrs.bproperty()

    class Meta:
        collection_name = "City"
    
City.new(
        doc_id='SF',
        name='San Francisco',
        state='CA', 
        country='USA', 
        capital=False, 
        populations=860000,
        regions=['west_coast', 'norcal']).save()

# ...
```

### Relationship

Flask-boiler adds an option to retrieve a relation with 
minimal steps. Take an example given from SQLAlchemy, 

```python
category_id = utils.random_id()
py = Category.new(doc_id=category_id)
py.name = "Python"

post_id = utils.random_id()
p = Post.new(doc_id=post_id)
p.title = "snakes"
p.body = "Ssssssss"

# py.posts.append(p)
p.category = py

p.save()

```

See ```examples/relationship_example.py```

### Automatically Generated Swagger Docs
You can enable auto-generated swagger docs. See: `examples/view_example.py`



### Create Flask View
You can create a flask view to specify how a view model is read and changed.

```python


app = Flask(__name__)

meeting_session_mediator = view_mediator.ViewMediator(
    view_model_cls=MeetingSession,
    app=app,
    mutation_cls=MeetingSessionMutation
)
meeting_session_mediator.add_list_get(
    rule="/meeting_sessions",
    list_get_view=meeting_session_ops.ListGet
)

meeting_session_mediator.add_instance_get(
    rule="/meeting_sessions/<string:doc_id>")
meeting_session_mediator.add_instance_patch(
    rule="/meeting_sessions/<string:doc_id>")

user_mediator = view_mediator.ViewMediator(
    view_model_cls=UserView,
    app=app,
)
user_mediator.add_instance_get(
    rule="/users/<string:doc_id>"
)

swagger = Swagger(app)

app.run(debug=True)


```

## Object Lifecycle

### Once

Object created with ```cls.new``` -> 
Object exported with ```obj.to_view_dict```. 

### Multi

Object created when a new domain model is created in database -> 
Object changed when underlying datasource changes -> 
Object calls ```self.notify``` 

## Advantages

### Decoupled Domain Model and View Model
Using Firebase Firestore sometimes require duplicated fields
across several documents in order to both query the data and
display them properly in front end. Flask-boiler solves this
problem by decoupling domain model and view model. View model
are generated and refreshed automatically as domain model
changes. This means that you will only have to write business
logics on the domain model without worrying about how the data
will be displayed. This also means that the View Models can
be displayed directly in front end, while supporting
real-time features of Firebase Firestore.

### One-step Configuration
Rather than configuring the network and different certificate
settings for your database and other cloud services. All you
have to do is to enable related services on Google Cloud
Console, and add your certificate. Flask-boiler configures
all the services you need, and expose them as a singleton
Context object across the project.

### Redundancy
Since all View Models are persisted in Firebase Firestore.
Even if your App Instance is offline, the users can still
access a view of the data from Firebase Firestore. Every
View is also a Flask View, so you can also access the data
with auto-generated REST API, in case Firebase Firestore is
not viable.

### Added Safety
By separating business data from documents that are accessible
to the front end, you have more control over which data is
displayed depending on the user's role.

### One-step Documentation
All ViewModels have automatically generated documentations
(provided by Flasgger). This helps AGILE teams keep their
documentations and actual code in sync.

### Fully-extendable
When you need better performance or relational database
support, you can always refactor a specific layer by
adding modules such as `flask-sqlalchemy`.


## Comparisons 

### GraphQL

In GraphQL, the fields are evaluated with each query, but 
flask-boiler evaluates the fields if and only if the 
underlying data source changes. This leads to faster 
read for data that has not changed for a while. Also, 
the data source is expected to be consistent, as the 
field evaluation are triggered after all changes made in 
one transaction to firestore is read. 

GraphQL, however, lets front-end customize the return. You 
must define the exact structure you want to return in flask-boiler. 
This nevertheless has its advantage as most documentations 
of the request and response can be done the same way as REST API. 

### REST API / Flask

REST API does not cache or store the response. When 
a view model is evaluated by flask-boiler, the response 
is stored in firestore forever until update or manual removal. 

Flask-boiler controls role-based access with security rules 
integrated with Firestore. REST API usually controls these 
access with a JWT token. 

### Redux

Redux is implemented mostly in front end. Flask-boiler targets 
back end and is more scalable, since all data are communicated 
with Firestore, a infinitely scalable NoSQL datastore. 

Flask-boiler is declarative, and Redux is imperative. 
The design pattern of REDUX requires you to write functional programming 
in domain models, but flask-boiler favors a different approach: 
ViewModel reads and calculates data from domain models 
and exposes the attribute as a property getter. (When writing 
to DomainModel, the view model changes domain model and 
exposes the operation as a property setter). 
Nevertheless, you can still add function callbacks that are 
triggered after a domain model is updated, but this 
may introduce concurrency issues and is not perfectly supported 
due to the design tradeoff in flask-boiler. 


### Architecture Diagram: 

![Architecture Diagram](https://user-images.githubusercontent.com/24789156/70380617-06e4d100-18f3-11ea-9111-4398ed0e865c.png)

## Contributing
Pull requests are welcome. 

Please make sure to update tests as appropriate.

## License
[MIT](https://choosealicense.com/licenses/mit/)
