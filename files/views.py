from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.decorators.http import require_POST
from django.http import FileResponse, Http404
from .models import Folder, File

@login_required
def drive(request, folder_id=None):
    search = request.GET.get("search")
    current_folder = get_object_or_404(Folder, id=folder_id, owner=request.user) if folder_id else None

    # get subfolders and files
    folders = Folder.objects.filter(owner=request.user, parent=current_folder).order_by("name")
    files = File.objects.filter(owner=request.user, folder=current_folder).order_by("name")

    if search:
        folders = Folder.objects.filter(owner=request.user, name__icontains=search).order_by("name")
        files = File.objects.filter(owner=request.user, name__icontains=search).order_by("name")

    return render(request, "files/drive.html", {
        "current_folder": current_folder,
        "folders": folders,
        "files": files,
        "search": search,
    })

@login_required
@require_POST
def upload_files(request):
    files = request.FILES.getlist('file_field')
    folder_id = request.POST.get('folder_id')
    target_folder = Folder.objects.filter(id=folder_id, owner=request.user).first() if folder_id else None

    for file in files:
        File.objects.create(file=file, name=file.name, folder=target_folder, size=file.size, owner=request.user)

    messages.success(request, "File uploaded successfully.")
    return redirect("files:drive_folder", folder_id=target_folder.id) if target_folder else redirect("files:drive")    

@login_required
@require_POST
def upload_folder(request):
    files = request.FILES.getlist('file_field')
    paths = request.POST.getlist('paths')
    folder_id = request.POST.get('folder_id')
    root_folder = Folder.objects.filter(id=folder_id, owner=request.user).first() if folder_id else None

    for uploaded_file, relative_path in zip(files, paths):
        parts = relative_path.split('/')
        current_parent = root_folder

        for folder_name in parts[:-1]:
            current_parent, _ = Folder.objects.get_or_create(name=folder_name, parent=current_parent, owner=request.user)

        File.objects.create(file=uploaded_file, name=uploaded_file.name, folder=current_parent, size=uploaded_file.size, owner=request.user)

    messages.success(request, "Folder uploaded successfully.")
    return redirect("files:drive_folder", folder_id=root_folder.id) if root_folder else redirect("files:drive")

@login_required
def download(request, pk):
    file = get_object_or_404(File, pk=pk, owner=request.user)
    if not file.file:
        raise Http404()

    response = FileResponse(file.file.open(), as_attachment=True)
    response["Content-Disposition"] = f'attachment; filename="{file.name}"'
    return response

@login_required
@require_POST
def delete(request, pk):
    file = get_object_or_404(File, pk=pk, owner=request.user)
    folder_id = file.folder.id if file.folder else None
    file.file.delete()  # delete actual file from storage
    file.delete()  # delete db record
    messages.success(request, "File deleted successfully.")
    return redirect("files:drive_folder", folder_id=folder_id) if folder_id else redirect("files:drive")
