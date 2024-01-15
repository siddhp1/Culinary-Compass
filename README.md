final project

notes for now:

pages that are done
- layout
- account
- login
- register
- reset request
- reset token
- add rest
- my rest 

pages that need to be worked on
- home (just add images and adjust sizing)
- find rest (finalize styles)

NEED TO COMMENT ALL HTML

stuff to do
- check that dietary restriction form is loading from db
- Enter button functionality on add restaurant page
- See if top features can be used for non-category search (then add two buttons (cusine search and feature search))

<!-- {% for restaurant_rec in restaurant_recs.items %}
            <div class="card mt-3">
                <div class="card-body">
                <div class="row">
                    <div class="col-md-6">
                        {% if restaurant_rec.restaurant.website %}
                            <h2 class="card-title"><a href="{{ restaurant_rec.restaurant.website }}">{{ restaurant_rec.restaurant.name }}</a></h2>
                        {% else %}
                            <h2 class="card-title">{{ restaurant_rec.restaurant.name }}</h2>
                        {% endif %}
                        <p>{{ restaurant_rec.restaurant.address }}</p>
                    </div>
                    <div class="col-md-6">
                        <p><strong>Categories: </strong>
                            {% for category in restaurant_rec.restaurant.category.split(',') %}
                                {{ category.split(':')[0] }}{% if not loop.last %}, {% endif %}
                            {% endfor %}
                        </p>
                    </div>
                </div>
                </div>
            </div>
        {% endfor %} -->
