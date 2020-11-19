#!/usr/bin/env python
import argparse
import os
import shutil
import json
import sys
import skimage
from skimage import io


def copytree(src, dst, symlinks=False, ignore=None):
    for item in os.listdir(src):
        s = os.path.join(src, item)
        d = os.path.join(dst, item)
        if os.path.isdir(s):
            shutil.copytree(s, d, symlinks, ignore)
        else:
            shutil.copy2(s, d)


class ViaToCoco(object):
    def __init__(self, args):
        self.input_image_dir = os.path.join(args.input_dir, 'image')
        self.input_anno_dir = os.path.join(args.input_dir, 'annos')
        self.output_dir = os.path.split(self.input_image_dir)[0]
        self.coordinate_type = args.coordinate_type
        self.via_anno_path = os.path.join(self.output_dir, "via_region_data.json")

    def _get_points_x(self, location):
        return [location[x*3] for x in range(len(location)//3)]

    def _get_points_y(self, location):
        return [location[1+x*3] for x in range(len(location)//3)]

    def to_via_anno(self):
        anno_paths = sorted([os.path.join(self.input_anno_dir, file) for file in os.listdir(self.input_anno_dir)])
        image_paths = sorted([os.path.join(self.input_image_dir, file) for file in os.listdir(self.input_image_dir)])
        anno_paths = [anno for anno in anno_paths if os.path.splitext(anno)[1] == '.json']
        image_paths = [img for img in image_paths if os.path.splitext(img)[1] == '.jpg']
        print(f'len(anno_paths)={len(anno_paths)}')
        print(f'len(image_paths)={len(image_paths)}')

        via_fmt = {}
        for anno_path, image_path in zip(anno_paths, image_paths):
            with open(anno_path) as f:
                anno_json = json.load(f)
            height, width = io.imread(image_path).shape[:2]
            image_filename = os.path.split(image_path)[1]
            via_element_fmt = {
                "fileref": "",
                "size": height * width,
                "filename": image_filename,
                "base64_img_data": "",
                "file_attributes": {},
                "regions": {
                }
            }
            for i in range(0,5):
                via_element_region_fmt = {
                    "shape_attributes": {
                        "name": "polygon",
                        "all_points_x": None,
                        "all_points_y": None
                    },
                    "region_attributes": {}
                }

                location = anno_json.get('item'+str(i+1), {}).get(self.coordinate_type, None)
                if location:
                    if self.coordinate_type == 'segmentation':
                        location = location[0]
                    via_element_region_fmt["shape_attributes"]["all_points_x"] = self._get_points_x(location)
                    via_element_region_fmt["shape_attributes"]["all_points_y"] = self._get_points_y(location)
                    via_element_fmt["regions"][str(i)]=via_element_region_fmt
            via_fmt[image_filename] = via_element_fmt

        with open(self.via_anno_path, 'w') as f:
            json.dump(via_fmt, f)
        print(f'Check the via annotation file({self.via_anno_path})')
        copytree(self.input_image_dir, self.output_dir)


def parse():
    class PaserHandler(argparse.ArgumentParser):
        def error(self, message):
            sys.stderr.write('error: %s\n' % message)
            self.print_help()
            sys.exit(2)
    parser = PaserHandler()
    parser.add_argument('-i', '--input_dir', required=True, type=str,
                        help='Specifies the directory '
                             'in which to convert via annotation format to coco annotation format.')
    parser.add_argument('-c', '--coordinate_type', type=str, default='landmarks',
                        choices=['landmarks', 'segmentation'],
                        help='Select whether to use landmarks coordinates or segmentation coordinates.'
                             '(landmarks, segmentation)')
    args = parser.parse_args()
    return args


def main():
    args = parse()
    vtc = ViaToCoco(args)
    vtc.to_via_anno()


if __name__ == "__main__":
    main()
