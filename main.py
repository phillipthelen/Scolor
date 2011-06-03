#!/usr/bin/python2
# -*- coding: utf-8 -*-

import gobject
from gi.repository import Gtk, Gdk

class Color():
    name = ""
    
    def __init__(self, red, blue, green):
        self.color = Gdk.Color(red, blue, green)

class scolor():
    
    def main_quit(self, widget=None):
        Gtk.main_quit()

    def __init__(self):
        self.gui = Gtk.Builder()
        self.gui.add_from_file("scolor.glade")
        self.window = self.gui.get_object("mainwindow")
        self.colorlist = self.gui.get_object("colorlist")
        self.colorbox = self.gui.get_object("colorbox")
        self.modebox = self.gui.get_object("modebox")
        self.colorcount = self.gui.get_object("colorcount")
        self.colorbutton = self.gui.get_object("colorbutton")
        
        self.colorlist = []
        self.actcolor = 0
        self.colorlist.append(Color(0, 0, 0))
        self.redraw_colors(self)
        
        self.gui.connect_signals(self)
        self.window.connect("destroy", self.main_quit)
        self.window.show_all()
        
    def new_color(self, red, green, blue, name="", act=False):
        col = Color(red, green, blue)
        self.colorlist.append(col)
        col.name = col.name
        eb = Gtk.EventBox()
        label = Gtk.Label()
        eb.add(label)
        eb.modify_bg(0, col.color)
        if act:
            eb.set_border_width (4)
        self.colorlist.append(col)
        label.set_text(col.name + "\n" + col.color.to_string())
        if (col.color.red + col.color.green + col.color.blue) < 100000:
            label.modify_fg(0, Gdk.Color(65535, 65535, 65535))
        self.colorbox.pack_start(eb, True, True, 0)
        eb.show_all()
     
    def change_mode(self, widget=None):
        id = self.modebox.get_active()
        if id == 1:
            None
            
    def redraw_colors(self, widget=None, color=None):
        if color == None:
            color = self.colorlist[0].color
        colors = self.colorbox.get_children()
        for i in colors:
            self.colorbox.remove(i)
            
        del self.colorlist[:]
        
        count = self.colorcount.get_value()
        if count > 1:
            rstep = (65535-color.red) / (count-1)
            gstep = (65535-color.green) / (count-1)
            bstep = (65535-color.blue) / (count-1)
        else:
            rstep = (65535-color.red) / count
            gstep = (65535-color.green) / count
            bstep = (65535-color.blue) / count

        for i in range(0, int(count)):
            if count == 0:
                act = True
            else:
                act = False
            self.new_color(color.red + rstep*i, color.green + gstep*i, color.blue + bstep*i, act)
            
    def set_color(self, widget=None):
        colorsel = self.colorbutton.get_color()
        print colorsel
        self.redraw_colors(self, colorsel)
        
    def lighten_color(self, widget=None, color=None):
        if color == None:
            color = self.colorlist[0]
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
        self.redraw_colors(self, color.color)
        self.reload_toolbar(self, color=color)
        
    def darken_color(self, widget=None, color=None):
        if color == None:
            color = self.colorlist[0]
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
        self.redraw_colors(self, color.color)
        self.reload_toolbar(self, color=color)
        
    def saturate_color(self, widget=None, color=None):
        if color == None:
            color = self.colorlist[0]

    def desaturate_color(self, widget=None, color=None):
        if color == None:
            color = self.colorlist[0]
            
    def reload_toolbar(self, widget=None, color=None):
        if color.color == None:
            color = self.colorlist[0]
        if color.color.to_string() == "#ffffffffffff":
            None
    
    def add_color(self, widget=None):
        color = self.colorlist[0]
        self.colorlist.append(["test", color.color.to_string()])
        self.window.show_all()
        
if __name__ == "__main__":
    scolor()
    Gtk.main()
