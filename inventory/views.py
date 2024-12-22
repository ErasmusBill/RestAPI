from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes,authentication_classes
from rest_framework.permissions import AllowAny
from rest_framework.authtoken.models import Token
from django.contrib.auth.models import User
from rest_framework import status,generics
from .serializers import *
from rest_framework.views import APIView
from django.shortcuts import render, get_object_or_404
from rest_framework.permissions import IsAuthenticated
from django.utils import timezone
from django.db.models import Sum,Avg,Q
from rest_framework import permissions,authentication
from .permissions import IsSalesPersonOrAdmin


@permission_classes([IsAuthenticated])
@api_view(["POST"])
def login(request):
    data = request.data
    username = data.get("username")
    password = data.get("password")

    if not username or not password:
        return Response({"error": "Username and password are required."}, status=status.HTTP_400_BAD_REQUEST)

    user = User.objects.filter(username=username).first()  
    if not user or not user.check_password(password):  
        return Response({"error": "Invalid credentials"}, status=status.HTTP_401_UNAUTHORIZED)
    
    token, created = Token.objects.get_or_create(user=user)
    serializer = UserSerializer(instance=user)
    
    return Response({"token": token.key, "user": serializer.data}, status=status.HTTP_200_OK)

@permission_classes([AllowAny])
@api_view(["POST", "GET"])
def signup(request):
    try:
        data = request.data
        
        # Check if required fields are present
        required_fields = ['username', 'password']
        for field in required_fields:
            if field not in data:
                return Response(
                    {"error": f"{field} is required"}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
        
        # Check if username already exists
        if User.objects.filter(username=data['username']).exists():
            return Response(
                {"error": "Username already exists"}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Validate and create user
        serializer = UserSerializer(data=data)
        if serializer.is_valid():
            user = serializer.save()
            user.set_password(data["password"])
            user.save()
            
            # Create auth token
            token = Token.objects.create(user=user)
            
            return Response({
                "token": token.key,
                "user": serializer.data
            }, status=status.HTTP_201_CREATED)
        
        return Response(
            serializer.errors, 
            status=status.HTTP_400_BAD_REQUEST
        )
        
    except Exception as e:
        return Response({
            "error": str(e),
            "message": "An unexpected error occurred"
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

# Logout view
@permission_classes([IsAuthenticated])
@api_view(["POST"])
def logout(request):
    """
    Handle user logout by deleting the token.
    """
    try:
        # Delete the user's auth token
        request.user.auth_token.delete()
        return Response({'message': 'Logged out successfully'}, status=status.HTTP_200_OK)
    except AttributeError:
        return Response({'error': 'No token found for this user.'}, status=status.HTTP_400_BAD_REQUEST)
    
    
#add product    
# @permission_classes([IsAuthenticated])
# @api_view(['PATCH'])  
# def change_password(request):
#     if not request.user.is_authenticated:
#         return Response({"error": "Authentication required"}, status=status.HTTP_401_UNAUTHORIZED)

#     serializer = PasswordChangeSerializer(data=request.data)
#     if serializer.is_valid():
#         # Save the new password (the logic would go here to save the password)
#         user = request.user
#         user.set_password(serializer.validated_data['new_password'])
#         user.save()

#         return Response(
#             {"message": "Password changed successfully"},
#             status=status.HTTP_200_OK
#         )
#     return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class ChangePasswordView(generics.UpdateAPIView):
    queryset = User.objects.all()
    serializer_class = PasswordChangeSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user

    def update(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            # Assuming the password is updated through the serializer.save()
            self.get_object().set_password(serializer.validated_data['new_password'])
            self.get_object().save()

            return Response(
                {"message": "Password changed successfully"},
                status=status.HTTP_200_OK
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
# @api_view(["POST"])
# def product_create(request):
#     data = request.data
#     if request.method == "POST":  
#         serializer = ProductSerializer(data=data)
#         if serializer.is_valid():
#             serializer.save()
#             return Response({"message":"Product has being added successfuly"}, status=status.HTTP_201_CREATED)    
#         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)  # Better to return 
    
# class CreateProduct(APIView):
#     def post(self, request, *args, **kwargs):
#         serializer = ProductSerializer(data=request.data)
#         if serializer.is_valid():
#             serializer.save()
#             return Response(serializer.data, status=status.HTTP_201_CREATED)
#         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            


class ProductCreateView(generics.CreateAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer  
    authentication_classes = [authentication.TokenAuthentication]
    permission_classes = [permissions.IsAdminUser,IsAuthenticated]
    
    def perform_create(self, serializer):
        serializer.save()
    
    
#Retrieving all product from the database
# @api_view(["GET"])
# def product(request):
#     products = Product.objects.all()
#     serializer = ProductSerializer(products, many=True)  
#     return Response(serializer.data) 

# class product(APIView):
#     def get(self, request, pk, *args, **kwargs):
#         products = Product.objects.all()
#         serialer = ProductSerializer(products,many=True).data
#         return Response(serialer)
        
class ProductListView(generics.ListAPIView):
    permission_classes = [IsAuthenticated] 
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    
    
#Retriving a particular product
# @api_view(["GET"])
# def productDetail(request,pk):
#     product = get_object_or_404(Product, pk=pk)  
#     serializer = ProductSerializer(product,many=False)
#     return Response(serializer)  

# class productDetail(APIView):
#     def get(self, request, pk=None, *args, **kwargs):
#         product = get_object_or_404(product,pk=pk)
#         serializer = ProductSerializer(product,many=False).data
#         return Response(serializer)
    
class ProductDetailView(generics.RetrieveAPIView):
    permission_classes = [IsAuthenticated] 
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    
#Updating Product    
    
# @api_view(["PUT"])
# def productUpdate(request,pk):
#     data = request.data
#     product = get_object_or_404(Product,pk=pk)
#     serializer = ProductSerializer(instance=product).data
#     if serializer.is_valid():
#         serializer.save() 
#         return Response({"message": "Product successfully updated"},status=status.HTTP_200_OK) 
#     else:
#         return Response({"error":"An error occured when updating the product, please try again later..."},status=status.HTTP_400_BAD_REQUEST) 
    
# class productUpdate(APIView):
#     def post(self, request, pk=None, *args, **kwargs):
#         product = get_object_or_404(Product,pk=pk)
#         serializer = ProductSerializer(instance=product).data
#         if serializer.is_valid():
#             serializer.save()
#             return Response({"message": "Product successfully updated"},status=status.HTTP_200_OK)
#         else:
#             return Response({"error":"An error occured when updating the product, please try again later..."},status=status.HTTP_400_BAD_REQUEST)  
        
class ProductUpdateView(generics.UpdateAPIView):
    permission_classes = [IsAuthenticated] 
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    authentication_classes = [authentication.TokenAuthentication]
    permission_classes = [permissions.IsAdminUser]
    lookup_field = "pk"
    
    def perform_update(self, serializer):
        return super().perform_update(serializer)
    
#Destorying or deleting products
# @api_view(["DELETE"])
# def delete_product(request,pk=None):
#     product = get_object_or_404(Product,pk=pk)
#     product.delete()
  
#     return Response(
#         {"success": "Product has been deleted successfully"},
#         status=status.HTTP_204_NO_CONTENT
#     )   
    
# class DeleteProduct(APIView):
#     def delete(self, request, pk=None, *args, **kwargs):
#         product = get_object_or_404(Product,pk=pk)
#         product.delete()
#         return Response(
#         {"success": "Product has been deleted successfully"},
#         status=status.HTTP_204_NO_CONTENT
#     )   

class ProductDeleteView(generics.DestroyAPIView):
    authentication_classes = [authentication.TokenAuthentication]
    permission_classes = [permissions.IsAdminUser]
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    lookup_field = "pk"
    
    def perform_destroy(self, instance):
        super().perform_destroy(instance)
            

class SalesAnalyticsView(APIView):
    """View for sales analytics"""
    permission_classes = [IsSalesPersonOrAdmin]
    authentication_classes = [authentication.TokenAuthentication]
    
    def get(self, request):
        """Get daily sales analytics by product"""
        today = timezone.now().date()
        daily_sales = Sale.objects.filter(
            date__date=today
        ).values(
            'product__id',
            'product__product_name'
        ).annotate(
            total_quantity=Sum('quantity_sold'),
            total_revenue=Sum('total_sale'),
            average_price=Avg('unit_price')
        ).order_by('-total_revenue')

        return Response({
            'date': today,
            'sales': daily_sales
        })
        
        
#implementing search tonight  

@api_view(["GET"])
@authentication_classes([authentication.TokenAuthentication])
@permission_classes([permissions.IsAuthenticatedOrReadOnly])
def search(request):
    if request.method == "GET":
        searched = request.GET.get("searched")
        
        if searched:
            queryset = Product.objects.filter(
                Q(name__icontains=searched) | Q(description__icontains=searched)
            )
            
            serializer = ProductSerializer(queryset, many=True)
            return Response({
                "count": queryset.count(),
                "results": serializer.data
            }, status=status.HTTP_200_OK)
        else:
        
            queryset = Product.objects.all()
            serializer = ProductSerializer(queryset, many=True)
            return Response({
                "count": queryset.count(),
                "results": serializer.data
            }, status=status.HTTP_200_OK)


    

    
        
        
    
    
    
    