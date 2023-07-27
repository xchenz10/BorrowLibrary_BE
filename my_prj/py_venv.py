import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "my_prj.settings")

import django
django.setup()

from my_app.models import Rent, Pupil, Parent, Book
from my_app.serilizers import RentSerializer2

p_id = 54256956
pupil = Pupil.objects.get(personal_id=p_id)
rent = Rent.objects.filter(client=pupil)
rent_instance = rent.first()

rent_instance = rent.first()
rent_data = RentSerializer2(rent_instance).data
rented_books = {f'book_{i}': book_data for i, book_data in rent_data.items()
                if book_data is not None and not i.startswith('start_date')}
