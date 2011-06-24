#!/usr/bin/python2
# -*- coding: utf-8 -*-

#Copyright (C) 2011 by Phillip Thelen

#Permission is hereby granted, free of charge, to any person obtaining a copy
#of this software and associated documentation files (the "Software"), to deal
#in the Software without restriction, including without limitation the rights
#to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
#copies of the Software, and to permit persons to whom the Software is
#furnished to do so, subject to the following conditions:

#The above copyright notice and this permission notice shall be included in
#all copies or substantial portions of the Software.

#THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
#IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
#FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
#AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
#LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
#OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
#THE SOFTWARE.

import pygtk
import gtk
import random
import os
import ConfigParser
import xml.dom.minidom
import datetime

pname = "Scolor"
version = "0.4"

class Color():
    name = ""
    group = ""
    
    def __init__(self, red, blue, green):
        self.color = gtk.gdk.Color(red, blue, green)
    
    def get_hexstr(self):
        red, green, blue = self.get_rgb()
        return "#%02X%02X%02X" % (red, green, blue)
        
    
    def get_rgbstr(self):
        red, green, blue = self.get_rgb()
        return "rgb(%s, %s, %s)" % (red, green, blue)
        
    def get_hex(self):
        red, green, blue = self.get_rgb()
        return hex(red), hex(green), hex(blue)
    
    def get_rgb(self):
        red = self.color.red
        green = self.color.green
        blue = self.color.blue
        pers = (65535 / 100.0)
        red = int(round(red / pers * 2.55))
        green = int(round(green / pers * 2.55))
        blue = int(round(blue / pers * 2.55))
        return red, green, blue

