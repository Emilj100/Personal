from django.shortcuts import render
import markdown2

from . import util

def index(request):
    return render(request, "encyclopedia/index.html", {
        "entries": util.list_entries()
    })

def entry(request, title):
    entry = util.get_entry(title)
    if not entry:
        return render(request, "encyclopedia/error.html", {
            "error": "The requested page could not be found"
        })
    else: 
        return render(request, "encyclopedia/entry.html", {
            "content": markdown2.markdown(entry)
        })

def search(request):
    if request.method == "POST":
        search = request.POST.get("query")
        entry = util.get_entry(search)
        if entry:
            return render(request, "encyclopedia/entry.html", {
            "content": markdown2.markdown(entry)
        })
        else:
            matching_entries = []
            all_entries = util.list_entries()
            for entry in all_entries:
                if search.lower() in entry.lower():
                    matching_entries.append(entry)
            return render(request, "encyclopedia/search_results.html", {
                "entries": matching_entries 
            })

def new_page(request):
    if request.method == "POST":
        title = request.POST.get("title")
        content = request.POST.get("content")
        all_entries = util.list_entries()

        for entry in all_entries:
            if title.lower() == entry.lower():
                return render(request, "encyclopedia/error.html", {
                    "error": "A page with the title already exist"
                })
            
        content = f"# {title}\n\n{content}"
        util.save_entry(title, content)
        entry = util.get_entry(title)
        if not entry:
            return render(request, "encyclopedia/error.html", {
                "error": "The requested page could not be found"
            })
        else: 
            return render(request, "encyclopedia/entry.html", {
                "content": markdown2.markdown(entry)
            })

    return render(request, "encyclopedia/new_page.html")

    

