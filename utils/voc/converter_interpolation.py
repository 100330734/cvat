#!/usr/bin/env python
#
# SPDX-License-Identifier: MIT
"""
Given a CVAT XML and a directory with the image dataset, this script reads the
CVAT XML and writes the annotations in PASCAL VOC format into a given
directory.

This implementation only supports bounding boxes in CVAT annotation format, and
warns if it encounter any tracks or annotations that are not bounding boxes,
ignoring them in both cases.


Created on Tue Feb 19 15:12:58 2019

@author: jmsamblas, dbarrejon
"""

import os
import argparse
import glog as log
from lxml import etree
from pascal_voc_writer import Writer
import cv2

def parse_args():
    """Parse arguments of command line"""
    parser = argparse.ArgumentParser(
        description='Convert CVAT XML annotations to PASCAL VOC format'
    )

    parser.add_argument(
        '--cvat-xml', metavar='FILE', required=True,
        help='input file with CVAT annotation in xml format. Only the file, not full path.'
    )
    
    parser.add_argument(
        '--video', metavar='FILE', required=True,
        help='Video file for the annotations. Only the file, not full path.'
    )

    parser.add_argument(
        '--output-dir', metavar='DIRECTORY', required=True,
        help='directory for output annotations in PASCAL VOC format'
    )

    return parser.parse_args()


def process_cvat_xml(xml_file, output_dir, video):
    """
    Transforms a single XML in CVAT format to multiple PASCAL VOC format
    XMls.

    :param xml_file: CVAT format XML
    :param output_dir: directory of annotations with PASCAL VOC format
    :return:
    """
    KNOWN_TAGS = {'box', 'image', 'attribute'}
    os.makedirs(output_dir, exist_ok=True)
    cvat_xml = etree.parse(xml_file)

    basename = os.path.splitext( os.path.basename( xml_file ) )[0]
    video_name = os.path.basename(video)
    # video_name = basename + '.MP4'
    tracks = cvat_xml.findall( './/track' )
    #print( "Tracks: "

    # Build up a dictionary of each bounding box per frame

    frames = {}
    
    #%% Parse xml and gather data
    for track in tracks:
        trackid = int(track.get("id"))
        label = track.get("label")
        boxes = track.findall( './box' )
        for box in boxes:
            frameid  = int(box.get('frame'))
            outside  = int(box.get('outside'))
            occluded = int(box.get('occluded'))
            keyframe = int(box.get('keyframe'))
            xtl      = float(box.get('xtl'))
            ytl      = float(box.get('ytl'))
            xbr      = float(box.get('xbr'))
            ybr      = float(box.get('ybr'))
            
            frame = frames.get( frameid, {} )
            
            if outside == 0:
                frame[ trackid ] = { 'xtl': xtl, 'ytl': ytl, 'xbr': xbr, 'ybr': ybr, 'label': label }
                frames[ frameid ] = frame

    #%% Get rid of the frames without hitos
    for frameid in sorted(frames.keys()):

        frame = frames[frameid]
        objids = sorted(frame.keys()) # track ids
        hito_present = 0

        for objid in objids:
            obj = frame[objid]
            if 'hito_right' in obj.values() or  'hito_left' in obj.values():
                hito_present = 1
                break             
        if not hito_present :
            del frames[frameid] # Delete frame without hitos
            
            
   #%% Generate Data set Images
    video_absPath = os.path.abspath(video)
    anno_dir = os.path.join(os.path.expanduser(output_dir), basename)
    os.makedirs(anno_dir, exist_ok=True)
    
    generate_dataset(video_absPath, anno_dir, frames )

    #%% Spit out a list of each object for each frame
    
    width = int(cvat_xml.find('.//original_size/width').text)
    height  = int(cvat_xml.find('.//original_size/height').text)
    
    for frameid in sorted(frames.keys()):
        print( frameid )

        image_name = "%s_%05d.jpg" % (basename, frameid)
#        original_size = cvat_xml.findall('.//original_size')[0]
#        elem_width = original_size.getchildren()[0]
#        width = int(elem_width.text)
#        elem_height = original_size.getchildren()[1]
#        height = int(elem_height.text)

        image_path = os.path.join(anno_dir, image_name)
        if not os.path.exists(image_path):
            log.warn('{} image cannot be found. Is `{}` image directory correct?'.
                format(image_path, anno_dir))
        writer = Writer(image_path, width, height)

        # Save frame at outputdir
        
        frame = frames[frameid]

        objids = sorted(frame.keys()) # track ids

        for objid in objids:

            box = frame[objid]
            
            print( "    %d: (%f,%f) (%f,%f) '%s'" % (objid, box['xtl'],box['ytl'],box['xbr'],box['ybr'],box['label']) )

            label = box.get('label')
            xmin = float(box.get('xtl'))
            ymin = float(box.get('ytl'))
            xmax = float(box.get('xbr'))
            ymax = float(box.get('ybr'))

            writer.addObject(label, xmin, ymin, xmax, ymax)

        anno_name = os.path.basename(os.path.splitext(image_name)[0] + '.xml')
#        anno_dir = os.path.dirname(os.path.join(output_dir, image_name))
        os.makedirs(anno_dir, exist_ok=True)
        writer.save(os.path.join(anno_dir, anno_name))
        
    return frames


def generate_dataset(video_absPath, anno_dir, frames):
    """
    Generate the annotated frames data set from the annotated video.

    :param video_absPath: full path for the annotated video
    :param anno_dir: directory of annotations with PASCAL VOC format
    :frames: dictionary with the annotated frames infomrmation
    """
    basename = os.path.splitext( os.path.basename( video_absPath ) )[0]
    cap = cv2.VideoCapture(video_absPath)
    list_frameId = [*frames]
    
    ## Faster way
    while (cap.isOpened()): # open video file
    
        frameId = int(cap.get(1)) #current frame number
        ret, frame = cap.read()
        
        if frameId in frames.keys(): # check if current id = anno_frameId
            framename = "%s_%05d.jpg" % (basename, frameId)
            filename = os.path.join(anno_dir, framename)
            cv2.imwrite(filename, frame) # store annotated frame
            
            list_frameId.remove(frameId)
            if not list_frameId: # Check if list is empty
                cap.release()
                print('Dataset generated at ' + anno_dir)
                return
        
#    ## Slower way   
#    for frameid in list_frameId:
#        cap.set(1, frameid)
#        ret, frame = cap.read()
#        
#        framename = "%s_%05d.jpg" % (basename, frameid)
#        filename = os.path.join(anno_dir, framename)
#        cv2.imwrite(filename, frame) # store annotated frame
#                    
#    cap.release()
#    print('Dataset generated at ' + anno_dir)

            
def main():
    args = parse_args()
    frames = process_cvat_xml(args.cvat_xml, args.output_dir,args.video)


if __name__ == "__main__":
    main()