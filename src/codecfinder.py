#!/usr/bin/python

import pygst
pygst.require("0.10")
import gst
import gst.pbutils

def list_compat(a1, b1):
   for x1 in a1:
       if not x1 in b1:
           return False
   return True

#####
#This code checks for available muxers and return a unique caps string
#for each. It also creates a python dictionary mapping the caps strings 
#to concrete element names. 
#####
   
def available_muxers():
   """ return all available muxers except the broken ffmpeg ones """
   flist = gst.registry_get_default().get_feature_list(gst.ElementFactory)
   res = []
   for fact in flist:
       if list_compat(["Codec", "Muxer"], fact.get_klass().split('/')) and not fact.get_name().startswith('ffmux'): 
           res.append(fact.get_name())
   return res
   
def get_muxer_element(containercaps): 
   """
   Check all muxers for their caps and create a dictionary mapping caps 
   to element names. Then return elementname
   """
   muxers = available_muxers()
   stringcaps = []
   for x in muxers:
       factory = gst.registry_get_default().lookup_feature(str(x))
       sinkcaps = [x.get_caps() for x in factory.get_static_pad_templates() if x.direction == gst.PAD_SRC]
       for caps in sinkcaps:
           stringcaps.append(caps[0].get_name())
   # print stringcaps   
   muxerchoice = dict(zip(stringcaps, muxers))
   elementname = muxerchoice[containercaps]    
   return elementname

######
#   This class checks for available audio encoders and return a unique caps string for each. 
#   It also creates a python dictionary mapping the caps strings to concrete element 
#   names. 
##### 
def available_audio_encoders():
   """ returns all available audio encoders """
   flist = gst.registry_get_default().get_feature_list(gst.ElementFactory)
   res = []
   for fact in flist:
       if list_compat(["Codec", "Encoder", "Audio"], fact.get_klass().split('/')):
           # excluding wavpackenc as the fact that it got two SRC pads mess up the logic of this code
           if fact.get_name() != 'wavpackenc':
               res.append(fact.get_name())
           else:
               print "adding nothing"
   return res

def donemessage(done):
   print "done"

def get_audio_encoder_element(audioencodercaps):
   """
   Check all audio encoders for their caps and create a dictionary 
   mapping caps to element names. Then return elementname.
   """
   audioencoders = available_audio_encoders()
   audiocaps = []
   # blacklist all caps information we do not need to create a unique identifier
   blacklist = ['rate','channels','bitrate','block_align','mode','subbands'
               ,'allocation','framed','bitpool','blocks','width']
   for x in audioencoders:
       factory = gst.registry_get_default().lookup_feature(str(x))
       sinkcaps = [x.get_caps() for x in factory.get_static_pad_templates() if x.direction == gst.PAD_SRC]
       for caps in sinkcaps:
           result = caps[0].get_name();
           for attr in caps[0].keys():
               if attr not in blacklist:
                   result += ","+attr+"="+str(caps[0][attr])
           audiocaps.append(result)
   # print audiocaps 
   audioencoderchoice = dict(zip(audiocaps, audioencoders))
   elementname = audioencoderchoice[audioencodercaps]    
   return elementname

#######
# This class checks for available video encoders and return a unique caps
# string for each. It also creates a python dictionary mapping the caps 
# strings to concrete element names. 
#######
   
def available_video_encoders():
   """ returns all available video encoders """
   flist = gst.registry_get_default().get_feature_list(gst.ElementFactory)
   res = []
   for fact in flist:
       if list_compat(["Codec", "Encoder", "Video"], fact.get_klass().split('/')):
           if fact.get_name() != 'ffenc_libtheora':
               res.append(fact.get_name())
           elif 'theoraenc' in res:
               print "adding nothing"
           else:
               res.append(fact.get_name()) 
       elif list_compat(["Codec", "Encoder", "Image"], fact.get_klass().split('/')):
           res.append(fact.get_name())
   return res 

def get_video_encoder_element(videoencodercaps):
   """
   Check all video encoders for their caps and create a dictionary 
   mapping caps to element names. Then return elementname.
   """
   encoders = available_video_encoders()
   stringcaps = []
   # blacklist all caps information we do not need to create a unique identifier
   blacklist = ['height','width','framerate','systemstream','depth']
   for x in encoders:
       factory = gst.registry_get_default().lookup_feature(str(x))
       sinkcaps = [x.get_caps() for x in factory.get_static_pad_templates() if x.direction == gst.PAD_SRC]
       for caps in sinkcaps:
           result = caps[0].get_name();
           for attr in caps[0].keys():
               if attr not in blacklist:
                   result += ","+attr+"="+str(caps[0][attr])
           stringcaps.append(result)
   # print stringcaps 
   videoencoderchoice = dict(zip(stringcaps, encoders))
   elementname = videoencoderchoice[videoencodercaps]    
   return elementname
