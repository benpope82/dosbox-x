#!/usr/bin/python
from lxml import html
from lxml import etree
import stat
import os
import re

# open the template page file.
# Python will blow up with an exception here on failure.
htmt_tree = etree.parse("_page.html")
htmt_tree_root = htmt_tree.getroot()

# list and enumerate blog entries.
# each one is a directory of the form YYYY-MM-DD-HHMMSS
blogents = [ ]
dirreg = re.compile('^\d+', re.IGNORECASE)
for dirname in os.listdir("."):
    try:
        st = os.lstat(dirname)
        if stat.S_ISDIR(st.st_mode):
            if dirreg.match(dirname):
                try:
                    st2 = os.lstat(dirname+"/_page.html")
                    if stat.S_ISREG(st2.st_mode):
                        blogents.append(dirname)
                except:
                    True
    except:
        True

# sort into descending order
blogents.sort(reverse=True)

# load each blog
blogtree = { }
for ent in blogents:
    print "Loading " + ent + "..."
    broot = etree.parse(ent+"/_page.html")
    blogtree[ent] = broot

# get the title, if possible
blogtitles = { }
for ent in blogtree:
    tree = blogtree[ent]
    root = tree.getroot()
    title = root.find("./head/title")
    if not title == None:
        if not title.text == None and not title.text == "":
            blogtitles[ent] = title.text

# find the LIST_PLACEHOLDER and remove it from the tree
list_placeholder = htmt_tree_root.find("./body/LIST_PLACEHOLDER")
if not list_placeholder == None:
    list_placeholder_index = list_placeholder.getparent().index(list_placeholder)
    list_placeholder_parent = list_placeholder.getparent()
    list_placeholder_parent.remove(list_placeholder)
    #
    list_tbl = etree.SubElement(list_placeholder_parent, "table", attrib={"width":"100%"})
    #
    for ent in blogtree:
        tree = blogtree[ent] # I want Python to blow up with an exception if this is ever None or invalid
        title = blogtitles[ent]
        if title == None or title == "":
            title = "(no title)"
        #
        row = etree.SubElement(list_tbl, "tr")
        list_tbl.append(row)
        #
        rowtitle = etree.SubElement(row, "div")
        #
        href = ent + "/index.html";
        rowtitle_p1 = etree.SubElement(rowtitle, "a", attrib={"href":href})
        rowtitle_p1.text = title
        rowtitle.append(rowtitle_p1)
        #
        rowtitle_p2 = etree.SubElement(rowtitle, "span")
        rowtitle_p2.text = u" \u2014 " + ent
        rowtitle.append(rowtitle_p2)
        #
        rowtitle_p3 = etree.SubElement(rowtitle, "br")
        rowtitle.append(rowtitle_p3)
        #
        row.append(rowtitle)
        # TODO: Put the content of each entry in the main page... but only going back so far.
        content = tree.find('./body')
        if not content == None:
            content.tag = 'div'
            row.append(content)
            #
            rowpad1 = etree.SubElement(row, "br")
            row.append(rowpad1)
    #
    list_placeholder_parent.insert(list_placeholder_index,list_tbl)

# write the final result
htmt_tree.write("index.html", encoding='utf-8')
