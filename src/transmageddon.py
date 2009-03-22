#!/usr/bin/env python

import sys
import os
import time
import transcoder_engine
import gobject; gobject.threads_init()
import gettext, locale


try:	
 	import pygtk
  	pygtk.require("2.0")
	import gobject
except:
  	pass
try:
	import gtk
  	import gtk.glade
except:
	sys.exit(1)
try:
	import pygst
	pygst.require("0.10")
	import gst
	import gst.interfaces
except: 
	pass

class TransmageddonUI (gtk.glade.XML):
	"""This class loads the Glade file of the UI"""

	def __init__(self):
		#Set the Glade file
		self.gladefile = "transmageddon.glade"  
	        gtk.glade.XML.__init__ (self, self.gladefile) 
		
		##Define functionality of our button and main window
		self.FileChooser = self.get_widget("FileChooser")
		self.CodecBox = self.get_widget("CodecBox")
		self.ContainerChoice = self.get_widget("ContainerChoice")
		self.vorbisbutton = self.get_widget("vorbisbutton") 
		self.flacbutton = self.get_widget("flacbutton")
		self.mp3button = self.get_widget("mp3button")
		self.aacbutton = self.get_widget("aacbutton")
		self.ac3button = self.get_widget("ac3button")
		self.speexbutton = self.get_widget("speexbutton")
		self.celtbutton = self.get_widget("celtbutton")
		self.alacbutton = self.get_widget("alacbutton")
 		self.theorabutton = self.get_widget("theorabutton")
		self.diracbutton = self.get_widget("diracbutton")
		self.h264button = self.get_widget("h264button")
		self.mpeg2button = self.get_widget("mpeg2button")
		self.mpeg4button = self.get_widget("mpeg4button")
		self.wma2button = self.get_widget("wma2button")
		self.wmv2button = self.get_widget("wmv2button")
		self.TranscodeButton = self.get_widget("TranscodeButton")
		self.ProgressBar = self.get_widget("ProgressBar")
		self.cancelbutton = self.get_widget("cancelbutton")

		self.signal_autoconnect(self) # Initialize User Interface


