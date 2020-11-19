#!/usr/bin/env python
import argparse
import os
import shutil
import json
import sys


class CategoryFilter(object):
    category_map = {
        1: 'short sleeve top',
        2: 'short sleeve dress',
        3: 'shorts',
        4: 'sling',
        5: 'sling dress',
        6: 'long sleeve top',
        7: 'long sleeve dress',
        8: 'long sleeve outwear',
        9: 'skirt',
        10: 'short sleeve outwear',
        11: 'vest dress',
        12: 'trousers',
        13: 'vest',
    }

    def __init__(self, args):
        self.input_anno_dir = os.path.join(args.input_dir, 'annos')
        self.input_img_dir = os.path.join(args.input_dir, 'image')
        self.output_anno_dir = os.path.join(args.output_dir, 'annos')
        self.output_img_dir = os.path.join(args.output_dir, 'image')
        self.category = CategoryFilter.category_map.get(args.category)
        shutil.rmtree(self.output_anno_dir, ignore_errors=True)
        shutil.rmtree(self.output_img_dir, ignore_errors=True)
        os.makedirs(self.output_anno_dir, exist_ok=True)
        os.makedirs(self.output_img_dir, exist_ok=True)

    def _get_category_names(self, data):
        category_names = []
        for i in range(1, 6):
            category_name = data.get('item'+str(i), {}).get('category_name', None)
            if category_name:
                category_names.append(category_name)
        return category_names

    def get_anno_image_paths(self):
        anno_filenames = os.listdir(self.input_anno_dir)
        image_paths = []
        anno_paths = []
        for i, anno in enumerate(anno_filenames):
            anno_path = os.path.join(self.input_anno_dir, anno)
            image_key = os.path.splitext(anno)[0]
            image_path = os.path.join(self.input_img_dir, image_key + '.jpg')
            with open(anno_path) as f:
                data = json.load(f)
            category_name = set(self._get_category_names(data))
            # It is only for photos with one category type. For example, a photo with only shorts.
            if len(category_name) == 1 and category_name.pop() == self.category:
                image_paths.append(image_path)
                anno_paths.append(anno_path)

        image_paths = sorted(image_paths)
        anno_paths = sorted(anno_paths)
        print(f'len(image_paths)={len(image_paths)}')
        print(f'len(anno_paths)={len(anno_paths)}')
        return image_paths, anno_paths

    def save_filtered_category(self, image_paths, anno_paths):
        for anno in anno_paths:
            shutil.copy(anno, self.output_anno_dir)
        for img in image_paths:
            shutil.copy(img, self.output_img_dir)


def parse():
    class PaserHandler(argparse.ArgumentParser):
        def error(self, message):
            sys.stderr.write('error: %s\n' % message)
            self.print_help()
            sys.exit(2)
    parser = PaserHandler()
    parser.add_argument('-i', '--input_dir', required=True, type=str,
                        help='Specifies the source input directory to be filtered. '
                             'Specify the path to the annos, image parent directory.')
    parser.add_argument('-o', '--output_dir', required=True, type=str,
                        help='Specifies the filtering results output directory.')
    parser.add_argument('-c', '--category', required=True, type=int,
                        choices=[1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13],
                        help='Select the category to filter.(1~13) '
                             'Ex) 1 : short sleeve top '
                             '2 : short sleeve dress '
                             '3 : shorts '
                             '4 : sling '
                             '5 : sling dress '
                             '6 : long sleeve top '
                             '7 : long sleeve dress '
                             '8 : long sleeve outwear '
                             '9 : skirt '
                             '10 : short sleeve outwear '
                             '11 : vest dress '
                             '12 : trousers '
                             '13 : vest ')
    args = parser.parse_args()
    return args


def main():
    args = parse()
    cf = CategoryFilter(args)
    image_paths, anno_paths = cf.get_anno_image_paths()
    cf.save_filtered_category(image_paths, anno_paths)


if __name__ == "__main__":
    main()
