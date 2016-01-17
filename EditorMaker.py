print "Editor Maker for all these tile based games I'm making"

print "GAME NAME"
name = raw_input("Game Name: ")

print "BASIC ROOM PROPERTIES"
width = raw_input("Room width: ")
height = raw_input("Room height: ")

print "Editor display options"
dw = raw_input("Tile width for display: ")
dh = raw_input("Tile height for display: ")

#Generate the file
file = open(name + " editor.html", "w")

file.write("<html>\n<head>\n<title>")
file.write(name + " editor</title>\n")

print "Done."