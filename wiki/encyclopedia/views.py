from django import forms
from django.shortcuts import render, redirect
from django.urls import reverse
from markdown2 import Markdown
from random import choice

from . import util

markdowner = Markdown()


class NewPageForm(forms.Form):
    title = forms.CharField(label="Title:", widget=forms.TextInput(
        attrs={"placeholder": "Title for New Page"}
    ))
    new_entry = forms.CharField(label="New Entry:", widget=forms.Textarea(
        attrs={"class": "form-control", "placeholder": "New entry in Markdown here", "id": "Textarea", "rows": "10"}
    ))


class EditPageForm(forms.Form):
    updated_entry = forms.CharField(widget=forms.Textarea(
        attrs={"class": "form-control", "id": "Textarea", "rows": "8"}
    ))


def index(request):
    # If sent a post request (by submitting search box)
    if request.method == "POST":
        form = request.POST
        query = form["q"]

        # If query matches an entry, redirect to it
        if util.get_entry(query):
            return redirect(reverse("entry", args=[query]))
        
        else:
            # Get list for entries that have the query as substrings
            list_entries = util.list_entries()
            entries = []

            for item in list_entries:
                if query in item:
                    entries.append(item)

            return render(request, "encyclopedia/search.html", {
                "entries": entries
            })

    return render(request, "encyclopedia/index.html", {
        "entries": util.list_entries()
    })


def entry(request, title):
    # Check if entry exists, and show its page
    if util.get_entry(title):

        return render(request, "encyclopedia/entry.html", {
            "title": title,
            "entry": markdowner.convert(util.get_entry(title))
        })
    
    # If entry does not exist, show message "Not Found"
    return render(request, "encyclopedia/notfound.html", {
        "title": title
    }, status=404)


def new(request):
    # If request.method == "POST"
    if request.method == "POST":
        form = NewPageForm(request.POST)

        if form.is_valid():
            # Take in the data from the cleaned version of form
            title = form.cleaned_data["title"]
            new_entry = form.cleaned_data["new_entry"]

            # If title alrady exists display error message
            if util.get_entry(title):

                return render(request, "encyclopedia/invalid.html", status=403)

            # Otherwise, create and write a file called {title}
            with open(f"entries/{title}.md", "w") as f:
                f.write(new_entry)

            return redirect(reverse("entry", args=[title]))   

    # Else if the request is "GET"
    return render(request, "encyclopedia/newpage.html", {
        "form": NewPageForm()
    })


def edit(request, title):
    # When user submits form with updated version of entry
    if request.method == "POST":
        form = EditPageForm(request.POST)
        
        if form.is_valid():
            updated_entry = form.cleaned_data["updated_entry"]

            # Update file's entry
            with open(f"entries/{title}.md", "w") as f:
                f.write(updated_entry)
            
            # Redirect to entry's page
            return redirect(reverse("entry", args=[title]))
    
    # If method is "GET". Prepopulate textarea with current entry's md to show in the form
    initial = {"updated_entry": util.get_entry(title)}
    form = EditPageForm(initial=initial)

    return render(request, "encyclopedia/edit.html", {
        "title": title,
        "form": form
    })


def random(request):
    # Randomnly choose an entry from list of entries
    entries = util.list_entries()
    title = choice(entries)

    return redirect(reverse("entry", args=[title]))
