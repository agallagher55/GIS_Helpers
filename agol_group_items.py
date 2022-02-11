from arcgis.gis import GIS

gis = GIS('pro')

GROUP_ID = "48d1d894e65e47c99a07bbf9bb8b0b24"

# items = gis.content.search(query="")
# print(items)

# GET GROUP - https://developers.arcgis.com/python/guide/accessing-and-managing-groups/
# group = gis.groups.search("title:GIS Hub")
group = gis.groups.search(f"id:{GROUP_ID}")[0]
print(group)

# GET ITEMS IN GROUP
group_content = group.content()
print()

# Filter Items for App items
for count, item in enumerate(group_content, start=1):
    if item.type == 'Web Mapping Application':
        print(f"{count}) {item.title}")
