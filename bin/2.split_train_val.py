#!/usr/bin/env python
import argparse
import json
import os
import shutil
import random
import sys


class Splitter(object):
    def __init__(self, args):
        self.input_anno_dir = os.path.join(args.input_dir, 'annos')
        self.input_img_dir = os.path.join(args.input_dir, 'image')
        self.output_train_image_dir = os.path.join(args.output_dir, 'train/image')
        self.output_val_image_dir = os.path.join(args.output_dir, 'val/image')
        self.output_train_anno_dir = os.path.join(args.output_dir, 'train/annos')
        self.output_val_anno_dir = os.path.join(args.output_dir, 'val/annos')
        shutil.rmtree(self.output_train_image_dir, ignore_errors=True)
        shutil.rmtree(self.output_val_image_dir, ignore_errors=True)
        shutil.rmtree(self.output_train_anno_dir, ignore_errors=True)
        shutil.rmtree(self.output_val_anno_dir, ignore_errors=True)
        os.makedirs(self.output_train_image_dir, exist_ok=True)
        os.makedirs(self.output_val_image_dir, exist_ok=True)
        os.makedirs(self.output_train_anno_dir, exist_ok=True)
        os.makedirs(self.output_val_anno_dir, exist_ok=True)

    def get_train_val_idx(self, data_list, val_ratio=0.1):
        idx_set = set(range(len(data_list)))
        val_idx = set(random.sample(idx_set, int(len(idx_set)*val_ratio)))
        train_idx = idx_set.difference(val_idx)
        return train_idx, val_idx

    def get_anno_image_paths(self):
        anno_filenames = os.listdir(self.input_anno_dir)
        image_paths = []
        anno_paths = []
        for i, anno in enumerate(anno_filenames):
            anno_path = os.path.join(self.input_anno_dir, anno)
            image_key = os.path.splitext(anno)[0]
            image_path = os.path.join(self.input_img_dir, image_key + '.jpg')
            image_paths.append(image_path)
            anno_paths.append(anno_path)

        image_paths = sorted(image_paths)
        anno_paths = sorted(anno_paths)
        print(f'len(image_paths)={len(image_paths)}')
        print(f'len(anno_paths)={len(anno_paths)}')
        return image_paths, anno_paths

    def splitter(self, image_paths, anno_paths):
        train_idx, val_idx = self.get_train_val_idx(image_paths)
        print(f'len(train_idx)={len(train_idx)}, train_idx={train_idx}')
        print()
        print(f'len(val_idx)={len(val_idx)}, val_idx={val_idx}')
        for idx in train_idx:
            shutil.copy(image_paths[idx], self.output_train_image_dir)
            shutil.copy(anno_paths[idx], self.output_train_anno_dir)

        for idx in val_idx:
            shutil.copy(image_paths[idx], self.output_val_image_dir)
            shutil.copy(anno_paths[idx], self.output_val_anno_dir)


def parse():
    class PaserHandler(argparse.ArgumentParser):
        def error(self, message):
            sys.stderr.write('error: %s\n' % message)
            self.print_help()
            sys.exit(2)
    parser = PaserHandler()
    parser.add_argument('-i', '--input_dir', required=True, type=str,
                        help='Specifies the source path to be split into the train and val datasets.')
    parser.add_argument('-o', '--output_dir', required=True, type=str,
                        help='Specify the splitting target path with the train and val datasets.')
    parser.add_argument('-r', '--ratio', type=float, default=0.9,
                        help='Specify the proportion of the train.(0.1~0.9)')
    args = parser.parse_args()
    return args


def main():
    args = parse()
    s = Splitter(args)
    image_paths, anno_paths = s.get_anno_image_paths()
    s.splitter(image_paths, anno_paths)


if __name__ == "__main__":
    main()
