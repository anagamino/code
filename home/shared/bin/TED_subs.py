#!/usr/bin/env python
# -*- coding: utf8 -*-
 
"""
    TEDSubs.py: Downloads a TED Talk' subtitles and videos by it's url
"""
 
#===============================================================================
# This Script uses a TED Talk URL to download the talk's video and 
# subtitles.
#
# Este script emplea la url de una TED Talk y descarga el video y los
# subtitulos de la misma
#===============================================================================
 
#===============================================================================
#       Copyright 2010 joe di castro <joe@joedicastro.com>
#       
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
#
#    Este programa es software libre: usted puede redistribuirlo y/o modificarlo
#    bajo los términos de la Licencia Publica General GNU publicada 
#    por la Fundación para el Software Libre, ya sea la versión 3 
#    de la Licencia, o (a su elección) cualquier versión posterior.
#
#    Este programa se distribuye con la esperanza de que sea útil, pero 
#    SIN GARANTIA ALGUNA; ni siquiera la garantía implícita 
#    MERCANTIL o de APTITUD PARA UN PROPOSITO DETERMINADO. 
#    Consulte los detalles de la Licencia Publica General GNU para obtener 
#    una información mas detallada. 
#
#    Deberla haber recibido una copia de la Licencia Publica General GNU 
#    junto a este programa. 
#    En caso contrario, consulte <http://www.gnu.org/licenses/>.
#
#===============================================================================
 
__author__ = "joe di castro - joe@joedicastro.com"
__license__ = "GNU General Public License version 3"
__date__ = "31/07/2010"
__version__ = "0.10"
 
try:
    import optparse
    import sys
    import json
    import urllib
    import re
except ImportError:
    # Checks the installation of the necessary python modules 
    # Comprueba si todos los módulos necesarios están instalados
    print ("""An error found importing one or more modules:
    \n{0}
    \nYou need to install this module\nQuitting...""").format(sys.exc_info()[1])
    sys.exit(-2)
 
def options():
    """Defines the command line arguments and options for the script
    Define los argumentos y las opciones de la linea de comandos del script"""
    usage = """usage: %prog [Options] TEDTalkURL
 
Where TEDTalkURL is the url of a TED Talk webpage
 
For example:
 
%prog -s  http://www.ted.com/talks/lang/eng/jamie_oliver.html
 
Downloads only the subs for the Jamie Oliver's TED Talk, if wants the video too
only needs to remove the "-s" option"""
    desc = "Downloads the subtitles and the video (optional) for a TED Talk."
    parser = optparse.OptionParser(usage=usage, version="%prog " + __version__,
                                   description=desc)
 
    parser.add_option("-s", "--only_subs", action='store_true', dest="no_video",
                      help="download only the subs, not the video ",
                      default=False)
 
    return parser
 
 
def get_sub(tt_id , tt_intro, lang):
    """Get TED Subtitle in JSON format & convert it to SRT Subtitle
    Obtiene el subtitulo de TED en formato JSON y lo convierte al formato SRT"""
 
    def srt_time(tst):
        """Format Time from TED Subtitles format to SRT time Format
        Convierte el formato de tiempo del subtitulo TED al formato de SRT"""
        secs, mins, hours = ((tst / 1000) % 60), (tst / 60000), (tst / 3600000)
        right_srt_time = "{0:02d}:{1:02d}:{2:02d},000".format(hours, mins, secs)
        return right_srt_time
 
    srt_content = ''
    tt_url = 'http://www.ted.com/talks'
    sub_url = '{0}/subtitles/id/{1}/lang/{2}'.format(tt_url, tt_id, lang)
    json_object = json.loads(urllib.urlopen(sub_url).read()) ## Get JSON sub
    if 'captions' in json_object:
        caption_idx = 1
        for caption in json_object['captions'] :
            start = tt_intro + caption['startTime']
            end = start + caption['duration']
            idx_line = '{0}'.format(caption_idx)
            time_line = '{0} --> {1}'.format(srt_time(start), srt_time(end))
            text_line = '{0}'.format(caption['content'].encode("utf-8"))
            srt_content += '\n'.join([idx_line, time_line, text_line, '\n'])
            caption_idx += 1
    return srt_content
 
 
def check_subs(tt_id, tt_intro, tt_video):
    """Check if the subtitles for the talk exists and try to get them. Checks it
    for english and spanish languages.
    Comprueba si los subtitulos para la charla existen e intenta obtenerlos. Lo 
    comprueba para los idiomas español e ingles"""
    ## Get the names for the subtitles (for english and spanish languages) only 
    # if they not are already downloaded
    subs = ("{0}.{1}.srt".format(tt_video[:-4], lang) for lang in
            ('eng', 'spa'))
    for sub in subs:
        subtitle = get_sub(tt_id, tt_intro, sub.split('.')[1])
        if subtitle:
            with open(sub, 'w') as srt_file:
                srt_file.write(subtitle)
            print "Subtitle {0} downloaded".format(sub)
    return
 
def get_video(vid_name):
    """Gets the TED Talk video
    Obtiene el video de la TED Talk"""
    root_url = 'http://video.ted.com/talks/podcast/'
    print "Donwloading video..."
    urllib.urlretrieve('{0}{1}'.format(root_url, vid_name),
                       '{0}'.format(vid_name))
    print "Video {0} downloaded".format(vid_name)
    return
 
def main():
    """main section"""
    # first, parse the options & arguments
    (opts, args) = options().parse_args()
 
    if not args:
        options().print_help()
    else:
        tedtalk_webpage = args[0]
        ## Reads the talk web page, to search the talk's values
        ttalk_webpage = urllib.urlopen(tedtalk_webpage).read()
        ttalk_intro = int(re.search("introDuration:(\d+),",
                                    ttalk_webpage).group(1))
        ttalk_id = int(re.search("talkID = (\d+);", ttalk_webpage).group(1))
        ttalk_vid = re.search('hs:"(?:\w+:)?talks/dynamic/(.*)-high.\w+"',
                              ttalk_webpage).group(1) + '_480.mp4'
 
        #@ Get subs (and video)
        check_subs(ttalk_id, ttalk_intro, ttalk_vid)
        if not opts.no_video:
            get_video(ttalk_vid)
 
 
if __name__ == "__main__":
    main()
