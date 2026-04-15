from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .models import File
from .forms import FileForm

@login_required
def drive(request):
    files = File.objects.filter(owner=request.user).order_by("-uploaded_at")
    return render(request, "files/drive.html", {"files": files})

@login_required
def new_file(request):
    if request.method == "POST":
        form = FileForm(request.POST, request.FILES)
        if form.is_valid():
            file = form.save(commit=False)
            file.owner = request.user
            file.save()
            return redirect("files:drive")
    else:
        form = FileForm()

    return render(request, "files/new_file.html", {"form": form})
