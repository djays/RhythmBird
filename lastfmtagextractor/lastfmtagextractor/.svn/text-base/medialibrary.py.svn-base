#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''
lastfmtagextractor/medialibrary.py

    
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

from lastfmwrapper import LastFM_Wrapper
from mediahelper import MediaHelper
from xml.etree.ElementTree import Element, SubElement, ElementTree
import common
import fileinput
import os
import string
import sys
import time


class MediaLibrary:
    # Media Library object:
    #
    # dict(string (lowercase artist) -> dict)
    #    string ('tags') -> list of lastfm tag pairs (name,weight)
    #    string ('albums') -> dict(string (lowercase album) -> dict)
    #        string ('tracks') -> dict(string (lowercase track) -> dict)
    #            string ('tags') -> list of lastfm tag pairs (name,weight)
    #
    # It's more than a little inelegant, but it's a quick hack. I don't fully distinguish between same-filenamed tracks or albums,
    # even when they may be different (e.g. by track number), as lastFM itself only uses simple artist/album/track filenames as keys.
    # In otherwords, the library is not intended to be a representation of file system objects so much as distinct lastFM entities. As
    # such, we don't persist other fields, like comments, genres, etc., which may differ from file to file (even with the same key metadata).
    # This probably isn't an important distinction for the vast majority of files.    
    
    mediaLibrary = {}
    
    # LastFM Tag Library object:
    # dict(string (lowercase lastfm tag) -> int (number of hits/count reported by lastFM)
    lastTagLibrary = {}

    # Local Tag Library object:
    # dict(string (lowercase local tag) -> dict)
    #    string ('disp')      -> Canonical display form for the tag
    #    string ('lastfmkeys')-> LastFM version of the tag (the original, before synonym processing)
    #    string ('localhits') -> Number of times seen in the media library (post-processing)
    #    string ('lasthits')  -> Number of times seen on lastFM (summation of the union of lastfmkey key counts)
    localTagLibrary = {}

    mediaHelper = None
    config = None
    synonyms = {}
        

    def __init__(self, config):
        self.config = config
        self.mediaHelper = MediaHelper(config)
        self.readCache()

             
    def readCache(self):
        cachefile = self.config.get('cacheFile')
        if (not os.path.exists(cachefile)):
            return
        self.fromXml(ElementTree().parse(cachefile))
    
    
    def writeCache(self):
        cachefile = self.config.get('cacheFile')
        ElementTree(self.toXml()).write(cachefile, 'UTF-8')
    
    
    def readMedia(self):
        mediadir = self.config.get('mediaDir')
        verbose = self.config.getboolean('verbose')
        skipExtensions = map(lambda x: '.'+x.lower().strip(), self.config.get('skipExtensions').split(','))
        
        common.safeStdout('Reading existing metadata from ['+mediadir+']')
        numfiles = 0
        for root, dirs, files in os.walk(mediadir):
            for filename in files:
                fname, ext = os.path.splitext(filename.lower())
                if (ext is not None and ext in skipExtensions):
                    continue                
                metadata = self.mediaHelper.extractMetadata(os.path.join(root, filename))
                if (metadata is None or len(metadata['artists']) == 0 or metadata['album'] is None or metadata['track'] is None):
                    continue
                for artist in metadata['artists']:                        
                    self.addToMediaLibrary(artist, metadata['album'], metadata['track'])
                numfiles += 1
                if (verbose):
                    common.safeStdout('\tProcessed: '+os.path.join(root, filename))
        print 'Read ['+str(numfiles)+'] media files'            
    
         
    def addToMediaLibrary(self, artist, album, track, artistTags=None, trackTags=None):
        if (common.isempty(artist)):
            raise Exception('No artist info provided')
        elif (common.isempty(track)):
            raise Exception('No track title provided')
        elif (common.isempty(album)):
            raise Exception('No album title provided')
                
        if (artist not in self.mediaLibrary):
            self.mediaLibrary[artist] = { 'albums':{}, 'tags':artistTags }
            
        if (album not in self.mediaLibrary[artist]['albums']):
            self.mediaLibrary[artist]['albums'][album] = { 'tracks':{} }
    
        if (track not in self.mediaLibrary[artist]['albums'][album]['tracks']):
            self.mediaLibrary[artist]['albums'][album]['tracks'][track] = { 'tags':trackTags }
   
              
    def printLibrary(self):
        for artist in self.mediaLibrary:
            print common.safeStdout(artist + ' ('+ ', '.join(map(lambda pair: pair[0], self.mediaLibrary[artist]['tags'] or [])) + ')')
            for album in self.mediaLibrary[artist]['albums']:
                print common.safeStdout('\t'+album)
                for track in self.mediaLibrary[artist]['albums'][album]['tracks']:
                    print common.safeStdout('\t\t'+track + ' ('+ ', '.join(map(lambda pair: pair[0], self.mediaLibrary[artist]['albums'][album]['tracks'][track]['tags'] or [])) + ')')                        
                
    
    def toXml(self):
        numartists = 0
        numalbums = 0
        numtracks = 0

        try:        
            libraryElement = Element('library')            
            artistsElement = SubElement(libraryElement,'artists')
            for artist in sorted(self.mediaLibrary):
                artistDict = self.mediaLibrary[artist]
                artistElement = SubElement(artistsElement, 'artist')
                
                SubElement(artistElement, 'name').text = artist
                      
                if (artistDict['tags'] is not None):
                    if (len(artistDict['tags']) == 0):
                        SubElement(artistElement, 'notags')
                    else:
                        for tagpair in sorted(artistDict['tags']):
                            SubElement(artistElement, 'tag', weight=str(tagpair[1])).text = tagpair[0]
                
                for album in sorted(artistDict['albums']):
                    albumDict = artistDict['albums'][album]            
                    albumElement = SubElement(artistElement, 'album')
                    
                    SubElement(albumElement, 'name').text = album
                    
                    for track in sorted(albumDict['tracks']):
                        trackDict = albumDict['tracks'][track]
                        trackElement = SubElement(albumElement, 'track')
                        
                        SubElement(trackElement, 'name').text = track
    
                        if (trackDict['tags'] is not None):
                            if (len(trackDict['tags']) == 0):
                                SubElement(trackElement, 'notags')
                            else:
                                for tagpair in sorted(trackDict['tags']):
                                    SubElement(trackElement, 'tag', weight=str(tagpair[1])).text = tagpair[0]

                        numtracks += 1
                    numalbums += 1
                numartists += 1
            print 'Serialized ['+str(numartists)+'] artists, ['+str(numalbums)+'] albums, and ['+str(numtracks)+'] tracks to XML'
            
            lastTagsElement = SubElement(libraryElement, 'lasttags')
            numtags = 0
            for lastTag in sorted(self.lastTagLibrary):
                SubElement(lastTagsElement, 'tag', hits=str(self.lastTagLibrary[lastTag] or 0)).text=lastTag
                numtags += 1
            print 'Serialized ['+str(numtags)+'] lastFM tags to XML'
    
            return libraryElement
        except Exception, err:
            raise Exception('Could not serialize the XML cache data: '+str(err)), None, sys.exc_info()[2]
    
    
    def fromXml(self, rootElement):
        numartists = 0
        numalbums = 0
        numtracks = 0
        try:
            artistsElement = rootElement.find('artists')
            for artistElement in artistsElement.findall('artist'):
                nameElement = artistElement.find('name')
                if (nameElement is None):
                    common.safeStderr('Missing name element on ['+artistElement.tag+']')
                    continue                
                artist = unicode(nameElement.text).lower()
                
                # tags = None means there is no tag info, tags = [] means we know it's an empty list
                artistTags = None
                artistTagElements = artistElement.findall('tag')
                if (artistTagElements is not None and len(artistTagElements) > 0):
                    artistTags = []
                    for artistTagElement in artistTagElements:
                        artistTags.append((unicode(artistTagElement.text), int(artistTagElement.get('weight'))))
                elif (artistElement.find('notags') is not None):
                    artistTags = []
        
                for albumElement in artistElement.findall('album'):
                    nameElement = albumElement.find('name')
                    if (nameElement is None):
                        common.safeStderr('Missing name element on ['+albumElement.tag+']')
                        continue
                    album = unicode(nameElement.text).lower()
                    
                    for trackElement in albumElement.findall('track'):
                        nameElement = trackElement.find('name')
                        if (nameElement is None):
                            common.safeStderr('Missing name element on ['+trackElement.tag+']')
                            continue
                        track = unicode(nameElement.text).lower()
                            
                        # tags = None means there is no tag info, tags = [] means we know it's an empty list
                        trackTags = None
                        trackTagElements = trackElement.findall('tag')
                        if (trackTagElements is not None and len(trackTagElements) > 0):
                            trackTags = []
                            for trackTagElement in trackTagElements:
                                trackTags.append((unicode(trackTagElement.text), int(trackTagElement.get('weight'))))
                        elif (trackElement.find('notags') is not None):
                            trackTags = []

                        self.addToMediaLibrary(artist, album, track, artistTags, trackTags)
                        
                        numtracks += 1
                    numalbums += 1
                numartists += 1
            print 'Loaded ['+str(numartists)+'] artists, ['+str(numalbums)+'] albums, and ['+str(numtracks)+'] cached tracks'
            
            lastTagsElement = rootElement.find('lasttags')
            for lastTagElement in lastTagsElement.findall('tag'):
                self.addToLastFMTagLibrary(unicode(lastTagElement.text), int(lastTagElement.get('hits')))
        except Exception, err:
            raise Exception('Could not deserialize the XML cache data, possibly corrupted: '+str(err)), None, sys.exc_info()[2]


    def fetchTags(self):
        lastfm = LastFM_Wrapper(self.config)         
        self.fetchArtistTags(lastfm)
        self.fetchTrackTags(lastfm)
        self.fetchTagStats(lastfm)        
        if (self.config.getboolean('verbose')):
            self.printDistinctLastTags()

        
    def fetchArtistTags(self, lastfm):
        verbose = self.config.getboolean('verbose')
        refetch = self.config.getboolean('refetchCachedTags')
        minWeight = self.config.getint('minArtistTagWeight')
        niceness = self.config.getint('niceness') / 1000
        maxTagsToSave = self.config.getint('getArtistTags')
        if (maxTagsToSave <= 0):
            return        
    
        print 'Fetching artist tags from LastFM'
        for artist in sorted(self.mediaLibrary):
            tagpairs = self.mediaLibrary[artist]['tags']
            if (tagpairs is not None and refetch is False):
                #if (verbose):
                #    common.safeStdout('\tSkipping already-tagged artist ['+artist+']')
                continue
            tagpairs = lastfm.fetchArtistTags(artist, maxTagsToSave, minWeight)
            if (tagpairs is not None):
                map(self.addToLastFMTagLibrary, map(lambda pair: pair[0], tagpairs))
                if (verbose):
                    common.safeStdout('\tFetched ['+artist+'] ('+', '.join(map(lambda pair: pair[0], tagpairs))+')')
            self.mediaLibrary[artist]['tags'] = tagpairs
            time.sleep(niceness)
                    
                    
    def fetchTrackTags(self, lastfm):
        verbose = self.config.getboolean('verbose')
        refetch = self.config.getboolean('refetchCachedTags')
        minWeight = self.config.getint('minTrackTagWeight')
        niceness = self.config.getint('niceness') / 1000
        maxTagsToSave = self.config.getint('getTrackTags')
        if (maxTagsToSave <= 0):
            return
        
        print 'Fetching track tags from LastFM'
        for artist in sorted(self.mediaLibrary):
            for album in sorted(self.mediaLibrary[artist]['albums']):
                for track in sorted(self.mediaLibrary[artist]['albums'][album]['tracks']):
                    tagpairs = self.mediaLibrary[artist]['albums'][album]['tracks'][track]['tags']
                    if (tagpairs is not None and refetch is False):                    
                        if (verbose):
                            common.safeStdout('\tSkipping already-tagged track ['+artist+':'+track+']')
                        continue
                    tagpairs = lastfm.fetchTrackTags(artist, track, maxTagsToSave, minWeight)
                    if (tagpairs is not None):
                        map(self.addToLastFMTagLibrary, map(lambda pair: pair[0], tagpairs))
                        if (verbose):
                            common.safeStdout('\tFetched ['+artist+':'+track+'] ('+', '.join(map(lambda pair: pair[0], tagpairs))+')')
                    self.mediaLibrary[artist]['albums'][album]['tracks'][track]['tags'] = tagpairs 
                    time.sleep(niceness)

    
    def fetchTagStats(self, lastfm):
        ''' Fetch overall/LastFM-wide tag counts. Currently only works for LastFM's 'top tracks' (they don't syndicate counts for arbitrary tags '''
        toptags = lastfm.fetchTopTagStats()
        if (toptags is None or len(toptags) == 0):
            common.safeStderr('Could not retrieve tag counts from lastFM')
            for lasttag in self.lastTagLibrary:
                self.lastTagLibrary[lasttag] = 0
            return
        #lonelytags = set()
        for lasttag in self.lastTagLibrary:
            if (lasttag in toptags):
                self.lastTagLibrary[lasttag] = toptags[lasttag]
        #    else:
        #        lonelytags.add(lasttag)        
        #for lonelytag in lonelytags:
        #    count = lastfm.fetchTagCount(lonelytag)
        #    self.lastTagLibrary[lonelytag] = count or 0
            
                        

    def addToLastFMTagLibrary(self, lasttag, hits=0):
        ''' 
        This method ensures that the fetched tags are in the lastFM tag library. We use 
        this later to handle stats. If the tag is already in the library, this does nothing.
        '''
        key = lasttag.lower()
        if (key not in self.lastTagLibrary): 
            self.lastTagLibrary[key] = hits 


    def updateTags(self):
        ''' This pushes the tags back into the underlying media files '''
        verbose             = self.config.getboolean('verbose')
        mediadir            = self.config.get('mediaDir')
        startDelim          = self.config.get('tagStartDelim')
        endDelim            = self.config.get('tagEndDelim')
        artistTagFields     = set(map(string.strip, self.config.get('artistTagFields').lower().split(',')))
        trackTagFields      = set(map(string.strip, self.config.get('trackTagFields').lower().split(',')))
        touchedFields       = artistTagFields.union(trackTagFields)
        skipExtensions      = map(lambda x: '.'+x.lower().strip(), self.config.get('skipExtensions').split(','))
        writeUntaggedArtist = (self.config.get('writeUntaggedTag').lower() == 'artist' or self.config.get('writeUntaggedTag').lower() == 'both')
        writeUntaggedTrack  = (self.config.get('writeUntaggedTag').lower() == 'track' or self.config.get('writeUntaggedTag').lower() == 'both')
        
        if (touchedFields is None or len(touchedFields) == 0):
            common.safeStderr('Perhaps you should configure a destination field...')
            return
        
        self.loadSynonyms()
        self.generateLocalTags()
        
        common.safeStdout('Updating tags in ['+mediadir+']')
        numfiles = 0
        for root, dirs, files in os.walk(mediadir):
            for filename in files:
                fname, ext = os.path.splitext(filename.lower())
                if (ext is not None and ext in skipExtensions):
                    continue

                metadata = self.mediaHelper.extractMetadata(os.path.join(root, filename))
                if (metadata is None or len(metadata['artists']) == 0 or metadata['album'] is None or metadata['track'] is None):
                    continue
                album, track = metadata['album'].lower(), metadata['track'].lower()
                
                artistTags = []
                trackTags = []
                for artist in map(string.lower, metadata['artists']):                                           
                    if (artist not in self.mediaLibrary or 
                        album not in self.mediaLibrary[artist]['albums'] or 
                        track not in self.mediaLibrary[artist]['albums'][album]['tracks']):
                        common.safeStderr('Entry not found in library: ['+artist+']['+album+']['+track+']')
                        continue
                    artistTags.extend(self.mediaLibrary[artist]['tags'] or [])
                    trackTags.extend(self.mediaLibrary[artist]['albums'][album]['tracks'][track]['tags'] or [])
                                 
                localArtistTags = self.lastTagsToLocalTags(artistTags)
                localTrackTags = self.lastTagsToLocalTags(trackTags)
                
                # Use untagged tags, if requested and appropriate
                if (len(localArtistTags) == 0 and writeUntaggedArtist):  localArtistTags = [(u'untagged artist', 0)]
                if (len(localTrackTags) == 0 and writeUntaggedTrack):    localTrackTags = [(u'untagged track', 0)]
                
                tagPayload = {}
                for touchedField in touchedFields:
                    if (touchedField in artistTagFields and touchedField in trackTagFields):
                        fieldTags = common.distinctTagSeq(localArtistTags + localTrackTags)
                    elif (touchedField in artistTagFields):
                        fieldTags = localArtistTags
                    else:
                        fieldTags = localTrackTags

                    if (fieldTags is None or len(fieldTags) == 0) : 
                        continue

                    # The following section is mostly to deal with multi-column sorting
                    
                    # Store the record weights somewhere we can look them up (the list should already be distinct)
                    recordWeights = {}
                    for tagpair in fieldTags:
                        recordWeights[tagpair[0].lower()] = tagpair[1]

                    # Pull out just the tag names as singleton tuples, we'll tack on sort weights next                                        
                    tagWeightsList = map(lambda tuple: (tuple[0],), fieldTags)
                                        
                    # Pull out the list of sort rules (e.g. record, library) and append each appropriate weight to the tuple list, in succession
                    sortRules = map(string.strip, self.config.get(touchedField + 'Sort').lower().split(','))                    
                    for sortRule in sortRules:
                        if (sortRule == 'record'):      tagWeightsList = map(lambda tagtuple: tagtuple + (recordWeights[tagtuple[0].lower()],), tagWeightsList)
                        elif (sortRule == 'library'):   tagWeightsList = map(lambda tagtuple: tagtuple + (self.getLibraryWeight(tagtuple[0].lower()),), tagWeightsList)
                        elif (sortRule == 'popularity'):tagWeightsList = map(lambda tagtuple: tagtuple + (self.getPopularityWeight(tagtuple[0].lower()),), tagWeightsList)
                    
                    common.sortWeightedTagTuples(tagWeightsList)
                    
                    tagPayload[touchedField] = self.formattedTagList(tagWeightsList, startDelim, endDelim)
                        
                if (self.mediaHelper.updateTags(os.path.join(root, filename), tagPayload)):                                                                      
                    numfiles += 1
                    if (verbose):
                        common.safeStdout('\tUpdated: '+os.path.join(root, filename))
                elif (verbose):
                    common.safeStdout('\tSkipped: '+os.path.join(root, filename)+' (nothing to update)')
        print 'Updated ['+str(numfiles)+'] media files'
        #if (verbose):
        #    self.printDistinctLocalTags()            


    def loadSynonyms(self):
        synfile = self.config.get('tagSynonymsFile')
        if (common.isempty(synfile)):
            return
        if (not os.path.exists(synfile) or not os.access(synfile, os.R_OK)):
            common.safeStderr('Synonyms file either does not exist or cannot be accessed ['+synfile+']')
        
        # Read the synonmyms file. The expected format is:
        # original token(tab)replacement token[,replacement token]...
        # e.g. 
        # rnb    rhythm and blues, r&b
        # This would replace any instance of 'rnb' seen in the LastFM tag set with both 'rhythm and blues' and 'r&b'
        # We preserve order, for the replacement values (so you can order them as you would like them to be replaced)
        for line in fileinput.input(synfile):
            # Allow inline comments
            if ('#' in line):
                line = line.split('#')[0]
            line = line.strip()
            if (common.isempty(line)):
                continue
            if (isinstance(line, str)):                
                line = unicode(line, 'latin1')
            synline = line.split('\t')
            if (len(synline) < 2):
                common.safeStderr('Invalid synonym file line: '+line)
                continue
            original = synline[0].lower()
            replacements = map(string.strip, synline[1].split(','))
            if ('-none-' in map(lambda val: val.lower(), replacements)):
                self.synonyms[original] = []
            elif (original in self.synonyms):
                self.synonyms[original] = common.distinctSeq(self.synonyms[original] + replacements)
            else:
                self.synonyms[original] = common.distinctSeq(replacements)
        #for syn in sorted(self.synonyms):
        #    common.safeStdout('Synonyms: '+ syn + ' :: '+ ', '.join(sorted(self.synonyms[syn])))
        if (self.config.getboolean('verbose')):
            print 'Loaded ['+str(len(self.synonyms.keys()))+'] tag synonyms'           
        

    def generateLocalTags(self):
        '''
        This method goes through the media library and pulls out each distinct token, storing it in
        the localTagLibrary object. At the end of processing, this object will contain counters for the
        number of times each tag is referenced in the local library and a canonical (display) form of the tag
        '''
        for artist in self.mediaLibrary:
            self.generateLocalTagsHelper(self.mediaLibrary[artist]['tags'])
            for album in self.mediaLibrary[artist]['albums']:
                for track in self.mediaLibrary[artist]['albums'][album]['tracks']:
                    self.generateLocalTagsHelper(self.mediaLibrary[artist]['albums'][album]['tracks'][track]['tags'])
                    
        # Move or merge the lastFM tag counts to the local tag object
        for localtag in self.localTagLibrary:
            lastcount = 0
            for lastkey in self.localTagLibrary[localtag]['lastfmkeys']:
                lastcount += self.lastTagLibrary[lastkey]
            self.localTagLibrary[localtag]['lasthits'] = lastcount

        # These are dummy tags which may optionally be used to indicate an absence of tags
        self.localTagLibrary['untagged artist'] = dict(disp='Untagged Artist', lastfmkey=[], localhits=0, lasthits=0 )
        self.localTagLibrary['untagged track'] = dict(disp='Untagged Track', lastfmkey=[], localhits=0, lasthits=0 )
        

    def generateLocalTagsHelper(self, tagpairs):
        ''' 
        This method operates on each individual record (either a track or an artist), performing synonym 
        expansion/contraction and finally incrementing tag counters for the distinct tags left after processing
        '''
        if (tagpairs is None or len(tagpairs) == 0): 
            return
        newtags = []
        for tagpair in tagpairs:
            synlist = self.lookupSynonyms(tagpair[0])
            if (synlist is not None):   tmplist = synlist       # an empty set is valid (means delete the tag)
            else:                       tmplist = [tagpair[0]]            
            for tmptag in tmplist:
                self.addToLocalTagLibrary(tmptag, tagpair[0])
                newtags.append((tmptag.lower(), tagpair[1]))
        newtags = common.distinctTagSeq(newtags)
        # Keep track of distinct library hits for the local tags 
        for newtag in newtags:
            self.localTagLibrary[newtag[0]]['localhits'] += 1

                     
    def addToLocalTagLibrary(self, localtag, lasttag):
        ''' 
        Ensures that the specified tag is in the local tag library, with a back reference to the original
        lastFM tag. We also seed the 'disp' value with a canonical tag representation. In general, this is the
        first case-form of the tag seen (so you don't end up with genres 'indie' and 'Indie'), but may optionally
        be forced to a cap-word form ('Punk Rock') via the config file
        '''
        localkey = localtag.lower()
        lastkey = lasttag.lower()
        if (localkey not in self.localTagLibrary):
            if (self.config.get('captagwords')):    disptag = string.capwords(localtag)
            else:                                   disptag = localtag
            self.localTagLibrary[localkey] = dict(disp=disptag, lastfmkeys=set([lastkey]), localhits=0)
        elif (lastkey not in self.localTagLibrary[localkey]['lastfmkeys']):
            self.localTagLibrary[localkey]['lastfmkeys'].add(lastkey)
        

    def lastTagsToLocalTags(self, tagpairs):
        ''' 
        This method performs synonym expansion/contraction and duplicate removal, returning a 'local tag'
        version of the lastFM tag stream. It also optionally filters out low-count tags.
        '''
        if (tagpairs is None or len(tagpairs) == 0) : 
            return []
        
        newtags = []
        for tagpair in tagpairs:
            synlist = self.lookupSynonyms(tagpair[0])
            if (synlist is not None):   tmplist = synlist       # an empty list is valid (means delete the tag)
            else:                       tmplist = [tagpair[0]]            
            for tmptag in tmplist:
                key = tmptag.lower()
                if (self.localTagLibrary[key]['localhits'] < self.config.getint('minLibraryCount')): continue
                if (self.localTagLibrary[key]['lasthits'] < self.config.getint('minlastFMCount')): continue
                newtags.append((tmptag.lower(), tagpair[1]))
        return common.distinctTagSeq(newtags)
           

    def lookupSynonyms(self, tag):
        ''' Returns a set of synonyms for the given tag, or None if none exist '''
        if (common.isempty(tag)):
            return None
        key = tag.lower()
        if (key in self.synonyms):
            return self.synonyms[key]
        return None

        
    def printDistinctLocalTags(self):
        if (len(self.localTagLibrary) == 0):
            return
        disptags = []
        for localtag in self.localTagLibrary:
            disptags.append((self.localTagLibrary[localtag]['disp'], self.localTagLibrary[localtag]['localhits']))
        common.safeStdout('\nDistinct Update-stream Tags (most to least frequent, in your library): \n\t'+'\n\t'.join(map(lambda pair: pair[0]+' ('+str(pair[1])+')', common.sortWeightedTagTuples(disptags))))


    def printDistinctLastTags(self):
        if (len(self.lastTagLibrary) == 0):
            return
        disptags = []
        for lasttag in self.lastTagLibrary:
            disptags.append((lasttag, self.lastTagLibrary[lasttag]))
        common.safeStdout('\nDistinct In-library LastFM Tags (most to least popular, on LastFM): \n\t'+'\n\t'.join(map(lambda pair: pair[0]+' ('+str(pair[1])+')', common.sortWeightedTagTuples(disptags))))


    def formattedTagList(self, tagpairs, startDelim, endDelim):
        ''' 
        This method breaks apart the tag pairs, returning just a list of the canonical-form 
        tags (optionally formatted with starting/ending delimiters) 
        '''
        return map(lambda pair: startDelim+ self.localTagLibrary[pair[0]]['disp'] +endDelim, tagpairs)

    
    def getLibraryWeight(self, tag):
        ''' Returns the library weight for the given tag, or 0 if the tag is empty or not present '''
        if (common.isempty(tag)):
            return 0
        key = tag.lower()
        if (self.localTagLibrary[key] is not None): 
            return self.localTagLibrary[key]['localhits']
        return 0

        
    def getPopularityWeight(self, tag):
        ''' Returns the popularity weight for the given tag, or 0 if the tag is empty or not present '''
        if (common.isempty(tag)):
            return 0
        key = tag.lower()
        if (self.localTagLibrary[key] is not None): 
            return self.localTagLibrary[key]['lasthits']
        return 0
