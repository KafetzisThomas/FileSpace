from django.shortcuts import render, redirect, get_object_or_404
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

@login_required
def delete_file(request, pk):
    file = get_object_or_404(File, pk=pk, owner=request.user)
    file.file.delete()  # delete actual file from storage
    file.delete()  # delete db record
    return redirect("files:drive")
