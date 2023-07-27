from rest_framework.response import Response
from rest_framework.authtoken.admin import User, Token
from rest_framework.authentication import TokenAuthentication
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from .models import Parent, Pupil, Book, Rent
from .serilizers import ParentSerializer, PupilSerializer, RentSerializer, BookSerializer, UserSerializer, \
    RentSerializer2, UserSerializer2
from django.contrib.auth.models import User
from django.contrib.auth.hashers import make_password
from django.utils import timezone
from django.core.mail import EmailMultiAlternatives
from django.views.decorators.cache import cache_page
from django.core.exceptions import ObjectDoesNotExist


@api_view(['GET'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def check_token(req):
    """This function check the TokenAuthentication of the token send
     by the user and returns the first name of the current user."""

    return Response({'user': req.user.first_name, 'is': req.user.is_superuser}, 200)


@api_view(['GET', 'POST'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def home(request):
    """This function check the TokenAuthentication of the token send
     by the user and returns every single pupil under the current user."""

    if not request.user.is_authenticated:
        return Response({'message': 'Authentication required.'}, status=400)

    parent_id = request.user

    pupils = Pupil.objects.filter(parent__parent_id=parent_id)
    serializer = PupilSerializer(pupils, many=True)

    return Response(serializer.data, status=200)


@api_view(["POST"])
def signup(request):
    """Creates a new user (parent) with the provided information
     and generates an authentication token for the user."""
    if request.method == 'POST':
        parent_id = request.data.get('parent_id')
        password = request.data.get('password')
        confirm_password = request.data.get('confirm_password')
        first_name = request.data.get('first_name')
        last_name = request.data.get('last_name')
        email = request.data.get('email')
        address = request.data.get('address')

        if password != confirm_password:
            return Response({'message': 'סיסמאות לא תואמות'}, status=400)
        if not parent_id.isdigit():
            return Response({'message': 'על ת.ז להכיל רק מספרים'}, status=400)

        try:
            Parent.objects.get(parent_id=parent_id)
            return Response({'message': 'תלמיד עם ת.ז זו כבר קיים במערכת'}, status=400)
        except Parent.DoesNotExist:
            hashed_password = make_password(password)
            user = User.objects.create(username=parent_id, password=hashed_password,
                                       first_name=first_name, last_name=last_name, email=email)
            token = Token.objects.create(user=user)
            Parent.objects.create(parent_id=parent_id, address=address, user=user)
            return Response({'message': 'User created successfully', 'token': token.key}, status=200)
    else:
        return Response({'message': 'Invalid request'}, status=400)


@api_view(['POST'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def create_pupil(request):
    """Creates a new pupil associated with the authenticated parent user."""

    if request.method == 'POST':

        parent_id = request.user
        personal_id = request.data.get('personal_id')
        full_name = request.data.get('full_name')
        grade = request.data.get('grade')

        try:
            parent = Parent.objects.get(parent_id=parent_id)
        except Parent.DoesNotExist as e:
            return Response({'msg': f'{e}'}, status=400)

        if not personal_id or not full_name or not grade:
            return Response({'msg': 'אנא מלא את כל הפרטים'}, status=400)

        if Pupil.objects.filter(personal_id=personal_id).exists():
            return Response({'msg': 'תלמיד עם ת.ז זו כבר קיים במערכת'}, status=400)

        try:
            pupil = Pupil.objects.create(personal_id=personal_id, full_name=full_name, grade=grade, parent=parent)
            return Response({'msg': 'Pupil created successfully', 'pupil_id': pupil.id}, status=200)
        except Exception as e:
            return Response({'msg': f'הודעת תקלה המיועדת לאדמין: {e}'}, status=400)


@api_view(['GET'])
def has_rent(request):
    """Checks if a pupil has any active rents
     and returns the rent data if found."""

    pupil_id = request.query_params.get('p_id')
    if pupil_id is not None:
        try:
            pupil = Pupil.objects.get(personal_id=pupil_id)
            rent = Rent.objects.filter(client=pupil)

            if rent.exists():
                rs = RentSerializer(rent, many=True)
                return Response({'msg': True, 'data': rs.data}, status=200)
            else:
                return Response({'msg': False, 'data': []}, status=200)
        except Pupil.DoesNotExist:
            return Response({'msg': 'Pupil not found'}, status=400)
    else:
        return Response({'msg': 'Missing pupil ID'}, status=400)


@api_view(['GET'])
def books_for_rent(request):
    """Retrieves books based on the provided pupil ID and grade."""

    pupil_id = request.query_params.get('p_id')
    pupil_grade = request.query_params.get('p_grade')
    p_name = request.query_params.get('p_name')
    try:
        p = Pupil.objects.get(personal_id=pupil_id)
        if pupil_grade == p.grade:
            books = Book.objects.filter(book_grade=pupil_grade)
            bs = BookSerializer(books, many=True)
            return Response({'data': bs.data}, status=200)
        else:
            return Response({'msg': 'Pupil grade does not match'}, status=400)
    except ObjectDoesNotExist:
        return Response({'msg': 'Pupil not found'}, status=404)
    except Exception as e:
        return Response({'msg': str(e)}, status=400)


@api_view(['POST'])
def mk_rent(request):
    """Creates a new rent for a pupil and associates books with the rent."""

    pupil_id = request.query_params.get('p_id')
    if not pupil_id:
        return Response({'msg': 'Please provide the pupil ID'}, status=400)

    try:
        pupil = Pupil.objects.get(personal_id=pupil_id)
        grade = pupil.grade
        books = Book.objects.filter(book_grade=grade)

        if not books.exists():
            return Response({'msg': 'No books found for the pupil\'s grade'}, status=400)

        start_date = timezone.now()
        end_date = timezone.make_aware(timezone.datetime(2024, 6, 17))

        r = Rent.objects.create(client=pupil, start_date=start_date, end_date=end_date)

        for i, book in enumerate(books[:17]):
            setattr(r, f'book_{i + 1}', book)
            book.storage -= 1
            book.save()

        r.save()
        rs = RentSerializer(r)
        return Response(rs.data, status=200)
    except Pupil.DoesNotExist:
        return Response({'msg': 'Pupil not found'}, status=400)
    except Exception as e:
        return Response({'msg': str(e)}, status=400)


@api_view(['GET', 'POST'])
def send_email(request):
    """ Sends an email to the parent associated with a pupil,
     containing a message and information about the rented books."""

    pupil_id = request.query_params.get('p_id')
    pupil = Pupil.objects.get(personal_id=pupil_id)
    user_parent = pupil.parent.user
    user_serializer = UserSerializer(user_parent)
    user = user_serializer.data
    user_email = user['email']
    if request.method == 'POST':
        try:
            subject = f"אישור הזמנה על שם התלמיד - {pupil.full_name}"
            message = request.data.get('message')
            html_content = f"<div style={{direction: 'rtl}}> להלן הספרים שהוזמנו<br/>" \
                           f"{message}.</div>"
            from_email = 'setting.EMAIL_HOST_USER'
            to = user_email
            msg = EmailMultiAlternatives(subject, html_content, from_email, [to])
            msg.attach_alternative(html_content, "text/html")
            msg.send()
            return Response('email sent successfully', status=200)
        except Exception as e:
            return Response(f'ERROR: {e}', status=400)


@api_view(['GET', 'PUT'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def edit_profile(request):
    """Updates the profile information of the authenticated
     user (parent) and associated parent address."""

    if request.method == 'GET':
        username = request.user
        user = User.objects.get(username=username)
        parent = Parent.objects.get(parent_id=username)
        parent_serializer = ParentSerializer(parent)
        user_serializer = UserSerializer2(user)
        data = {
            'user': user_serializer.data,
            'parent': parent_serializer.data,
        }
        return Response(data)

    if request.method == 'PUT':
        user = request.user
        user.first_name = request.data.get('first_name')
        user.last_name = request.data.get('last_name')
        user.email = request.data.get('email')

        try:
            parent_id = request.user
            parent = Parent.objects.get(parent_id=parent_id)
            new_address = request.data.get('address')
            parent.address = new_address
            parent.save()
        except Parent.DoesNotExist:
            return Response({'message': 'Parent profile does not exist.'}, status=400)

        user.save()
        return Response({'message': 'User profile and parent address updated successfully.'}, status=200)

    return Response({'message': 'Invalid request method.'}, status=400)


@cache_page(60 * 60 * 24)
@api_view(['GET'])
def book_value(request):
    if request.method == 'GET':
        try:
            books = Book.objects.filter(value__range=(2, 100)).order_by('book_grade')
            bs = BookSerializer(books, many=True)
            return Response({'msg': 'OK', 'data': bs.data}, status=200)
        except Exception as e:
            return Response({'msg': 'ERROR', 'data': e}, status=400)
    else:
        return Response({'msg': 'ERROR'}, status=400)


@api_view(['GET', 'POST', 'PUT', 'DELETE'])
def dash_books(request):
    """Dashboard for admin to track after the books storage"""

    if request.method == 'GET':
        all_books = Book.objects.order_by('book_grade')
        bs = BookSerializer(all_books, many=True)
        return Response({'data': bs.data}, status=200)

    if request.method == 'POST':
        book_id = request.data.get('book_id')
        book_name = request.data.get('book_name')
        book_grade = request.data.get('book_grade')
        book_value = request.data.get('book_value', None)
        book_storage = request.data.get('book_storage', None)

        if book_id and book_name and book_grade:
            existing_book = Book.objects.filter(book_id=book_id).first()
            if existing_book:
                return Response({'msg': 'ספר זה עם מספר פריט זה כבר קיים במערכת'}, status=400)
            try:
                book = Book.objects.create(book_id=book_id, book_name=book_name, book_grade=book_grade,
                                           value=book_value, storage=book_storage)
                bs = BookSerializer(book).data
                return Response({'msg': 'Book Created Successfully', 'data': bs}, status=200)
            except Exception as e:
                return Response({'msg': f'ERRor{e}'}, status=400)
        else:
            return Response('מספר פריט, שם הספר וכיתה הם שדות חובה.', status=400)

    if request.method == 'PUT':
        book_id = request.data.get('book_id')
        book_name = request.data.get('book_name')
        book_grade = request.data.get('book_grade')
        book_value = request.data.get('book_value')
        book_storage = request.data.get('book_storage')

        try:
            book = Book.objects.get(book_id=book_id)
            book.book_name = book_name
            book.book_grade = book_grade
            book.value = book_value
            book.storage = book_storage
            book.save()

            bs = BookSerializer(book).data
            return Response({'msg': 'Book Updated Successfully', 'data': bs}, status=200)
        except Exception as e:
            return Response({'msg': f'Error: {str(e)}'}, status=400)

    if request.method == 'DELETE':
        book_id = request.data.get('book_id')

        try:
            book = Book.objects.get(book_id=book_id)
            book.delete()
            return Response({'msg': 'Book Deleted Successfully'}, status=200)
        except Book.DoesNotExist:
            return Response({'msg': 'Book does not exist'}, status=400)
        except Exception as e:
            return Response({'msg': f'Error: {str(e)}'}, status=400)


@api_view(['GET', 'DELETE'])
def dash_rents(request):
    """Dashboard for admin to track after the rents"""

    if request.method == 'GET':
        all_rents = Rent.objects.all().select_related('client')
        rs = RentSerializer(all_rents, many=True)
        return Response({'data': rs.data}, status=200)


@api_view(['GET', 'PUT', 'DELETE'])
def dash_client_rent(request):
    if request.method == 'GET':
        p_id = request.query_params.get('p_id')
        try:
            pupil = Pupil.objects.get(personal_id=p_id)
            rent = Rent.objects.filter(client=pupil)
            if not rent.exists():
                return Response({'msg': 'No rent found for the pupil'}, status=400)

            rent_instance = rent.first()
            rent_data = RentSerializer2(rent_instance).data
            rented_books = {f'book_{i}': book_data for i, book_data in rent_data.items()
                            if book_data is not None and not i.startswith('start_date')}
            return Response({'msg': rented_books}, status=200)
        except Pupil.DoesNotExist:
            return Response({'msg': 'Pupil not found'}, status=400)

    elif request.method == 'PUT':

        p_id = request.query_params.get('p_id')
        try:
            pupil = Pupil.objects.get(personal_id=p_id)
        except Pupil.DoesNotExist:
            return Response({'msg': 'Pupil not found'}, status=400)
        rent = Rent.objects.filter(client=pupil)

        if not rent.exists():
            return Response({'msg': 'No rent found for the pupil'}, status=400)

        rent_instance = rent.first()
        selected_books = request.data.get('books', [])

        for i in range(1, 18):
            book_attr_name = f'book_{i}'
            related_book = getattr(rent_instance, book_attr_name)

            if related_book and related_book.book_id in [book.get('book_id') for book in selected_books]:
                setattr(rent_instance, book_attr_name, None)

        rent_instance.save()

        serializer = RentSerializer2(rent_instance)
        return Response(serializer.data, status=200)

    # elif request.method == 'PUT':
    #
    #     p_id = request.query_params.get('p_id')
    #     pupil = Pupil.objects.get(personal_id=p_id)
    #     rent = Rent.objects.filter(client=pupil)
    #     rent_instance = rent.first()
    #     rent_data = RentSerializer2(rent_instance).data
    #     rented_books = {f'book_{i}': book_data for i, book_data in rent_data.items()
    #                     if book_data is not None and not i.startswith('start_date')}
    #     pass


@api_view(['GET'])
def check_superuser(request):
    """Checks if the user is superuser"""

    user = User.objects.get(username=28065555)
    user_data = UserSerializer(user)
    if user.is_superuser:
        return Response(user_data.data, status=200)
    else:
        return Response(user_data.data)


@api_view(['POST'])
def contact_msg(request):
    """Contact msg from client to the school"""

    p_id = request.data.get('p_id')

    if not p_id:
        return Response({'msg': 'אנא מלא ת.ז'}, status=400)
    if not p_id.isdigit():
        return Response({'msg': 'על ת.ז להכיל רק מספרים'}, status=400)

    parent = Parent.objects.get(parent_id=p_id)
    p_name = parent.user.first_name
    c_msg = request.data.get('c_msg')
    if len(c_msg) == 0:
        return Response({'msg': 'תאר/י בפנינו את בעייתך'}, status=400)
    if request.method == 'POST':
        try:
            subject = f"טופס יצירת התקבל על ידי:{p_name}, תעודת זהות:{parent.parent_id}"
            message = c_msg
            html_content = f"<div style={{direction: 'rtl}}>{message}<br/></div>"
            from_email = 'setting.EMAIL_HOST_USER'
            to = 'chenschoolproject@gmail.com'
            msg = EmailMultiAlternatives(subject, html_content, from_email, [to])
            msg.attach_alternative(html_content, "text/html")
            msg.send()
            return Response({'msg': 'email sent successfully'}, status=200)
        except Exception as e:
            return Response({f'msg': {e}}, status=400)
