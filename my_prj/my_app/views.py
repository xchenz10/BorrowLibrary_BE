from django.contrib.auth.hashers import make_password
from django.contrib.auth.models import User
from rest_framework.authentication import TokenAuthentication
from rest_framework.authtoken.admin import User, Token
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from .models import Parent, Pupil, Book, Rent
from .serilizers import ParentSerializer, PupilSerializer, RentSerializer, BookSerializer
from django.utils import timezone


@api_view(['GET'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def check_token(req):
    return Response({'user': {req.user.first_name}}, 200)


@api_view(['GET', 'POST'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def home(request):
    if not request.user.is_authenticated:
        return Response({'message': 'Authentication required.'}, status=400)

    parent_id = request.user

    pupils = Pupil.objects.filter(parent__parent_id=parent_id)
    serializer = PupilSerializer(pupils, many=True)

    return Response(serializer.data, status=200)


@api_view(["POST"])
def signup(request):
    if request.method == 'POST':
        parent_id = request.data.get('parent_id')
        password = request.data.get('password')
        confirm_password = request.data.get('confirm_password')
        first_name = request.data.get('first_name')
        last_name = request.data.get('last_name')
        email = request.data.get('email')
        address = request.data.get('address')

        if password != confirm_password:
            return Response({'message': 'Passwords do not match'}, status=400)
        if not parent_id.isdigit():
            return Response({'message': 'ID must be a number'}, status=400)

        try:
            Parent.objects.get(parent_id=parent_id)
            return Response({'message': 'User with this ID already exists'}, status=400)
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
    pupil_id = request.query_params.get('p_id')
    if pupil_id is not None:
        try:
            pupil = Pupil.objects.get(personal_id=pupil_id)
            rent = Rent.objects.filter(client=pupil)

            if rent.exists():
                rs = RentSerializer(rent, many=True)
                return Response({'msg': rs.data}, status=200)
            else:
                return Response({'msg': 'No rent found'}, status=400)
        except Pupil.DoesNotExist:
            return Response({'msg': 'Pupil not found'}, status=400)
    else:
        return Response({'msg': 'Missing pupil ID'}, status=400)


@api_view(['GET', 'POST'])
def books(request):
    if request.method == 'GET':
        pupil_id = request.query_params.get('p_id')
        pupil_grade = request.query_params.get('p_grade')
        full_name = request.query_params.get('p_name')

        if pupil_id is not None and pupil_grade is not None:
            try:
                books = Book.objects.filter(book_grade=pupil_grade)
                bs = BookSerializer(books, many=True)
                return Response(bs.data, status=200)
            except Pupil.DoesNotExist:
                return Response({'msg': 'Pupil not found'}, status=404)


@api_view(['POST'])
def mk_rent(request):
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
        end_date = start_date + timezone.timedelta(days=365)

        r = Rent.objects.create(client=pupil, start_date=start_date, end_date=end_date)

        for i, book in enumerate(books[:17]):
            setattr(r, f'book_{i + 1}', book)

        r.save()

        rs = RentSerializer(r)
        return Response(rs.data, status=200)
    except Pupil.DoesNotExist:
        return Response({'msg': rs.errors}, status=400)
    except Exception as e:
        return Response({'msg': str(e)}, status=400)


@api_view(['PUT'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def edit_profile(request):
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




# # פונקציה המתופעלת ע"י בחירת הספרים בצ'קבוקס.
# @api_view(['GET', 'POST'])
# def books(request):
#     if request.method == 'GET':
#         pupil_id = request.query_params.get('p_id')
#         pupil_grade = request.query_params.get('p_grade')
#
#         if pupil_id is not None and pupil_grade is not None:
#             try:
#                 books = Book.objects.filter(book_grade=pupil_grade)
#                 bs = BookSerializer(books, many=True)
#                 return Response(bs.data, status=200)
#             except Pupil.DoesNotExist:
#                 return Response({'msg': 'Pupil not found'}, status=404)
#
#     elif request.method == 'POST':
#         pupil_id = request.data.get('p_id')
#         book_1 = request.data.get('book_1')
#         book_2 = request.data.get('book_2', None)
#         book_3 = request.data.get('book_3', None)
#         book_4 = request.data.get('book_4', None)
#         book_5 = request.data.get('book_5', None)
#         book_6 = request.data.get('book_6', None)
#         book_7 = request.data.get('book_7', None)
#         book_8 = request.data.get('book_8', None)
#         book_9 = request.data.get('book_9', None)
#         book_10 = request.data.get('book_10', None)
#         book_11 = request.data.get('book_11', None)
#         book_12 = request.data.get('book_12', None)
#         book_13 = request.data.get('book_13', None)
#         book_14 = request.data.get('book_14', None)
#         book_15 = request.data.get('book_15', None)
#         book_16 = request.data.get('book_16', None)
#         book_17 = request.data.get('book_17', None)
#
#         if pupil_id is not None and book_1 is not None:
#             try:
#                 pupil = Pupil.objects.get(personal_id=pupil_id)
#                 start_date = timezone.now()
#                 end_date = start_date + timezone.timedelta(days=365)
#                 rent = Rent.objects.create(client=pupil, start_date=start_date, end_date=end_date,
#                                            book_1=book_1, book_2=book_2, book_3=book_3, book_4=book_4,
#                                            book_5=book_5, book_6=book_6, book_7=book_7, book_8=book_8,
#                                            book_9=book_9, book_10=book_10, book_11=book_11, book_12=book_12,
#                                            book_13=book_13, book_14=book_14, book_15=book_15,book_16=book_16,
#                                            book_17=book_17)
#                 rent.save()
#                 return Response({'msg': 'Rent submitted successfully'}, status=200)
#             except Pupil.DoesNotExist:
#                 return Response({'msg': 'Pupil not found'}, status=404)
#             except Book.DoesNotExist:
#                 return Response({'msg': 'One or more selected books not found'}, status=400)
#     return Response({'msg': 'Invalid request'}, status=400)

