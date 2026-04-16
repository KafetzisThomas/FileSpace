from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import FileResponse, Http404
from .models import File

@login_required
def drive(request):
    files = File.objects.filter(owner=request.user).order_by("-uploaded_at")
    return render(request, "files/drive.html", {"files": files})

@login_required
def upload_files(request):
    if request.method == "POST":
        files = request.FILES.getlist('file_field')
        for file in files:
            File.objects.create(file=file, name=file.name, full_path=file.name, size=file.size, owner=request.user)
        return redirect("files:drive")
    return render(request, "files/new_files.html")

@login_required
def upload_dir(request):
    if request.method == "POST":
        files = request.FILES.getlist('file_field')
        paths = request.POST.getlist('paths')

        # webkitdirectory: map files to their paths and save
        for uploaded_file, relative_path in zip(files, paths):
            File.objects.create(file=uploaded_file, name=uploaded_file.name, full_path=relative_path, size=uploaded_file.size, owner=request.user)
        return redirect("files:drive")
    return render(request, "files/new_dir.html")

@login_required
def download(request, pk):
    file = File.objects.get(pk=pk, owner=request.user)
    if not file.file:
        raise Http404()

    response = FileResponse(file.file.open(), as_attachment=True)
    response["Content-Disposition"] = f'attachment; filename="{file.name}"'
    return response

@login_required
def delete(request, pk):
    file = get_object_or_404(File, pk=pk, owner=request.user)
    file.file.delete()  # delete actual file from storage
    file.delete()  # delete db record
    return redirect("files:drive")
