#!/usr/bin/env python

import sys
import os
import datetime

try:	
 	import pygtk
  	pygtk.require("2.0")
except:
  	pass
try:
	import gtk
  	import gtk.glade
	import gobject; gobject.threads_init()
except:
	sys.exit(1)
try:
	import pygst
	pygst.require("0.10")
	import gst
except: 
	pass


class Transcoder:

    def __init__(self, FileChosen, FileName, ContainerChoice, AudioCodecValue, VideoCodecValue):

	# create a dictionay taking the Codec/Container values and mapping them with plugin names
	# No asfmux atm, hopefully Soc will solve that

	CONTAINERMAP = { 'Ogg' : "oggmux",
			 'Matroska' : "matroskamux",
			 'MXF' : "mxfmux",
			 'AVI' : "avimux",
			 'Quicktime' : "qtmux",
			 'MPEG4' : "mp4mux",
			 'MPEG PS' : "ffmux_mpeg",
			 'MPEG TS' : "mpegtsmux",
			 'FLV' : "flvmux" }

	CSUFFIXMAP = { 'Ogg' : ".ogg",
		       'Matroska' : ".mkv",
		       'MXF' : ".mxf",
		       'AVI' : ".avi",
		       'Quicktime' : ".mov",
		       'MPEG4' : ".mp4",
		       'MPEG PS' : ".mpg",
		       'MPEG TS' : ".ts",
		       'FLV' : ".flv" }

	CODECMAP = { 'vorbis' : "vorbisenc", 
		     'flac' : "flacenc",
		     'mp3' : "lame",
		     'aac' : "faac",
		     'ac3' : "ffenc_ac3",
		     'speex' : "speexenc",
		     'celt' : "celtenc",
		     'alac' : "ffenc_alac",
		     'wma2' : "ffenc_wmav2",
		     'theora' : "theoraenc", 
		     'dirac' : "schroenc",
		     'h264' : "x264enc",
		     'mpeg2' : "mpeg2enc",
		     'mpeg4' : "ffenc_mpeg4",
		     'diracpro' : "schroenc",
		     'dnxhd' : "ffenc_dnxhd",
		     'wmv2' : "ffenc_wmv2" }

	# Choose plugin based on Codec Name
	self.AudioEncoderPlugin = CODECMAP[AudioCodecValue]
	self.VideoEncoderPlugin = CODECMAP[VideoCodecValue]

	# Choose plugin and file suffix based on Container name
	self.ContainerFormatPlugin = CONTAINERMAP[ContainerChoice]
	self.ContainerFormatSuffix = CSUFFIXMAP[ContainerChoice]
	
	# Remove suffix from inbound filename so we can reuse it together with suffix to create outbound filename
	self.FileNameOnly = os.path.splitext(os.path.basename(FileName))[0]
	self.VideoDirectory = os.path.expanduser("~")+"/Videos/"
	CheckDir = os.path.isdir(self.VideoDirectory)
	if CheckDir == (False):
	   os.mkdir(self.VideoDirectory)
	# elif CheckDir == (True): 
	#   print "Videos directory exist"
	# print self.VideoDirectory

	# create a variable with a timestamp code
	timeget = datetime.datetime.now()
	text = timeget.strftime("-%H%M%S-%d%m%Y") 
	self.timestamp = str(text)

	
        self.pipeline = gst.Pipeline("TranscodingPipeline")

        self.uridecoder = gst.element_factory_make("uridecodebin", "uridecoder")
	self.uridecoder.set_property("uri", FileChosen)
	# print "File loaded" + FileChosen
	self.uridecoder.connect("pad-added", self.OnDynamicPad)
        self.pipeline.add(self.uridecoder)
	self.uridecoder.sync_state_with_parent()

	self.containermuxer = gst.element_factory_make(self.ContainerFormatPlugin, "containermuxer")
	self.pipeline.add(self.containermuxer)
	self.containermuxer.sync_state_with_parent()
	
	self.transcodefileoutput = gst.element_factory_make("filesink", "transcodefileoutput")
	self.transcodefileoutput.set_property("location", (self.VideoDirectory+self.FileNameOnly+self.timestamp+self.ContainerFormatSuffix))
	self.pipeline.add(self.transcodefileoutput)
	self.transcodefileoutput.sync_state_with_parent()

	self.containermuxer.link(self.transcodefileoutput)
	
	self.Pipeline("playing")    

    def Pipeline (self, state):
        if state == ("playing"):
	   self.pipeline.set_state(gst.STATE_PLAYING)
	elif state == ("null"):
           self.pipeline.set_state(gst.STATE_NULL)

    def OnDynamicPad(self, dbin, sink_pad):
	# print "OnDynamicPad for Audio and Video Called!"
 	c = sink_pad.get_caps().to_string()
	if c.startswith("audio/"):
	#	print "Got an audio cap"

		self.audioconverter = gst.element_factory_make("audioconvert", "audioconverter")
		self.pipeline.add(self.audioconverter)
		self.audioconverter.sync_state_with_parent()
	
		self.audioencoder = gst.element_factory_make(self.AudioEncoderPlugin, "audioencoder")
	#	print "Audioencoder used is " + self.AudioEncoderPlugin
		self.pipeline.add(self.audioencoder)
		self.audioencoder.sync_state_with_parent()

		self.gstaudioqueue = gst.element_factory_make("queue", "gstaudioqueue")
		self.pipeline.add(self.gstaudioqueue)
		self.gstaudioqueue.sync_state_with_parent()

		sink_pad.link(self.audioconverter.get_pad("sink"))
		self.audioconverter.link(self.audioencoder)
		self.audioencoder.link(self.gstaudioqueue)
		self.gstaudioqueue.link(self.containermuxer)
        
	elif c.startswith("video/"):
	#	print "Got an video cap"

		self.colorspaceconverter = gst.element_factory_make("ffmpegcolorspace", "colorspaceconverter")
		self.pipeline.add(self.colorspaceconverter)
		self.colorspaceconverter.sync_state_with_parent()
	
		self.videoencoder = gst.element_factory_make(self.VideoEncoderPlugin, "videoencoder")
	#	print "Videoencoder used is " + self.VideoEncoderPlugin
		self.pipeline.add(self.videoencoder)
		self.videoencoder.sync_state_with_parent()

		self.gstvideoqueue = gst.element_factory_make("queue", "gstvideoqueue")
		self.pipeline.add(self.gstvideoqueue)
		self.gstvideoqueue.sync_state_with_parent()
	
		sink_pad.link(self.colorspaceconverter.get_pad("sink"))
		self.colorspaceconverter.link(self.videoencoder)
		self.videoencoder.link(self.gstvideoqueue)
		self.gstvideoqueue.link(self.containermuxer)

	else:
	   raise Exception("Got a non-A/V pad!")
	   print "Got a non-A/V pad!"
