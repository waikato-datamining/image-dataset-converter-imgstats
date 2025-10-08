import argparse
import csv
import json
import sys
from typing import List

import cv2
import numpy as np
from wai.logging import LOGGING_WARNING

from idc.api import ImageClassificationData, ObjectDetectionData, ImageSegmentationData, REQUIRED_FORMAT_BINARY
from idc.writer import ImageAndAnnotationWriter
from seppl.placeholders import PlaceholderSupporter, placeholder_list, expand_placeholders

OUTPUT_FORMAT_CSV = "csv"
OUTPUT_FORMAT_JSON = "json"
OUTPUT_FORMATS = [
    OUTPUT_FORMAT_CSV,
    OUTPUT_FORMAT_JSON,
]


class ContourAreasWriter(ImageAndAnnotationWriter, PlaceholderSupporter):
    """
    Records the areas of contours of objects.
    """

    def __init__(self, min_area: float = None, max_area: float = None, invert: bool = False,
                 incorrect_format_action: str = None,
                 output_file: str = None, output_format: str = OUTPUT_FORMAT_CSV,
                 logger_name: str = None, logging_level: str = LOGGING_WARNING):
        """
        Initializes the reader.

        :param min_area: the minimum area for the contours
        :type min_area: float
        :param max_area: the maximum area for the contours
        :type max_area: float
        :param invert: whether to invert the binary image
        :type invert: bool
        :param output_file: the output file to save the contour area information to
        :type output_file: str
        :param output_format: the format for the output file
        :type output_format: str
        :param logger_name: the name to use for the logger
        :type logger_name: str
        :param logging_level: the logging level to use
        :type logging_level: str
        """
        super().__init__(incorrect_format_action=incorrect_format_action, logger_name=logger_name, logging_level=logging_level)
        self.min_area = min_area
        self.max_area = max_area
        self.invert = invert
        self.output_file = output_file
        self.output_format = output_format
        self._areas = None
        self._image_name = None

    def name(self) -> str:
        """
        Returns the name of the handler, used as sub-command.

        :return: the name
        :rtype: str
        """
        return "contour-areas"

    def description(self) -> str:
        """
        Returns a description of the writer.

        :return: the description
        :rtype: str
        """
        return "Records the areas of contours of objects."

    def _create_argparser(self) -> argparse.ArgumentParser:
        """
        Creates an argument parser. Derived classes need to fill in the options.

        :return: the parser
        :rtype: argparse.ArgumentParser
        """
        parser = super()._create_argparser()
        parser.add_argument("-m", "--min_area", type=float, help="The minimum area for the contours in order to record them.", default=None, required=False)
        parser.add_argument("-M", "--max_area", type=float, help="The maximum area for the contours in order to record them.", default=None, required=False)
        parser.add_argument("-i", "--invert", action="store_true", help="Whether to invert the binary image, i.e., looking for black specks rather than white ones.")
        parser.add_argument("-o", "--output_file", type=str, help="The file to write the statistics to; uses stdout if omitted. " + placeholder_list(obj=self), required=False, default=None)
        parser.add_argument("-f", "--output_format", type=str, help="The format to use for the output, available formats: %s" % ", ".join(OUTPUT_FORMATS), required=False, default=OUTPUT_FORMAT_CSV)
        return parser

    def _apply_args(self, ns: argparse.Namespace):
        """
        Initializes the object with the arguments of the parsed namespace.

        :param ns: the parsed arguments
        :type ns: argparse.Namespace
        """
        super()._apply_args(ns)
        self.min_area = ns.min_area
        self.max_area = ns.max_area
        self.invert = ns.invert
        self.output_file = ns.output_file
        self.output_format = ns.output_format

    def accepts(self) -> List:
        """
        Returns the list of classes that are accepted.

        :return: the list of classes
        :rtype: list
        """
        return [ImageClassificationData, ObjectDetectionData, ImageSegmentationData]

    def initialize(self):
        """
        Initializes the processing, e.g., for opening files or databases.
        """
        super().initialize()
        if self.invert is None:
            self.invert = False
        if self.output_format is None:
            self.output_format = OUTPUT_FORMAT_CSV
        self._areas = dict()

    def output_csv(self, use_stdout: bool):
        """
        Outputs the pixel counts in CSV format.

        :param use_stdout: whether to use stdout or the file
        :type use_stdout: bool
        """
        if use_stdout:
            writer = csv.writer(sys.stdout)
            fp = None
        else:
            fp = open(expand_placeholders(self.output_file), "w")
            writer = csv.writer(fp)

        # header
        row = ["image", "source", "x", "y", "width", "height", "area"]
        writer.writerow(row)

        # data
        for image in self._areas:
            for source in self._areas[image]:
                for data in self._areas[image][source]:
                    row = [image, source, data["x"], data["y"], data["width"], data["height"], data["area"]]
                    writer.writerow(row)

        if fp is not None:
            fp.close()

    def output_json(self, use_stdout: bool):
        """
        Outputs the pixel counts in json format.

        :param use_stdout: whether to use stdout or the file
        :type use_stdout: bool
        """
        if use_stdout:
            print(json.dumps(self._areas, indent=2))
        else:
            with open(expand_placeholders(self.output_file), "w") as fp:
                json.dump(self._areas, fp, indent=2)

    def output_areas(self):
        """
        Outputs the distribution.
        """
        use_stdout = (self.output_file is None) or (len(self.output_file) == 0)

        if self.output_format == OUTPUT_FORMAT_CSV:
            self.output_csv(use_stdout)
        elif self.output_format == OUTPUT_FORMAT_JSON:
            self.output_json(use_stdout)
        else:
            raise Exception("Unhandled output format: %s" % self.output_format)

    def _required_format(self) -> str:
        """
        Returns what input format is required for applying the filter.

        :return: the type of image
        :rtype: str
        """
        return REQUIRED_FORMAT_BINARY

    def _pre_apply_writer(self, item):
        """
        Hook method that gets executed before the writer is being applied the first time.

        :param item: the current image data being processed
        """
        self._image_name = item.image_name

    def _apply_writer(self, source: str, array: np.ndarray):
        """
        Applies the writer to the image and returns the numpy array.

        :param source: whether image or a layer
        :type source: str
        :param array: the image to apply the writer to
        :type array: np.ndarray
        """
        current = array
        if self.invert:
            current ^= 255  # take from here: https://stackoverflow.com/a/15901351/4698227
        num_labels, labels, stats, centroids = cv2.connectedComponentsWithStats(current, connectivity=8)
        for i in range(1, num_labels):  # skip background (i=0)
            area = stats[i, cv2.CC_STAT_AREA]
            if (self.min_area is not None) and (area < self.min_area):
                continue
            if (self.max_area is not None) and (area > self.max_area):
                continue
            x, y, w, h, _ = stats[i]
            if self._image_name not in self._areas:
                self._areas[self._image_name] = dict()
            if source not in self._areas[self._image_name]:
                self._areas[self._image_name][source] = []
            self._areas[self._image_name][source].append({"area": float(area), "x": int(x), "y": int(y), "width": int(w), "height": int(h)})

    def finalize(self):
        """
        Finishes the processing, e.g., for closing files or databases.
        """
        super().finalize()
        self.output_areas()