class Scolor():
    
    def main_quit(self, widget=None):
        rect = self.window.allocation
        if not self.config.has_section('WINDOW'):
            self.config.add_section('WINDOW')
        self.config.set('WINDOW','width', rect.width)
        self.config.set('WINDOW','height', rect.height)
        self.config.set('WINDOW','paned_pos',self.mainhpane.get_position())
        self.config.set('WINDOW','last_mode', self.modebox.get_active())
        self.config.set('WINDOW','colorcount', int(self.colorcount.get_value()))
        self.config.set('WINDOW','colorpos', int(self.colorpos.get_value()))
        self.config.set('WINDOW','columnwidth', int(self.treeview.get_column(0).get_width()))
        self.config.set('WINDOW','compareexpanded', int(self.compareexpander.get_expanded()))
        
        if not self.config.has_section("LASTCOL"):
            self.config.add_section("LASTCOL")
        self.config.set("LASTCOL","name", self.actcolor.name)
        self.config.set("LASTCOL","group", self.actcolor.group)
        self.config.set("LASTCOL","red", self.actcolor.color.red)
        self.config.set("LASTCOL","green", self.actcolor.color.green)
        self.config.set("LASTCOL","blue", self.actcolor.color.blue)
        
        configfile = open(self.configpath+'Scolor.cfg', 'w')
        self.config.write(configfile)
        configfile.close()
        
        doc = xml.dom.minidom.Document()
        
        colors = doc.createElement("colors")
        doc.appendChild(colors)

        for entry in self.colorview:
            if entry[0] == True:
                children = entry.iterchildren()
                for e in children:
                    color = doc.createElement("color")
                    colors.appendChild(color)
                    
                    name = doc.createElement("name")
                    color.appendChild(name)

                    nametext = doc.createTextNode(e[2])
                    name.appendChild(nametext)
                    
                    group = doc.createElement("group")
                    color.appendChild(group)

                    grouptext = doc.createTextNode(entry[2])
                    group.appendChild(grouptext)
                    
                    values = doc.createElement("values")
                    values.setAttribute("red", str(e[3]))
                    values.setAttribute("green", str(e[4]))
                    values.setAttribute("blue", str(e[5]))
                    values.setAttribute("group", entry[2])
                    color.appendChild(values)
            else:
                color = doc.createElement("color")
                colors.appendChild(color)
                
                name = doc.createElement("name")
                color.appendChild(name)

                # Give the <p> elemenet some text
                nametext = doc.createTextNode(entry[2])
                name.appendChild(nametext)
                
                values = doc.createElement("values")
                values.setAttribute("red", str(entry[3]))
                values.setAttribute("green", str(entry[4]))
                values.setAttribute("blue", str(entry[5]))
                color.appendChild(values)
        
        # Print our newly created XML
        coldoc = open(self.configpath+'colors.xml', 'w')
        coldoc.write(doc.toprettyxml(indent="  "))
        coldoc.close()
        gtk.main_quit()

    def __init__(self):
        self.load_config()
        self.load_gui()
        

    def load_gui(self):
        self.gui = gtk.Builder()
        self.gui.add_from_file("scolor2.glade")
        self.window = self.gui.get_object("mainwindow")
        self.colorview = self.gui.get_object("colorstore")
        self.colorbox = self.gui.get_object("colorbox")
        self.modebox = self.gui.get_object("modebox")
        self.colorcount = self.gui.get_object("colorcount")
        self.colorpos = self.gui.get_object("colorpos")
        self.colorbutton = self.gui.get_object("colorbutton")
        self.mainhpane = self.gui.get_object("mainhpane")
        self.mainhpane.resize = False
        self.statusbar = self.gui.get_object("statusbar")
        self.compareexpander = self.gui.get_object("compareexpander")
        self.comparisonbox = self.gui.get_object("comparisonbox")
        self.comparisonbox.drag_source_set(gtk.gdk.BUTTON1_MASK, [], 0)
        self.comparisonbox.drag_dest_set(0, [], gtk.gdk.ACTION_MOVE)
        self.leftvbox = self.gui.get_object("leftvbox")
        self.treeview = self.gui.get_object("treeview")
        self.treeselection = self.treeview.get_selection()
        self.treeselection.set_mode(gtk.SELECTION_MULTIPLE)
        self.treeselection.connect("changed", self.redraw_comparison)
        self.removegroupsave = self.gui.get_object("removegroupsave")
        self.removecolorsave = self.gui.get_object("removecolorsave")
        self.colorpopup = self.gui.get_object("colorpopup")
        self.clipboard = gtk.clipboard_get(gtk.gdk.SELECTION_CLIPBOARD)
        self.popupcopy = self.gui.get_object("copybutton")
        self.popupremove = self.gui.get_object("removebutton")
        self.tooltips = gtk.Tooltips()
                
        if self.config.has_section('WINDOW'):
            self.window.resize(int(self.config.get("WINDOW", "width")), int(self.config.get("WINDOW", "height")))
            self.mainhpane.set_position(int(self.config.get("WINDOW", "paned_pos")))
            self.modebox.set_active(int(self.config.get("WINDOW", "last_mode")))
            self.colorcount.set_value(int(self.config.get("WINDOW", "colorcount")))
            self.colorpos.set_value(int(self.config.get("WINDOW", "colorpos")))
            self.compareexpander.set_expanded(int(self.config.get("WINDOW", "compareexpanded")))
            #self.treeview.get_column(0).set_width(int(self.config.get("WINDOW", "columnwidth")))
        
        if self.config.has_section("LASTCOL"):
            red = int(self.config.get("LASTCOL", "red"))
            green = int(self.config.get("LASTCOL", "green"))
            blue = int(self.config.get("LASTCOL", "blue"))
            self.actcolor = Color(red, green, blue)
            self.actcolor.name = self.config.get("LASTCOL", "name")
            self.actcolor.group = self.config.get("LASTCOL", "group")
        else:
            self.actcolor = Color(0, 0, 0)
        self.colorlist = []
        self.colorlist.append(self.actcolor)
        self.redraw_colors()
        self.change_color(self.actcolor)
        
        self.parse_colors()
        
        self.gui.connect_signals(self)
        self.window.connect("destroy", self.main_quit)
        self.window.show_all()

    def load_config(self):
        self.config=ConfigParser.ConfigParser()
        self.configpath = os.path.expanduser('~')+'/.config/Scolor/'
        if os.path.exists(self.configpath):
            if os.path.exists(self.configpath +'Scolor.cfg'):
                configfile= open(self.configpath +'Scolor.cfg')
                self.config.readfp(configfile)
                self.config.read(configfile)
                configfile.close()
                                
        else:
            os.makedirs(self.configpath)

    def parse_colors(self):
        if os.path.exists(self.configpath):
            if os.path.exists(self.configpath +'colors.xml'):
                glist = {}
                colorfile = xml.dom.minidom.parse(self.configpath +'colors.xml')
                colors = colorfile.getElementsByTagName("color")
                for color in colors:
                    
                    groupn = color.getElementsByTagName("group")
                    if groupn != []:
                        groupn = self.xmlgetText(groupn[0].childNodes)
                        if not groupn in glist:
                            
                            group = [1, "", groupn, 0, 0, 0, None]
                            piter = self.colorview.append(None, group)
                            glist[groupn] = piter
                        else:
                            piter = glist[groupn]
                    else:
                        piter = None
                    
                    values = color.getElementsByTagName("values")[0]
                    red = values.getAttribute("red")
                    green = values.getAttribute("green")
                    blue = values.getAttribute("blue")
                    col = Color(int(red), int(green), int(blue))
                    name = color.getElementsByTagName("name")[0].childNodes
                    col.name = self.xmlgetText(name)
                    col.group = groupn
                    pixbuf = self.draw_colorbuf(col.color)
                    newcol = [0, col.get_hexstr(), col.name, col.color.red, col.color.green, col.color.blue, pixbuf]
                    self.colorview.append(piter, newcol)
                self.treeview.expand_all()


    def new_color(self, red, green, blue, name="", act=False):
        col = Color(int(red), int(green), int(blue))
        col.name = name
        frame = gtk.Frame()
        eb = gtk.EventBox()
        eb.add_events(gtk.gdk.BUTTON_PRESS_MASK)
        eb.connect("button-press-event", self.select_color)
        label = gtk.Label()
        frame.add(eb)
        eb.add(label)
        
        eb.modify_bg(0, col.color)
        if act:
            frame.modify_bg(0, gtk.gdk.Color(0, 0, 0))
        self.colorlist.append(col)
        label.set_text("%s\n%s\n%s" % (col.name, col.get_hexstr(), col.get_rgbstr()))
        label.set_justify(gtk.JUSTIFY_CENTER)
        if (col.color.red + col.color.green + col.color.blue) < 100000:
            label.modify_fg(0, gtk.gdk.Color(65535, 65535, 65535))
        self.colorbox.pack_start(frame, True, True, 0)
        frame.show_all()
     
    def change_mode(self, widget=None):
        id = self.modebox.get_active()
        if id == 1:
            None
            
    def redraw_colors(self, widget=None, color=None):
        if color == None:
            color = self.actcolor
        colors = self.colorbox.get_children()
        for i in colors:
            self.colorbox.remove(i)
            
        del self.colorlist[:]
        
        count = self.colorcount.get_value()
        pos = self.colorpos.get_value()
        
        if pos > count:
            pos = count
            self.colorpos.set_value(pos)
        
        self.colorpos.set_range(1, count)
        
        if pos > 1:
            rdstep = (color.color.red) / (pos-1)
            gdstep = (color.color.green) / (pos-1)
            bdstep = (color.color.blue) / (pos-1)
        else:
            rdstep = color.color.red
            gdstep = color.color.green
            bdstep = color.color.blue
        
        for i in range(1, int(pos)):
            i = pos - i
            red = int(color.color.red - rdstep*i)
            green = int(color.color.green - gdstep*i)
            blue = int(color.color.blue - bdstep*i)
            self.new_color(red, green, blue)
            
        self.new_color(color.color.red, color.color.green, color.color.blue, act=True, name=color.name)
        
        if (count-pos) > 1:
            rlstep = (65535-color.color.red) / (count-pos)
            glstep = (65535-color.color.green) / (count-pos)
            blstep = (65535-color.color.blue) / (count-pos)
        else:
            rlstep = 65535-color.color.red
            glstep = 65535-color.color.green
            blstep = 65535-color.color.blue

        for i in range(1, int(count-pos+1)):
            red = int(color.color.red + rlstep*i)
            green = int(color.color.green + glstep*i)
            blue = int(color.color.blue + blstep*i)
            self.new_color(red, green, blue)
            
    def set_color(self, widget=None):
        colorsel = self.colorbutton.get_color()
        color = Color(colorsel.red, colorsel.green, colorsel.blue)
        self.redraw_colors(self, color=color)
        self.actcolor = color
        
    def lighten_color(self, widget=None, color=None):
        if color == None:
            color = self.actcolor
        if color.color.red <= 61535:
            color.color.red += 4000
        else:
            color.color.red = 65535
            
        if color.color.green <= 61535:
            color.color.green += 4000
        else:
            color.color.green = 65535
            
        if color.color.blue <= 61535:
            color.color.blue += 4000
        else:
            color.color.blue = 65535
        self.actcolor = color
        self.redraw_colors()
        self.reload_toolbar()
        
    def darken_color(self, widget=None, color=None):
        if color == None:
            color = self.actcolor
        if color.color.red >= 4000:
            color.color.red -= 4000
        else:
            color.color.red = 0
            
        if color.color.green >= 4000:
            color.color.green -= 4000
        else:
            color.color.green = 0
            
        if color.color.blue >= 4000:
            color.color.blue -= 4000
        else:
            color.color.blue = 0
        self.actcolor = color
        self.redraw_colors()
        self.reload_toolbar()
        
    def saturate_color(self, widget=None, color=None):
        if color == None:
            color = self.actcolor
        red = color.color.red
        green = color.color.green
        blue = color.color.blue
        avg = (red + green + blue) / 3
        if red > avg and red <= 61535:
            red += 4000
        elif red < avg-2000 and red  >= 4000:
            red -= 4000
            
        if green > avg+2000 and green <= 61535:
            green += 4000
        elif green < avg-2000 and green >= 4000:
            green -= 4000
            
        if blue > avg+2000 and blue <= 61535:
            blue += 4000
        elif blue < avg-2000 and blue >= 4000:
            blue -= 4000
        color.color.red = red
        color.color.green = green
        color.color.blue = blue
        self.change_color(color)
        self.redraw_colors()

    def desaturate_color(self, widget=None, color=None):
        if color == None:
            color = self.actcolor
        red = color.color.red
        green = color.color.green
        blue = color.color.blue
        avg = (red + green + blue) / 3
        if red >= avg+4000:
            red -= 4000
        elif red <= avg-4000:
            red += 4000
            
        if green >= avg+4000:
            green -= 4000
        elif green <= avg-4000:
            green += 4000
            
        if blue >= avg+4000:
            blue -= 4000
        elif blue <= avg-4000:
            blue += 4000
        color.color.red = red
        color.color.green = green
        color.color.blue = blue
        self.change_color(color)
        self.redraw_colors()
        #self.reload_toolbar(self, color=color)
        
    def random_color(self, widget=None):
            red = random.randint(1, 65535)
            green = random.randint(1, 65535)
            blue = random.randint(1, 65535)
            self.change_color(Color(red, green, blue))
            self.redraw_colors()
            
    def reload_toolbar(self, widget=None, color=None):
        if color.color == None:
            color = self.actcolor
    
    def select_color(self, widget=None, event=None):
        parent = widget.parent
        frames = self.colorbox.get_children()
        for i, frame in enumerate(frames):
            if frame == parent:
                frame.modify_bg(0, gtk.gdk.Color(0, 0, 0))
                self.change_color(self.colorlist[i])
            else:
                frame.modify_bg(0, gtk.gdk.Color(65535, 65535, 65535))
        if event.button == 3:
            self.popupremove.set_sensitive(False)
            self.popupcopy.set_sensitive(True)
            time = event.time
            self.colorpopup.popup( None, None, None, event.button, time)
            return True
    
    def change_color(self, color):
        self.actcolor = color
        self.statusbar.pop(0)
        self.statusbar.push(0, "Current color: %s" % self.actcolor.get_hexstr())
        self.colorbutton.set_color(self.actcolor.color)
        
    
    def save_color(self, widget=None, col=None):
        if col == None:
            col = self.actcolor
        pixbuf = self.draw_colorbuf(col.color)
        newcol = [0, col.get_hexstr(), col.name, col.color.red, col.color.green, col.color.blue, pixbuf]
        row, col = self.treeview.get_cursor()
        if row != None:
            if self.colorview[row][0] == True or len(row) == 2:
                piter = self.colorview.get_iter(row[0])
                firrow = self.colorview.get_path(piter)[0]
                secrow = self.colorview.iter_n_children(piter)
                path = (firrow, secrow)
            else:
                piter = None
                path = (len(self.colorview), )
        else:
            piter = None
            path = (len(self.colorview), )
        self.colorview.append(piter, newcol)
        col = self.treeview.get_column(0)
        if piter != None:
            self.treeview.expand_row(row, True)
        self.treeview.set_cursor(path, col, True)
    
    def draw_colorbuf(self, color, x=16, y=16, border=True):
        pixbuf = gtk.gdk.Pixbuf(gtk.gdk.COLORSPACE_RGB, False, 8, x, y)
        drawable = gtk.gdk.Pixmap(None, x, y, 24)
        gc = drawable.new_gc()
        cmap = gc.get_colormap()
        color = cmap.alloc_color(color)
        gc.set_foreground(color)
        drawable.draw_rectangle(gc, True, 0, 0, x-1, y-1)
        if border:
            color = cmap.alloc_color("Black")
            gc.set_foreground(color)
            drawable.draw_rectangle(gc, False, 0, 0, x-1, y-1)
        pixbuf.get_from_drawable(drawable, cmap, 0, 0, 0, 0, x, y)
        return pixbuf
    
    def remove_color(self, widget=None):
        row, col = self.treeview.get_cursor()
        item = self.colorview[row]
        if item[0] == False:
            piter = self.colorview.get_iter(row)
            self.colorview.remove(piter)
    
    def add_group(self, widget=None):
        group = [1, "", "Group", 0, 0, 0, None]
        self.colorview.append(None, group)
        col = self.treeview.get_column(0)
        self.treeview.set_cursor(len(self.colorview)-1, col, True)
        
    def remove_group(self, widget=None):
        row, col = self.treeview.get_cursor()
        item = self.colorview[row]
        if item[0] == True:
            piter = self.colorview.get_iter(row)
            self.colorview.remove(piter)
        
    def save_name(self, widget=None, pos=None, name=None):
        item = self.colorview[pos]
        self.colorview[pos][2] = name
        if item[0] == False:
            color = Color(item[3], item[4], item[5])
            color.name = item[2]
            self.change_color(color)
            self.redraw_colors()
        self.treeview.show_all()
    
    def colorrow_selected(self, widget=None):
        row, col = self.treeview.get_cursor()
        item = self.colorview[row]
        if item[0] == False:
            color = Color(item[3], item[4], item[5])
            color.name = item[2]
            self.change_color(color)
            self.redraw_colors()
            self.removecolorsave.set_sensitive(True)
            self.removegroupsave.set_sensitive(False)
        else:
            self.removecolorsave.set_sensitive(False)
            self.removegroupsave.set_sensitive(True)
    
    def popup_menu_treeview(self,widget=None, event=None):
        if event.button == 3:
            x = int(event.x)
            y = int(event.y)
            time = event.time
            pthinfo = self.treeview.get_path_at_pos(x, y)
            if pthinfo is not None:
                path, col, cellx, celly = pthinfo
                item = self.colorview[path]
                self.popupremove.set_sensitive(True)
                if item[0] == False:
                    self.popupcopy.set_sensitive(True)
                    self.popupremove.connect("activate", self.remove_color)
                else:
                    self.popupcopy.set_sensitive(False)
                    self.popupremove.connect("activate", self.remove_group)
                self.treeview.grab_focus()
                self.treeview.set_cursor( path, col, 0)
                self.colorpopup.popup( None, None, None, event.button, time, self.actcolor)
            return True
    
    def copy_color(self, widget):
        hexstr = self.actcolor.get_hexstr()
        self.clipboard.set_text(hexstr)
    
    def xmlgetText(self, nodelist):
        rc = []
        for node in nodelist:
            if node.nodeType == node.TEXT_NODE:
                rc.append(node.data)
        string = ''.join(rc)
        return string.strip()
        
    def cmpdrag_select(self, widget, context):
        self.dragwidget = widget

    def cmpdrag_starts(self, widget, context):
        color = self.dragwidget.get_style().bg[0]
        context.set_icon_pixbuf(self.draw_colorbuf(color, 32, 32), 20, 22)
        self.dragwidget.hide()
        
    def cmpdrag_dropped(self, widget, context, x, y, time):
        position = -1
        compboxalloc = self.comparisonbox.get_allocation()
        print x, compboxalloc.x, y, compboxalloc.y
        if x < 0 or y < 0 or x > compboxallox.x or y > compboxalloc.y:
            print False
            return False
        for widget in self.comparisonbox.get_children():
            alloc = widget.get_allocation()
            if alloc.x +  (alloc.width / 2) > x:
                position = self.comparisonbox.child_get_property(widget, "position")
                if position > self.comparisonbox.child_get_property(self.dragwidget, "position"):
                    position -= 1
                break
        self.comparisonbox.reorder_child(self.dragwidget, position)
        self.dragwidget.show_all()
        self.dragwidget = None
        context.finish(True, False, time)
        return True

    def cmpdrag_motion(self, widget, context, x, y, time):
        context.drag_status(gtk.gdk.ACTION_MOVE, time)
        return True
    
    def cmpdrag_failed(self, widget, context, result):
        self.dragwidget.show()
    
    def cmpcolor_dragged(self, widget, context, x, y, time):
        pthinfo = self.treeview.get_path_at_pos(x, y)
        if pthinfo is not None:
                path, col, cellx, celly = pthinfo
                item = self.colorview[path]
    
    def redraw_comparison(self, widget=None):
        widgets = self.comparisonbox.get_children()
        rows = self.treeselection.get_selected_rows()
        for i in widgets:
            self.comparisonbox.remove(i)
        for row in rows[1]:
            item = self.colorview[row]
            if item[0] == False:
                color = Color(item[3], item[4], item[5])
                color.name = item[2]
                eb = gtk.EventBox()
                eb.modify_bg(0, color.color)
                eb.connect("button-press-event", self.cmpdrag_select)
                self.tooltips.set_tip(eb, "%s\n%s\n%s" % (color.name, color.get_hexstr(), color.get_rgbstr()))
                self.comparisonbox.pack_start(eb, True, True, 0)
                eb.show_all()
            else:
                piter = self.colorview.get_iter(row[0])
                children = self.colorview.iter_n_children(piter)
                for i in range(0, children):
                    child = self.colorview.iter_nth_child(piter, i)
                    name, red, green, blue = self.colorview.get(child, 2, 3, 4, 5)
                    color = Color(red, green, blue)
                    color.name = name
                    eb = gtk.EventBox()
                    eb.modify_bg(0, color.color)
                    eb.connect("button-press-event", self.cmpdrag_select)
                    self.tooltips.set_tip(eb, "%s\n%s\n%s" % (color.name, color.get_hexstr(), color.get_rgbstr()))
                    self.comparisonbox.pack_start(eb, True, True, 0)
                    eb.show_all()
    
    def export_all_colors(self, widget):
        filedialog = gtk.FileChooserDialog(action=gtk.FILE_CHOOSER_ACTION_SAVE, buttons=(gtk.STOCK_CANCEL,gtk.RESPONSE_CANCEL,gtk.STOCK_SAVE,gtk.RESPONSE_OK))
        filedialog.set_default_response(gtk.RESPONSE_OK)
        
        response = filedialog.run()
        if response == gtk.RESPONSE_OK:
            path = filedialog.get_filename()
            rest, filename = path.rsplit("/", 1)
            folder = rest.rsplit("/", 1)[1]
            if os.path.exists(path):
                confirmation = self.confirmdialog(filename=filename, folder=folder)
                if confirmation == gtk.RESPONSE_OK:
                    date = datetime.date.today()        
                    f = file(path, "w")
                    f.write("""GIMP Palette
Name: Scolor Colors, exported {0}/{1}/{2}
Columns: 0\n""".format(date.year, date.month, date.day))
                    for color in self.colorview:
                        if color[0] == False:
                            col = Color(color[3], color[4], color[5])
                            red, green, blue = col.get_rgb()
                            if color[2] != "":
                                name = color[2]
                            else:
                                name = color[1]
                            f.write("{0:>3} {1:>3} {2:>3} {3}\n".format(red, green, blue, name))
                        else:
                            piter = self.colorview.get_iter(row[0])
                            children = self.colorview.iter_n_children(piter)
                            for i in range(0, children):
                                child = self.colorview.iter_nth_child(piter, i)
                                hexcode, name, red, green, blue = self.colorview.get(child, 1, 2, 3, 4, 5)
                                col = Color(red, green, blue)
                                col.name = name
                                red, green, blue = col.get_rgb()
                                if name == "":
                                    name = hexcode
                                f.write("{0:>3} {1:>3} {2:>3} {3}\n".format(red, green, blue, name))
                        filedialog.destroy()
    
    def confirmdialog(self, filename="", folder=""):
        dialog = gtk.MessageDialog(buttons=(gtk.BUTTONS_OK_CANCEL), type=gtk.MESSAGE_QUESTION,
            message_format='A file named "{0}" already exists.  Do you want to replace it?'.format(filename))
        if secmessage != "":
            dialog.format_secondary_text('The file already exists in "{0}".  Replacing it will overwrite its contents.'.format(folder))
        response = dialog.run()
        dialog.destroy()
        return response
    
    def about(self, widget=None):
        pixbuf = gtk.gdk.pixbuf_new_from_file("icon.svg")
        aboutwindow = gtk.AboutDialog()
        aboutwindow.set_parent(self.window)
        aboutwindow.set_title("About " + pname)
        aboutwindow.set_name(pname)
        aboutwindow.set_version(version)
        aboutwindow.set_copyright("© 2011 Phillip Thelen")
        aboutwindow.set_comments("A colorscheme designer written in Python")
        aboutwindow.set_website("http://github.com/vIiRuS/Scolor")
        aboutwindow.set_website_label("Github Page")
        aboutwindow.set_authors(["Phillip Thelen <viirus@pherth.net>",])
        aboutwindow.set_wrap_license(True)
        aboutwindow.set_logo(pixbuf)
        aboutwindow.set_license("""Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
THE SOFTWARE.""")
        result = aboutwindow.run()
        aboutwindow.destroy()
        
if __name__ == "__main__":
    Scolor()
    gtk.main()
