from django.shortcuts import render
import markdown2
from django.http import HttpResponseRedirect
from django.urls import reverse
import random

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
            "title": title,
            "content": markdown2.markdown(entry)
        })

def edit_page(request, title):
    if request.method == "POST":
        new_content = request.POST.get("content")
        util.save_entry(title, new_content)
        return HttpResponseRedirect(reverse("wiki:entry", args=[title]))

    return render(request, "encyclopedia/edit_page.html", {
        "title": title,
        "content": util.get_entry(title)
    })

def search(request):
    if request.method == "POST":
        query = request.POST.get("query")
        entry = util.get_entry(query)
        if entry:
            return render(request, "encyclopedia/entry.html", {
                "title": query, 
                "content": markdown2.markdown(entry)
            })
        else:
            matching_entries = []
            all_entries = util.list_entries()
            for entry in all_entries:
                if query.lower() in entry.lower():
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
                "title": title,
                "content": markdown2.markdown(entry)
            })

    return render(request, "encyclopedia/new_page.html")

    
def random_page(request):
    entries = util.list_entries()
    random_entry = random.choice(entries)
    return HttpResponseRedirect(reverse("wiki:entry", args=[random_entry]))
