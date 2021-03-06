from django.shortcuts import render, get_object_or_404, redirect
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.http import HttpResponse, HttpResponseRedirect, Http404
from .models import Post
from .forms import PostForm
from django.db.models import Q
from django.contrib import messages
from urllib import quote_plus
from django.utils import timezone
# Create your views here.


def post_create(request):
	if request.user.is_staff or request.user.is_superuser:
		form = PostForm(request.POST or None, request.FILES or None)
		if form.is_valid():
			instance = form.save(commit=False)
			instance.user = request.user
			instance.save()
			messages.success(request, "Successfully Created")
			return HttpResponseRedirect(instance.get_absolute_url())
		context = {
			"form": form,
		}
		return render(request, "post_form.html", context)
	else:
		raise Http404


def post_detail(request, slug=None):
	instance = get_object_or_404(Post, slug=slug)
	share_string = quote_plus(instance.content)
	context = {
		"title": instance.title,
		"instance": instance,
		"share_string": share_string,
	}
	return render(request, "post_detail.html", context)

def post_list(request):
	queryset_list = Post.objects.filter(publish__lte=timezone.now())
	query = request.GET.get("q")
	if query:
		queryset_list = queryset_list.filter(
			Q(title__icontains=query)|
			Q(content__icontains=query)|
			Q(user__first_name__icontains=query)|
			Q(user__last_name__icontains=query)
			).distinct()
	paginator = Paginator(queryset_list, 10) # Show 25 contacts per page
	page_request_var = "page"
	page = request.GET.get(page_request_var)
	try:
		queryset = paginator.page(page)
	except PageNotAnInteger:
		# If page is not an integer, deliver first page.
		queryset = paginator.page(1)
	except EmptyPage:
		# If page is out of range (e.g. 9999), deliver last page of results.
		queryset = paginator.page(paginator.num_pages)

	context = {
		"object_list": queryset,
		"title": "List",
		"page_request_var": page_request_var
	}
	return render(request, "post_list.html", context)

def post_update(request, slug=None):
	if request.user.is_staff or request.user.is_superuser:
		instance = get_object_or_404(Post, slug=slug)
		form = PostForm(request.POST or None, request.FILES or None, instance=instance)
		if form.is_valid():
			instance = form.save(commit=False)
			instance.save()
			messages.success(request, "Saved")
			return HttpResponseRedirect(instance.get_absolute_url())

		context = {
			"title": instance.title,
			"instance": instance,
			"form": form,
		}

		return render(request, "post_form.html", context)
	else:
		return Http404

def post_delete(request, slug=None):
	if request.user.is_staff or request.user.is_superuser:

		instance = get_object_or_404(Post, slug=slug)
		instance.delete()
		messages.success(request, "Successfully Deleted")
		return redirect("posts:list")
	else:
		return Http404