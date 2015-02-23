#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''
lastfmtagextractor/mediahelper.py
    
    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.

    @author: Aaron McKee (ucbmckee)
    v0.5 : Dec. 2009
'''

from mutagen.flac import FLAC
from mutagen.id3 import ID3, TIT1, COMM, TCON, TPE1, TPE2, TIT2, TALB
from mutagen.mp4 import MP4
from mutagen.oggvorbis import OggVorbis
import common
import mutagen
import os
import string

class MediaHelper:
    config = None
    tagSep = None
    maxTags = None
    overwriteFields = None
    forceOverwriteFields = None
    id3v1Handling = None
    useBothArtistFields = False
    artistFieldPref = []
    
    formatFieldMap = dict(
          id3 = dict(genre='TCON', grouping='TIT1', comment="COMM::'eng'", artist='TPE1', albumartist='TPE2', album='TALB', track='TIT2'),
          mp4 = dict(genre='\xa9gen', grouping='\xa9grp', comment='\xa9cmt', artist='\xa9ART', albumartist='aART', album='\xa9alb', track='\xa9nam'),
          oggvorbis = dict(genre='genre', grouping='grouping', comment='comment', artist='artist', albumartist='album artist', album='album', track='title'),
          flac = dict(genre='genre', grouping='grouping', comment='comment', artist='artist', albumartist='album artist', album='album', track='title')
    )
    
    id3FuncMap = dict(
        genre=lambda val: TCON(encoding=3, text=val),
        grouping=lambda val: TIT1(encoding=3, text=val),
        comment=lambda val: COMM(encoding=3, lang='eng', desc='', text=val),
        artist=lambda val: TPE1(encoding=3, text=val),
        albumartist=lambda val: TPE2(encoding=3, text=val),
        album=lambda val: TALB(encoding=3, text=val),
        track=lambda val: TIT2(encoding=3, text=val)
    )
    
    meaninglessArtists = frozenset(['various artists', 'soundtrack', 'soundtracks', 'original soundtrack', 'ost', 'compilation'])

    def __init__(self, config):
        self.config = config
        self.tagSep = self.config.get('tagSep')
        if (len(self.tagSep.strip()) > 0):
            self.tagSep += ' '
        self.maxTags = dict(genre = self.config.getint('genreMaxTags'),
                            grouping = self.config.getint('groupingMaxTags'),
                            comment = self.config.getint('commentMaxTags'))
        self.overwriteFields = set(map(string.strip, self.config.get('overwriteFields').lower().split(',')))
        self.forceOverwriteFields = set(map(string.strip, self.config.get('forceOverwriteFields').lower().split(',')))        
        self.id3v1Handling = self.config.getint('id3v1Handling')
        
        self.artistFieldPref = ['albumartist', 'artist']
        if (self.config.get('artistField').lower() == 'both'):      self.useBothArtistFields = True
        elif (self.config.get('artistField').lower() == 'artist'):  self.artistFieldPref.reverse()
        
        
    def getMediawrapper(self, filename):
        root,ext = os.path.splitext(filename.lower())
        if (ext == '.mp3'):     mediawrapper = ID3(filename)
        elif (ext == '.m4a'):   mediawrapper = MP4(filename)
        elif (ext == '.ogg'):   mediawrapper = OggVorbis(filename)
        elif (ext == '.flac'):  mediawrapper = FLAC(filename)
        else:                   mediawrapper = mutagen.File(filename)
        return mediawrapper
        
    
    def extractMetadata(self, filename):
        try:
            mediawrapper = self.getMediawrapper(filename)

            if (isinstance(mediawrapper, ID3)):         return self.extractMetadataHelper(mediawrapper, self.formatFieldMap['id3'], filename)
            elif (isinstance(mediawrapper, MP4)):       return self.extractMetadataHelper(mediawrapper, self.formatFieldMap['mp4'], filename)
            elif (isinstance(mediawrapper, OggVorbis)): return self.extractMetadataHelper(mediawrapper, self.formatFieldMap['oggvorbis'], filename)
            elif (isinstance(mediawrapper, FLAC)):      return self.extractMetadataHelper(mediawrapper, self.formatFieldMap['flac'], filename)
            else:
                if (self.config.getboolean('verbose')):                                       
                    common.safeStdout('\tSkipping unknown/incompatible media file type ['+filename+']')
        except Exception, err:
            common.safeStderr('Error seen during media reading: '+str(err))            
        return None
            

    def extractMetadataHelper(self, mediawrapper, fieldMap, filename):
        ''' Retrieves artist, album, and track data, forcing it to unicode '''
        artists = []
        for artistField in self.artistFieldPref:
            if (fieldMap[artistField] in mediawrapper):
                tmpartist = mediawrapper[fieldMap[artistField]][0]
                if (not common.isempty(tmpartist)):
                    artists.append(unicode(tmpartist).lower())
                if (self.useBothArtistFields):
                    continue
                break
        artists = set(artists).difference(self.meaninglessArtists)
        if (len(artists) == 0): 
            common.safeStderr('No artist info found for ['+filename+']')
            return None
        
        # album     
        album = u'-unknown-'
        if (fieldMap['album'] in mediawrapper):
            tmpalbum = mediawrapper[fieldMap['album']][0]  
            if (not common.isempty(tmpalbum)):
                album = unicode(tmpalbum).lower()
    
        # track
        track = None
        if (fieldMap['track'] in mediawrapper):
            tmptrack = mediawrapper[fieldMap['track']][0] 
            if (not common.isempty(tmptrack)):
                track = unicode(tmptrack).lower()
        if (track is None):
            common.safeStderr('No track title found for ['+filename+']')
            return None
        return {'artists':artists, 'album':album, 'track':track}
            
    
    def updateTags(self, filename, tagPayload):
        try:
            mediawrapper = self.getMediawrapper(filename)

            
            for bucket in tagPayload:
                tagPayload[bucket] = self.tagSep.join(tagPayload[bucket][0:self.maxTags[bucket]])                 
            
            if (isinstance(mediawrapper, ID3)):         return self.updateTagsHelperID3(mediawrapper, tagPayload, self.formatFieldMap['id3'])           
            elif (isinstance(mediawrapper, MP4)):       return self.updateTagsHelper(mediawrapper, tagPayload, self.formatFieldMap['mp4'])
            elif (isinstance(mediawrapper, OggVorbis)): return self.updateTagsHelper(mediawrapper, tagPayload, self.formatFieldMap['oggvorbis'])
            elif (isinstance(mediawrapper, FLAC)):      return self.updateTagsHelper(mediawrapper, tagPayload, self.formatFieldMap['flac'])
            else:                                       common.safeStdout('Skipping unknown/incompatible media file type ['+filename+']')
        except Exception, err:
            common.safeStderr('Error seen during update processing: '+str(err))                        
        return False

    
    def updateTagsHelper(self, mediawrapper, tagPayload, fieldMap):
        ''' This version saves the tag data in Unicode encoding '''
        retVal = False
        for bucket in tagPayload:
            if (bucket not in fieldMap): raise Exception('Unknown field type requested ['+bucket+']')
            curField = fieldMap[bucket]            
            # If we're not required to verwrite, check if we actually need to and should
            if (bucket not in self.forceOverwriteFields):
                # Is the payload empty? Don't update.
                if (len(tagPayload[bucket]) == 0):
                    continue
                # Is there an existing value? Don't update if this isn't an overwritable field or if the current value is the same as the update value
                elif (curField in mediawrapper and not common.isempty(mediawrapper[curField][0])):
                    if (bucket not in self.overwriteFields or unicode(mediawrapper[curField][0]) == unicode(tagPayload[bucket])):
                        continue
            mediawrapper[curField] = unicode(tagPayload[bucket])
            retVal = True
        if (retVal == True):
            mediawrapper.save()
        return retVal

        
    def updateTagsHelperID3(self, mediawrapper, tagPayload, fieldMap):
        ''' 
        ID3 requires uniquely encoded values, so this custom method is necessary to properly save the updated tags. 
        If the comments field is used, values will be saved with an empty description and lang=eng.  
        '''
        retVal = False
        for bucket in tagPayload:
            if (bucket not in fieldMap): raise Exception('Unknown field type requested ['+bucket+']')
            curField = fieldMap[bucket]            
            # If we're not required to verwrite, check if we actually need to and should
            if (bucket not in self.forceOverwriteFields):
                # Is the payload empty? Don't update.
                if (len(tagPayload[bucket]) == 0):
                    continue
                # Is there an existing value? Don't update if this isn't an overwritable field or if the current value is the same as the update value
                elif (curField in mediawrapper and not common.isempty(mediawrapper[curField][0])):
                    if (bucket not in self.overwriteFields or unicode(mediawrapper[curField][0]) == unicode(tagPayload[bucket])):
                        continue
            mediawrapper[curField] = self.id3FuncMap[bucket](tagPayload[bucket])
            retVal = True
        if (retVal == True):
            # There's an odd bug somewhere in the interaction between some set of Mutagen, iTunes, and/or WMP that causes
            # duplicate ID3v2 headers. This tends to break playback at least in iTunes. The following pre-save block makes a
            # copy of whatever the 'current' header is, deletes 'all' v2 headers, and then re-adds the current header frames. 
            # We seem to end up with some unnecessary blank padding between the frames and content, though. 
            curFrames = {}
            for key in mediawrapper.keys():
                curFrames[key] = mediawrapper[key]
            mediawrapper.delete(delete_v2=True)
            for key in curFrames:
                mediawrapper[key] = curFrames[key]
            mediawrapper.save(v1=self.id3v1Handling)
        return retVal