# Set the Videos XDG UserDir as the default directory for the filechooser, also make sure directory exists
		self.VideoDirectory = os.path.expanduser("~")+"/Videos/"
		CheckDir = os.path.isdir(self.VideoDirectory)
		if CheckDir == (False):
	   	   os.mkdir(self.VideoDirectory)
		self.FileChooser.set_current_folder(self.VideoDirectory)
		# elif CheckDir == (True): 
		#   print "Videos directory exist"
		# print self.VideoDirectory

		
		# Setting AppIcon
		main_window = gtk.Window(gtk.WINDOW_TOPLEVEL)
		main_window.set_icon_from_file("transmageddon.png")

		# default all but top box to insensitive by default
		self.ContainerChoice.set_sensitive(False)
		self.CodecBox.set_sensitive(False)
		self.TranscodeButton.set_sensitive(False)
		self.cancelbutton.set_sensitive(False)		

		self.AudioCodec = "vorbis"
		self.VideoCodec = "theora"
		self.ProgressBar.set_text("Transcoding Progress")

		self.p_duration = gst.CLOCK_TIME_NONE
		self.p_time = gst.FORMAT_TIME
	
	def Increment_Progressbar(self):
            "Returns a (position, duration) tuple"
            try:
               position, format = self._transcoder.uridecoder.query_position(gst.FORMAT_TIME)
            except:
               position = gst.CLOCK_TIME_NONE

            try:
               duration, format = self._transcoder.uridecoder.query_duration(gst.FORMAT_TIME)
            except:
               duration = gst.CLOCK_TIME_NONE
	    if position != gst.CLOCK_TIME_NONE:
               value = float(position) / duration
	       if float(value) < (1.0):
	         # print value
	         self.ProgressBar.set_fraction(value)
		 return True
	       else:
	     	  self.ProgressBar.set_fraction(1.0)	
            	  return False

	def ProgressBarUpdate(self): 
	 	gobject.timeout_add(500, self.Increment_Progressbar)
		print "Updating ProgressBar"

	# Set up function to start listening on the GStreamer bus

	def BusWatcher(self):
		bus = self._transcoder.pipeline.get_bus()
        	bus.add_watch(self.on_message)
        
	def on_message(self, bus, message):
	    mtype = message.type
	    if mtype == gst.MESSAGE_ERROR:
               err, debug = message.parse_error()
              # print "Error: %s" % err, debug
	    elif mtype == gst.MESSAGE_ASYNC_DONE:
	       StartProgressBar = self.ProgressBarUpdate()
	       print "Got ASYNC_DONE, starting ProgresBar"
            elif mtype == gst.MESSAGE_EOS:
               self.ProgressBar.set_text("Done Transcoding") 
	       return False
	    # print mtype        	
	    return True
			
	# The Transcodebutton is the one that calls the Transcoder class and thus starts the transcoding
	def on_TranscodeButton_clicked(self, widget):
		FileChoice = self.get_widget ("FileChooser").get_uri()
		FileName = self.get_widget ("FileChooser").get_filename()
		ContainerChoice = self.get_widget ("ContainerChoice").get_active_text ()
		self.FileChooser.set_sensitive(False)
		self.ContainerChoice.set_sensitive(False)
		self.CodecBox.set_sensitive(False)
		self.TranscodeButton.set_sensitive(False)
		self.cancelbutton.set_sensitive(True)
		self._transcoder = transcoder_engine.Transcoder(FileChoice, FileName, ContainerChoice, self.AudioCodec, self.VideoCodec)
		self.BusMessages = self.BusWatcher()
		
	def on_cancelbutton_clicked(self, widget):
		self.FileChooser.set_sensitive(True)
		self._cancel_encoding = transcoder_engine.Transcoder.Pipeline(self._transcoder,"null")
		self.ProgressBar.set_fraction(0.0)
		self.ProgressBar.set_text("Transcoding Progress")

	# define the behaviour of the other buttons
	def on_FileChooser_file_set(self, widget):
	  	self.ContainerChoice.set_sensitive(True)
		self.ProgressBar.set_fraction(0.0)
		self.ProgressBar.set_text("Transcoding Progress")

	def ContainerChoice_changed_cb(self, widget):
		self.CodecBox.set_sensitive(True)
		self.TranscodeButton.set_sensitive(True)		
		ContainerChoice = self.get_widget ("ContainerChoice").get_active_text ()
		print ContainerChoice		
		if ContainerChoice == "Ogg":
		  self.vorbisbutton.set_sensitive(True)
		  self.flacbutton.set_sensitive(True)
		  self.mp3button.set_sensitive(False)
		  self.aacbutton.set_sensitive(False)
		  self.ac3button.set_sensitive(False)
		  self.speexbutton.set_sensitive(True)
	          self.celtbutton.set_sensitive(True)
		  self.alacbutton.set_sensitive(False)
		  self.theorabutton.set_sensitive(True)
		  self.diracbutton.set_sensitive(True)
		  self.h264button.set_sensitive(False)
		  self.mpeg2button.set_sensitive(False)
		  self.mpeg4button.set_sensitive(False)
		  self.vorbisbutton.set_active(True)
		  self.theorabutton.set_active(True)
		  self.wma2button.set_sensitive(False)
		  self.wmv2button.set_sensitive(False)
	          
		elif ContainerChoice == "Matroska":
		  self.vorbisbutton.set_sensitive(True)
		  self.flacbutton.set_sensitive(True)
		  self.mp3button.set_sensitive(True)
		  self.aacbutton.set_sensitive(True)
		  self.ac3button.set_sensitive(True)
		  self.speexbutton.set_sensitive(True)
	          self.celtbutton.set_sensitive(True)
		  self.alacbutton.set_sensitive(True)
		  self.theorabutton.set_sensitive(True)
		  self.diracbutton.set_sensitive(True)
		  self.h264button.set_sensitive(True)
		  self.mpeg2button.set_sensitive(True)
		  self.mpeg4button.set_sensitive(True)
		  self.wma2button.set_sensitive(True)
		  self.wmv2button.set_sensitive(True)		
		  self.flacbutton.set_active(True)
		  self.AudioCodec = "flac"
		  self.diracbutton.set_active(True)
		  self.VideoCodec = "dirac"

		elif ContainerChoice == "AVI":
		  self.vorbisbutton.set_sensitive(False)
		  self.flacbutton.set_sensitive(False)
		  self.mp3button.set_sensitive(True)
		  self.aacbutton.set_sensitive(False)
		  self.ac3button.set_sensitive(True)
		  self.speexbutton.set_sensitive(False)
	          self.celtbutton.set_sensitive(False)
		  self.alacbutton.set_sensitive(False)
		  self.theorabutton.set_sensitive(False)
		  self.diracbutton.set_sensitive(True)
		  self.h264button.set_sensitive(True)
		  self.mpeg2button.set_sensitive(True)
		  self.mpeg4button.set_sensitive(True)
		  self.wma2button.set_sensitive(True)
		  self.wmv2button.set_sensitive(True)
		  self.mp3button.set_active(True)
		  self.AudioCodec = "mp3"
		  self.h264button.set_active(True)
		  self.VideoCodec = "h264"
		  print self.AudioCodec
		  print self.VideoCodec

		elif ContainerChoice == "Quicktime":
		  self.vorbisbutton.set_sensitive(False)
		  self.flacbutton.set_sensitive(False)
		  self.mp3button.set_sensitive(True)
		  self.aacbutton.set_sensitive(True)
		  self.ac3button.set_sensitive(True)
		  self.speexbutton.set_sensitive(False)
	          self.celtbutton.set_sensitive(False)
		  self.alacbutton.set_sensitive(True)
		  self.theorabutton.set_sensitive(False)
		  self.diracbutton.set_sensitive(True)
		  self.h264button.set_sensitive(True)
		  self.mpeg2button.set_sensitive(True)
		  self.mpeg4button.set_sensitive(True)
		  self.wma2button.set_sensitive(False)
		  self.wmv2button.set_sensitive(False)
		  self.aacbutton.set_active(True)
		  self.AudioCodec = "aac"
		  self.h264button.set_active(True)
		  self.VideoCodec = "h264"

		elif ContainerChoice == "MPEG4":
		  self.vorbisbutton.set_sensitive(False)
		  self.flacbutton.set_sensitive(False)
		  self.mp3button.set_sensitive(True)
		  self.aacbutton.set_sensitive(True)
		  self.ac3button.set_sensitive(False)
		  self.speexbutton.set_sensitive(False)
	          self.celtbutton.set_sensitive(False)
		  self.alacbutton.set_sensitive(False)
		  self.theorabutton.set_sensitive(False)
		  self.diracbutton.set_sensitive(False)
		  self.h264button.set_sensitive(True)
		  self.mpeg2button.set_sensitive(True)
		  self.mpeg4button.set_sensitive(True)
		  self.wma2button.set_sensitive(False)
		  self.wmv2button.set_sensitive(False)
		  self.aacbutton.set_active(True)
		  self.AudioCodec = "aac"
		  self.h264button.set_active(True)
		  self.VideoCodec = "h264"

		elif ContainerChoice == "MPEG PS":
		  self.vorbisbutton.set_sensitive(False)
		  self.flacbutton.set_sensitive(False)
		  self.mp3button.set_sensitive(True)
		  self.aacbutton.set_sensitive(True)
		  self.ac3button.set_sensitive(True)
		  self.speexbutton.set_sensitive(False)
	          self.celtbutton.set_sensitive(False)
		  self.alacbutton.set_sensitive(False)
		  self.theorabutton.set_sensitive(False)
		  self.diracbutton.set_sensitive(False)
		  self.h264button.set_sensitive(True)
		  self.mpeg2button.set_sensitive(True)
		  self.mpeg4button.set_sensitive(True)
		  self.wma2button.set_sensitive(False)
		  self.wmv2button.set_sensitive(False)
		  self.mp3button.set_active(True)
		  self.AudioCodec = "mp3"
		  self.mpeg2button.set_active(True)
		  self.VideoCodec = "mpeg2"
		  
		elif ContainerChoice == "MPEG TS":
		  self.vorbisbutton.set_sensitive(False)
		  self.flacbutton.set_sensitive(False)
		  self.mp3button.set_sensitive(True)
		  self.aacbutton.set_sensitive(True)
		  self.ac3button.set_sensitive(True)
		  self.speexbutton.set_sensitive(False)
	          self.celtbutton.set_sensitive(False)
		  self.alacbutton.set_sensitive(False)
		  self.theorabutton.set_sensitive(False)
		  self.diracbutton.set_sensitive(True)
		  self.h264button.set_sensitive(True)
		  self.mpeg2button.set_sensitive(True)
		  self.mpeg4button.set_sensitive(True)
		  self.wma2button.set_sensitive(False)
		  self.wmv2button.set_sensitive(False)
		  self.mp3button.set_active(True)
		  self.AudioCodec = "mp3"
		  self.mpeg2button.set_active(True)
		  self.VideoCodec = "mp3"
		  
		elif ContainerChoice == "FLV":
		  self.vorbisbutton.set_sensitive(False)
		  self.flacbutton.set_sensitive(False)
		  self.mp3button.set_sensitive(True)
		  self.aacbutton.set_sensitive(False)
		  self.ac3button.set_sensitive(False)
		  self.speexbutton.set_sensitive(False)
	          self.celtbutton.set_sensitive(False)
		  self.alacbutton.set_sensitive(False)
		  self.theorabutton.set_sensitive(False)
		  self.diracbutton.set_sensitive(False)
		  self.h264button.set_sensitive(True)
		  self.mpeg2button.set_sensitive(False)
		  self.mpeg4button.set_sensitive(False)
		  self.wma2button.set_sensitive(False)
		  self.wmv2button.set_sensitive(False)
		  self.mp3button.set_active(True)
		  self.AudioCodec = "mp3"
		  self.h264button.set_active(True)
		  self.VideoCodec = "h264"
		  
	def on_vorbisbutton_pressed(self, widget):
		self.AudioCodec = "vorbis"
		print "Radiobutton pressed choosing " + (self.AudioCodec)
 
	def on_flacbutton_pressed(self, widget):
		self.AudioCodec = "flac"
		print "Radiobutton pressed choosing " + (self.AudioCodec)

	def on_mp3button_pressed(self, widget):
		self.AudioCodec = "mp3"
		print "Radiobutton pressed choosing " + (self.AudioCodec)

	def on_aacbutton_pressed(self, widget):
		self.AudioCodec = "aac"
		print "Radiobutton pressed choosing " + (self.AudioCodec)

	def on_ac3button_pressed(self, widget):
		self.AudioCodec = "ac3"
		print "Radiobutton pressed choosing " + (self.AudioCodec)
	
	def on_speexbutton_pressed(self, widget):
		self.AudioCodec = "speex"
		print "Radiobutton pressed choosing " + (self.AudioCodec)

	def on_celtbutton_pressed(self, widget):
		self.AudioCodec = "celt"
		print "Radiobutton pressed choosing " + (self.AudioCodec)

	def on_alacbutton_pressed(self, widget):
		self.AudioCodec = "alac"
		print "Radiobutton pressed choosing " + (self.AudioCodec)

	def on_wma2button_pressed(self, widget):
		self.AudioCodec = "wma2"
		print "Radiobutton pressed choosing " + (self.AudioCodec)

	def on_theorabutton_pressed(self, widget):
		self.VideoCodec = "theora"
		print "Radiobutton pressed choosing " + (self.VideoCodec)
 
	def on_diracbutton_pressed(self, widget):
		self.VideoCodec = "dirac"
		print "Radiobutton pressed choosing " + (self.VideoCodec)

	def on_h264button_pressed(self, widget):
		self.VideoCodec = "h264"
		print "Radiobutton pressed choosing " + (self.VideoCodec)

	def on_mpeg2button_pressed(self, widget):
		self.VideoCodec = "mpeg2"
		print "Radiobutton pressed choosing " + (self.VideoCodec)

	def on_mpeg4button_pressed(self, widget):
		self.VideoCodec = "mpeg4"
		print "Radiobutton pressed choosing " + (self.VideoCodec)

	def on_wmv2button_pressed(self, widget):
		self.VideoCodec = "wmv2"
		print "Radiobutton pressed choosing " + (self.VideoCodec) 

	def main(name, version):
	    gettextName = 'debuggerDemo'
	    localeDir = '%s/locale' % _currentDir()
 	    gettext.bindtextdomain(gettextName, localeDir)
  	    gettext.textdomain(gettextName)
  	    gettext.install(gettextName, localeDir, unicode = 1)

	def on_MainWindow_destroy(self, widget):        #Close the program is you click X
		gtk.main_quit()          
	
if __name__ == "__main__":
	hwg = TransmageddonUI()
	gtk.main()


