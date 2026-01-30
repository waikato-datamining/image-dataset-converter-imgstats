import argparse
import csv
import json
import sys
from typing import List

import numpy as np
from wai.logging import LOGGING_WARNING

from idc.api import ImageSegmentationData
from kasperl.api import make_list, StreamWriter
from seppl.placeholders import PlaceholderSupporter, placeholder_list

OUTPUT_FORMAT_TEXT = "text"
OUTPUT_FORMAT_CSV = "csv"
OUTPUT_FORMAT_JSON = "json"
OUTPUT_FORMATS = [
    OUTPUT_FORMAT_TEXT,
    OUTPUT_FORMAT_CSV,
    OUTPUT_FORMAT_JSON,
]


class PixelCountWriter(StreamWriter, PlaceholderSupporter):
    """
    Counts the pixels per label per image.
    """

    def __init__(self, output_file: str = None, output_format: str = OUTPUT_FORMAT_TEXT,
                 labels: List[str] = None, per_image: bool = None, suppress_path: bool = None,
                 logger_name: str = None, logging_level: str = LOGGING_WARNING):
        """
        Initializes the reader.

        :param output_file: the output file to save the label distribution to
        :type output_file: str
        :param output_format: the format for the output file
        :type output_format: str
        :param labels: the labels to record
        :type labels: list
        :param per_image: whether to output the statistics per image rather than for the complete run
        :type per_image: bool
        :param suppress_path: whether to suppress the path
        :type suppress_path: bool
        :param logger_name: the name to use for the logger
        :type logger_name: str
        :param logging_level: the logging level to use
        :type logging_level: str
        """
        super().__init__(logger_name=logger_name, logging_level=logging_level)
        self.output_file = output_file
        self.output_format = output_format
        self.labels = labels
        self.per_image = per_image
        self.suppress_path = suppress_path
        self._counts = None

    def name(self) -> str:
        """
        Returns the name of the handler, used as sub-command.

        :return: the name
        :rtype: str
        """
        return "pixel-count"

    def description(self) -> str:
        """
        Returns a description of the writer.

        :return: the description
        :rtype: str
        """
        return "Counts the pixels per label per image."

    def _create_argparser(self) -> argparse.ArgumentParser:
        """
        Creates an argument parser. Derived classes need to fill in the options.

        :return: the parser
        :rtype: argparse.ArgumentParser
        """
        parser = super()._create_argparser()
        parser.add_argument("-o", "--output_file", type=str, help="The file to write the statistics to; uses stdout if omitted. " + placeholder_list(obj=self), required=False, default=None)
        parser.add_argument("-f", "--output_format", type=str, help="The format to use for the output, available formats: %s" % ", ".join(OUTPUT_FORMATS), required=False, default=OUTPUT_FORMAT_TEXT)
        parser.add_argument("--labels", type=str, help="The labels to calculate the pixel count for.", required=True, default=None, nargs="+")
        parser.add_argument("--per_image", action="store_true", help="Whether to output the statistics per image rather than for the complete run.")
        parser.add_argument("--suppress_path", action="store_true", help="Whether to suppress the path in the output.")
        return parser

    def _apply_args(self, ns: argparse.Namespace):
        """
        Initializes the object with the arguments of the parsed namespace.

        :param ns: the parsed arguments
        :type ns: argparse.Namespace
        """
        super()._apply_args(ns)
        self.output_file = ns.output_file
        self.output_format = ns.output_format
        self.labels = ns.labels
        self.per_image = ns.per_image
        self.suppress_path = ns.suppress_path

    def accepts(self) -> List:
        """
        Returns the list of classes that are accepted.

        :return: the list of classes
        :rtype: list
        """
        return [ImageSegmentationData]

    def initialize(self):
        """
        Initializes the processing, e.g., for opening files or databases.
        """
        super().initialize()
        if self.output_format is None:
            self.output_format = OUTPUT_FORMAT_TEXT
        if self.labels is None:
            raise Exception("No labels specified!")
        if self.per_image is None:
            self.per_image = False
        if self.suppress_path is None:
            self.suppress_path = False
        self._counts = []

    def output_text(self, use_stdout: bool):
        """
        Outputs the pixel counts in simple textual format.

        :param use_stdout: whether to use stdout or the file
        :type use_stdout: bool
        """
        if self.suppress_path:
            indent = ""
        else:
            indent = "  "
        if use_stdout:
            for count in self._counts:
                if not self.suppress_path:
                    print("%s" % count["path"])
                print("%sname: %s" % (indent, count["name"]))
                print("%swidth: %s" % (indent, count["width"]))
                print("%sheight: %s" % (indent, count["height"]))
                print("%slabels:" % indent)
                for label in self.labels:
                    if label in count["labels"]:
                        print("%s  %s: %d (%f%%)" % (indent, label, count["labels"][label]["count"], count["labels"][label]["percentage"]))
                print()
        else:
            path = self.session.expand_placeholders(self.output_file)
            self.logger().info("Writing pixel count to: %s" % path)
            with open(path, "w") as fp:
                for count in self._counts:
                    if not self.suppress_path:
                        fp.write("%s\n" % count["path"])
                    fp.write("%sname: %s\n" % (indent, count["name"]))
                    fp.write("%swidth: %s\n" % (indent, count["width"]))
                    fp.write("%sheight: %s\n" % (indent, count["height"]))
                    fp.write("%slabels:\n" % indent)
                    for label in self.labels:
                        if label in count["labels"]:
                            fp.write("%s  %s: %d (%f%%)\n" % (indent, label, count["labels"][label]["count"], count["labels"][label]["percentage"]))
                    fp.write("\n")

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
            path = self.session.expand_placeholders(self.output_file)
            self.logger().info("Writing pixel count to: %s" % path)
            fp = open(path, "w")
            writer = csv.writer(fp)

        # header
        row = []
        if not self.suppress_path:
            row.append("path")
        row.extend(["name", "width", "height"])
        for label in self.labels:
            row.append("%s - count" % label)
            row.append("%s - %%" % label)
        writer.writerow(row)

        # data
        for count in self._counts:
            row = []
            if not self.suppress_path:
                row.append(count["path"])
            row.extend([count["name"], count["width"], count["height"]])
            for label in self.labels:
                if label in count["labels"]:
                    row.append(count["labels"][label]["count"])
                    row.append(count["labels"][label]["percentage"])
                else:
                    row.append("")
                    row.append("")
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
            print(json.dumps(self._counts, indent=2))
        else:
            path = self.session.expand_placeholders(self.output_file)
            self.logger().info("Writing pixel count to: %s" % path)
            with open(path, "w") as fp:
                json.dump(self._counts, fp, indent=2)

    def output_label_distribution(self):
        """
        Outputs the distribution.
        """
        use_stdout = (self.output_file is None) or (len(self.output_file) == 0)

        if self.output_format == OUTPUT_FORMAT_TEXT:
            self.output_text(use_stdout)
        elif self.output_format == OUTPUT_FORMAT_CSV:
            self.output_csv(use_stdout)
        elif self.output_format == OUTPUT_FORMAT_JSON:
            self.output_json(use_stdout)
        else:
            raise Exception("Unhandled output format: %s" % self.output_format)

    def write_stream(self, data):
        """
        Saves the data one by one.

        :param data: the data to write (single record or iterable of records)
        """
        for item in make_list(data):
            stats = {
                "name": item.image_name,
                "width": item.image_width,
                "height": item.image_height,
                "labels": dict()
            }
            if not self.suppress_path:
                stats["path"] = item.source
            for label in self.labels:
                total = item.image_width*item.image_height
                if label in item.annotation.layers:
                    count = np.count_nonzero(item.annotation.layers[label])
                    stats["labels"][label] = {
                        "count": count,
                        "percentage": count / total * 100.0
                    }
                else:
                    stats["labels"][label] = {
                        "count": 0,
                        "percentage": 0.0
                    }
            self._counts.append(stats)
            if self.per_image:
                self.output_label_distribution()
                self._counts = []

    def finalize(self):
        """
        Finishes the processing, e.g., for closing files or databases.
        """
        super().finalize()
        if not self.per_image:
            self.output_label_distribution()
