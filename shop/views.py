from django.shortcuts import render
from .models import*
from django.contrib import messages
from django.shortcuts import redirect
from django.http import HttpResponse
from django.http import JsonResponse
from shop.form import CustomerUserForm
from django.contrib.auth import authenticate,login,logout
import json

def home(request):
    product = Product.objects.filter(trending=1)
    return render(request,"shop/index.html",{'productss':product})

def cart_page(request):
    if request.user.is_authenticated:
        cart=Cart.objects.filter(user=request.user)
        return render(request,"shop/cart.html",{'cart':cart})
    else:
        return redirect('home')
        

def remove_cart(request,cid):
    cartitem=Cart.objects.get(id=cid)
    cartitem.delete()
    return redirect('cart')

def fav_page(request):
   if request.headers.get('x-requested-with')=='XMLHttpRequest':
    if request.user.is_authenticated:
      data=json.load(request)
      product_id=data['pid']
      product_status=Product.objects.get(id=product_id)
      if product_status:
         if Favourite.objects.filter(user=request.user.id,product_id=product_id):
          return JsonResponse({'status':'Product Already in Favourite'}, status=200)
         else:
          Favourite.objects.create(user=request.user,product_id=product_id)
          return JsonResponse({'status':'Product Added to Favourite'}, status=200)
    else:
      return JsonResponse({'status':'Login to Add Favourite'}, status=200)
   else:
    return JsonResponse({'status':'Invalid Access'}, status=200)

def favviewpage(request):
    if request.user.is_authenticated:
        fav=Favourite.objects.filter(user=request.user)
        return render(request,"shop/fav.html",{'fav':fav})
    else:
        return redirect('home')
    
def remove_fav(request,fid):
    item=Favourite.objects.get(id=fid)
    item.delete()
    return redirect('favviewpage')
    
 
def add_to_cart(request):
   if request.headers.get('x-requested-with')=='XMLHttpRequest':
    if request.user.is_authenticated:
      data=json.load(request)
      product_qty=data['product_qty']
      product_id=data['pid']
      #print(request.user.id)
      product_status=Product.objects.get(id=product_id)
      if product_status:
        if Cart.objects.filter(user=request.user.id,product_id=product_id):
          return JsonResponse({'status':'Product Already in Cart'}, status=200)
        else:
          if product_status.quantity>=product_qty:
            Cart.objects.create(user=request.user,product_id=product_id,product_qty=product_qty)
            return JsonResponse({'status':'Product Added to Cart'}, status=200)
          else:
            return JsonResponse({'status':'Product Stock Not Available'}, status=200)
    else:
      return JsonResponse({'status':'Login to Add Cart'}, status=200)
   else:
    return JsonResponse({'status':'Invalid Access'}, status=200)
 
def logout_page(request):
    if request.user.is_authenticated:
        logout(request)
        messages.success(request,"Logged Out Successfully")
    return redirect('home')

def login_page(request):
    if request.user.is_authenticated:
        return redirect('home')
    else:
        if request.method=='POST':
            name=request.POST.get('username')
            pwd=request.POST.get('password')
            user=authenticate(request,username=name,password=pwd)
            if user is not None:
                login(request,user)
                messages.success(request,"logged in Successfully")
                return redirect('home')
            else:
                messages.error(request,"Invalid User Name Or Password")
                return redirect('login')
        return render(request,"shop/login.html")

        

def register(request):
    form=CustomerUserForm()
    if request.method=='POST':
        form=CustomerUserForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request,"Successfully Registerd Now You Can Login....")
            return redirect('login')
    return render(request,"shop/register.html",{'form':form})
        
        

def collections(request):
    catagory = Catagory.objects.filter(status=0)
    return render(request,"shop/collections.html",{'catagory':catagory})

def collectionsview(request,name):
    if(Catagory.objects.filter(name=name,status=0)):
        product=Product.objects.filter(catagory__name=name)
        return render(request,"shop/products/index.html",{'product':product,'catagory_name':name})
    else:
        messages.warning(request,"No Such Catagory Found")
        return redirect('collections')
    
def product_details(request,cname,pname):
    if(Catagory.objects.filter(name=cname,status=0)):
        if(Product.objects.filter(name=pname,status=0)):
            products=Product.objects.filter(name=pname,status=0).first()
            return render(request,"shop/products/product_details.html",{'products':products})
        else:
            messages.error(request,"No Such Product Found")
            return redirect('collections')       
    else:
        messages.error(request,"No Such Catagory Found")
        return redirect('collections')
